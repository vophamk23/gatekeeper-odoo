# -*- coding: utf-8 -*-
# Mục đích: Các công việc định kỳ (cron) của module Gate Keeper.
#          Xử lý đồng bộ trạng thái phần cứng (phát hiện offline),
#          đồng bộ hồ sơ nhân viên từ HR, leo thang cảnh báo và kiểm tra overtime.

# pyrefly: ignore [missing-import]
from odoo import api, fields, models, _
from datetime import timedelta

import logging

_logger = logging.getLogger(__name__)

# Số phút không nhận heartbeat trước khi đánh dấu offline
WAITING_TIME = 5

# Các mức leo thang priority theo thứ tự
PRIORITY_ESCALATION = ["low", "medium", "high", "critical"]

# Thời gian (phút) tối thiểu giữa các lần leo thang cảnh báo
ESCALATION_THRESHOLD_MINUTES = 15

# Thời gian (giờ) tối đa cho phép ở trong khu vực trước khi bị overtime
OVERTIME_THRESHOLD_HOURS = 9


class T4GateKeeperScheduler(models.Model):
    _name = "t4.gate_keeper.scheduler"
    _description = "Gate Keeper Scheduler"

    @api.model
    def cron_update_hardware_status(self):
        """Đánh dấu controller và device là offline khi heartbeat/last_seen vượt WAITING_TIME phút."""
        timeout = fields.Datetime.now() - timedelta(minutes=WAITING_TIME)

        controllers = self.env["t4.gate_keeper.controller"]

        # [Controller Model] Tìm các Controller có heartbeat quá hạn hoặc chưa kết nối lần nào
        offline_controllers = controllers.search(
            [
                ("status", "!=", "offline"),
                "|",
                ("last_heartbeat_at", "=", False),
                ("last_heartbeat_at", "<", timeout),
            ]
        )
        if offline_controllers:
            # Ghi trạng thái "offline" cho các Controller (Bộ điều khiển vật lý)
            offline_controllers.write({"status": "offline"})

        devices = self.env["t4.gate_keeper.device"]

        # [Device Model] 1. Tìm các Thiết bị con có Controller cha đang offline
        controller_offline_devices = devices.search(
            [
                ("controller_id.status", "!=", "online"),
                ("status", "!=", "controller_offline"),
            ]
        )
        if controller_offline_devices:
            # Ghi trạng thái "controller_offline" cho các Thiết bị đầu cuối (đầu đọc thẻ/vân tay con)
            controller_offline_devices.write({"status": "controller_offline"})

        # [Device Model] 2. Tìm các Thiết bị con có Controller cha online nhưng bản thân thiết bị không tương tác gần đây
        device_offline = devices.search(
            [
                ("controller_id.status", "=", "online"),
                ("status", "!=", "offline"),
                "|",
                ("last_seen_at", "=", False),
                ("last_seen_at", "<", timeout),
            ]
        )
        if device_offline:
            # Ghi trạng thái "offline" cho các Thiết bị đầu cuối (đầu đọc thẻ/vân tay con)
            device_offline.write({"status": "offline"})

    @api.model
    def cron_sync_missing_employees(self):
        """Tự động tạo bản ghi nhân viên Gate Keeper cho hr.employee chưa có.

        Đảm bảo tất cả nhân viên HR đều có hồ sơ trong Gate Keeper để
        có thể đăng ký sinh trắc học và đồng bộ với phần cứng.
        Lưu ý: sudo() dùng có chủ đích để vượt qua multi-company trong cron.
        """
        existing_hr_employee_ids = (
            self.env["t4.gate_keeper.employee"]
            .sudo()
            .search([])
            .mapped("hr_employee_id")
            .ids
        )

        missing_employees = self.env["hr.employee"].sudo().search(
            [("id", "not in", existing_hr_employee_ids)]
        )

        if not missing_employees:
            return

        vals_list = []
        for emp in missing_employees:
            # emp_id sẽ được tự động sinh bởi create() của gk_employee
            # thông qua ir.sequence hoặc fallback UUID — không lấy từ hr.employee
            vals_list.append(
                {
                    "name": emp.name,
                    "hr_employee_id": emp.id,
                }
            )

        # ---> Chuyển sang: Hàm create() trong file models/gk_employee.py để tạo nhân viên mới
        created = self.env["t4.gate_keeper.employee"].sudo().create(vals_list)
        _logger.info(
            "cron_sync_missing_employees: Tạo %d nhân viên Gate Keeper mới.",
            len(created),
        )

    @api.model
    def cron_escalate_warnings(self):
        """Leo thang cảnh báo chưa giải quyết quá ngưỡng thời gian.

        Quy tắc leo thang:
        - Tìm cảnh báo ở trạng thái 'warning' chưa được leo thang hoặc
          đã qua ESCALATION_THRESHOLD_MINUTES phút kể từ lần leo thang cuối.
        - Tăng priority theo thứ tự: low → medium → high → critical.
        - Ghi lại thời điểm leo thang vào escalated_at.
        """
        now = fields.Datetime.now()
        escalation_cutoff = now - timedelta(minutes=ESCALATION_THRESHOLD_MINUTES)

        # Lấy cảnh báo cần leo thang: chưa ở critical, chưa leo thang hoặc leo thang đã lâu
        warnings = self.env["t4.gate_keeper.area_warning"].search(
            [
                ("state", "=", "warning"),
                ("priority", "!=", "critical"),
                "|",
                ("escalated_at", "=", False),
                ("escalated_at", "<", escalation_cutoff),
            ]
        )

        if not warnings:
            return

        escalated_count = 0
        for warning in warnings:
            current_priority = warning.priority or "low"
            try:
                current_idx = PRIORITY_ESCALATION.index(current_priority)
            except ValueError:
                current_idx = 0

            # Tăng lên mức tiếp theo nếu chưa đến critical
            if current_idx < len(PRIORITY_ESCALATION) - 1:
                new_priority = PRIORITY_ESCALATION[current_idx + 1]
                warning.write({
                    "priority": new_priority,
                    "escalated_at": now,
                })
                escalated_count += 1

        if escalated_count:
            _logger.info(
                "cron_escalate_warnings: Đã leo thang %d cảnh báo.",
                escalated_count,
            )

    @api.model
    def cron_overtime_check(self):
        """Kiểm tra nhân viên vẫn ở trong khu vực sau khi vượt ngưỡng overtime.

        Quy tắc:
        - Tìm tất cả nhân viên có presence_state='inside' và current_area_id.
        - So sánh thời gian vào cuối cùng với ngưỡng OVERTIME_THRESHOLD_HOURS.
        - Nếu vượt ngưỡng và chưa có cảnh báo overtime đang mở → tạo area_warning loại 'overtime'.
        """
        now = fields.Datetime.now()
        overtime_cutoff = now - timedelta(hours=OVERTIME_THRESHOLD_HOURS)

        # Lấy warning_type 'overtime'
        overtime_type = self.env["t4.gate_keeper.area_warning_type"].search(
            [("condition_type", "=", "overtime")], limit=1
        )
        if not overtime_type:
            _logger.warning(
                "cron_overtime_check: Không tìm thấy warning type 'overtime'. "
                "Vui lòng tạo bản ghi area_warning_type với condition_type='overtime'."
            )
            return

        # Nhân viên đang ở trong khu vực
        employees_inside = self.env["t4.gate_keeper.employee"].search(
            [
                ("presence_state", "=", "inside"),
                ("current_area_id", "!=", False),
            ]
        )

        if not employees_inside:
            return

        overtime_count = 0
        for emp in employees_inside:
            # Tìm log vào cuối cùng của nhân viên trong khu vực hiện tại
            last_entry = self.env["t4.gate_keeper.access_log"].search(
                [
                    ("employee_id", "=", emp.id),
                    ("area_id", "=", emp.current_area_id.id),
                    ("direction", "=", "in"),
                    ("is_system_generated", "=", False),
                ],
                order="access_time desc",
                limit=1,
            )

            if not last_entry:
                continue

            # Kiểm tra có vượt ngưỡng không
            if last_entry.access_time > overtime_cutoff:
                continue

            # Kiểm tra đã có cảnh báo overtime đang mở chưa
            existing = self.env["t4.gate_keeper.area_warning"].search(
                [
                    ("employee_id", "=", emp.id),
                    ("area_id", "=", emp.current_area_id.id),
                    ("warning_type_id", "=", overtime_type.id),
                    ("state", "=", "warning"),
                ],
                limit=1,
            )
            if existing:
                continue

            # Tạo cảnh báo overtime
            duration_hours = (now - last_entry.access_time).total_seconds() / 3600.0
            # ---> Chuyển sang: Tạo bản ghi cảnh báo trong file models/gk_area_warning.py
            self.env["t4.gate_keeper.area_warning"].create(
                {
                    "area_id": emp.current_area_id.id,
                    "employee_id": emp.id,
                    "access_log_id": last_entry.id,
                    "warning_type_id": overtime_type.id,
                    "priority": "medium",
                    "description": _(
                        "%s đã ở trong khu vực \"%s\" hơn %.1f giờ — vượt ngưỡng overtime"
                    )
                    % (emp.name, emp.current_area_id.name, duration_hours),
                }
            )
            overtime_count += 1

        if overtime_count:
            _logger.info(
                "cron_overtime_check: Tạo %d cảnh báo overtime mới.",
                overtime_count,
            )
