# -*- coding: utf-8 -*-
# Mục đích: Các thiết lập công việc định kỳ (cron) của module Gate Keeper.
#          Xử lý đồng bộ trạng thái phần cứng (phát hiện offline) và
#          đồng bộ hồ sơ nhân viên từ HR sang Gate Keeper.
# pyrefly: ignore [missing-import]
from odoo import api, fields, models
from datetime import timedelta

# Number of minutes without a heartbeat before a controller/device is considered offline
WAITING_TIME = 5


class T4GateKeeperScheduler(models.Model):
    _name = "t4.gate_keeper.scheduler"
    _description = "Gate Keeper Scheduler"

    @api.model
    def cron_update_hardware_status(self):
        """Mark controllers and devices as offline when heartbeat/last-seen exceeds WAITING_TIME minutes."""
        timeout = fields.Datetime.now() - timedelta(minutes=WAITING_TIME)

        controllers = self.env["t4.gate_keeper.controller"]

        # Offline controllers: no heartbeat or heartbeat older than threshold
        offline = controllers.search(
            [
                ("status", "!=", "offline"),
                "|",
                ("last_heartbeat_at", "=", False),
                ("last_heartbeat_at", "<", timeout),
            ]
        )
        if offline:
            offline.write({"status": "offline"})

        devices = self.env["t4.gate_keeper.device"]

        # 1. Devices whose controller is offline → mark as controller_offline
        controller_offline_devices = devices.search(
            [
                ("controller_id.status", "!=", "online"),
                ("status", "!=", "controller_offline"),
            ]
        )
        if controller_offline_devices:
            controller_offline_devices.write({"status": "controller_offline"})

        # 2. Devices on an online controller but not seen recently → mark as offline
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
            device_offline.write({"status": "offline"})

    @api.model
    def cron_sync_missing_employees(self):
        """Auto-create Gate Keeper employee records for any hr.employee without one.

        This ensures hardware enrollment (biometric sync) stays possible for all staff.
        Note: sudo() is used intentionally to bypass multi-company record rules during the
        scheduled sync — the cron runs in a privileged context by design.
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

        if missing_employees:
            vals_list = []
            for emp in missing_employees:
                vals_list.append(
                    {
                        "name": emp.name,
                        # TODO: Thay emp.emp_id bằng mã định danh riêng được sinh tự động bởi Gate Keeper
                        "emp_id": emp.emp_id,
                        "hr_employee_id": emp.id,
                    }
                )
            self.env["t4.gate_keeper.employee"].sudo().create(vals_list)

    @api.model
    def cron_escalate_warnings(self):
        """TODO: Leo thang cảnh báo chưa giải quyết quá ngưỡng thời gian cấu hình.

        Logic (theo gatekeeper.md §9.4):
        - Tìm các cảnh báo ở trạng thái 'warning' có tuổi vượt ngưỡng escalation_threshold_minutes.
        - Kích hoạt hành động leo thang (ví dụ: thông báo giám sát viên, tăng độ ưu tiên).
        - Cập nhật escalated_at để tránh kích hoạt lại trong chu kỳ cron tiếp theo.
        """
        pass

    @api.model
    def cron_overtime_check(self):
        """TODO: Kiểm tra nhân viên vẫn ở trong khu vực sau khi vượt ngưỡng overtime.

        Logic (theo gatekeeper.md §9.5):
        - Tìm tất cả bản ghi presence_state với state='inside'.
        - Kiểm tra liệu access_time lần vào cuối có vượt ngưỡng overtime của chi nhánh không.
        - Nếu có, tạo area_warning loại 'overtime'.
        """
        pass
