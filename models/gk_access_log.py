# -*- coding: utf-8 -*-
# Mục đích: Lưu trữ bất biến sự kiện ra/vào. Trái tim của engine kiểm duyệt bảo mật.
#          Mỗi lần tạo log sẽ tự động kiểm tra chính sách cảnh báo và phát sinh area warning.
# pyrefly: ignore [missing-import]
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GateKeeperAccessLog(models.Model):
    _name = "t4.gate_keeper.access_log"
    _description = "Gate Keeper Access Log"
    _order = "access_time desc"

    controller_id = fields.Many2one(
        comodel_name="t4.gate_keeper.controller",
        string="Controller",
        ondelete="set null",
    )

    device_id = fields.Many2one(
        comodel_name="t4.gate_keeper.device",
        string="Device",
        ondelete="set null",
    )

    employee_id = fields.Many2one(
        comodel_name="t4.gate_keeper.employee",
        string="Employee",
        ondelete="set null",
    )

    access_time = fields.Datetime(
        string="Access Time", required=True, default=fields.Datetime.now
    )
    direction = fields.Selection(
        [("in", "In"), ("out", "Out")], string="Direction", required=True, default="in"
    )
    verification_type = fields.Selection(
        [
            ("face", "Face"),
            ("fingerprint", "Fingerprint"),
            ("card", "Card"),
            ("password", "Password"),
            ("other", "Other"),
        ],
        string="Verification Type",
        default="card",
    )
    sync_status = fields.Selection(
        [("success", "Success"), ("fail", "Fail"), ("updating", "Updating")],
        string="Sync Status",
        default="success",
    )
    is_system_generated = fields.Boolean(
        string="System Generated", default=False, readonly=True
    )

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        string="Branch",
        related="device_id.branch_id",
        store=True,
        readonly=True,
    )

    area_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area",
        string="Area",
        related="device_id.area_id",
        store=True,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Ghi nhận sự kiện ra/vào và kích hoạt engine kiểm tra chính sách bảo mật.

        Sau khi tạo bản ghi, tự động:
        1. Kiểm tra chính sách cảnh báo và tạo area_warning nếu vi phạm.
        2. Cập nhật presence_state của nhân viên.
        Bỏ qua các log tự sinh (is_auto_rejection) để tránh đệ quy.
        """
        from datetime import timedelta
        import logging

        _logger = logging.getLogger(__name__)

        filtered_vals_list = []
        for vals in vals_list:
            # Chống double-scan (quẹt trùng trong khoảng thời gian ngắn, ví dụ: 10 giây)
            # Chỉ lọc đối với các sự kiện thực tế của nhân viên (có employee_id) và thiết bị
            if (
                vals.get("employee_id")
                and vals.get("device_id")
                and not vals.get("is_system_generated")
                and not self.env.context.get("is_auto_rejection")
            ):
                access_time = fields.Datetime.to_datetime(
                    vals.get("access_time") or fields.Datetime.now()
                )
                limit_time = access_time - timedelta(seconds=10)

                # Kiểm tra xem có lượt quẹt nào cùng nhân viên, cùng thiết bị, cùng chiều trong vòng 10 giây trước đó chưa
                existing = self.env["t4.gate_keeper.access_log"].search(
                    [
                        ("employee_id", "=", vals["employee_id"]),
                        ("device_id", "=", vals["device_id"]),
                        ("direction", "=", vals.get("direction", "in")),
                        ("is_system_generated", "=", False),
                        ("access_time", ">=", limit_time),
                        ("access_time", "<=", access_time),
                    ],
                    limit=1,
                )

                if existing:
                    _logger.info(
                        "Bỏ qua sự kiện trùng lặp (double-scan) của nhân viên ID %s tại thiết bị %s.",
                        vals["employee_id"],
                        vals["device_id"],
                    )
                    continue

            filtered_vals_list.append(vals)

        if not filtered_vals_list:
            # Trả về recordset rỗng của model này
            return self.env[self._name]

        records = super().create(filtered_vals_list)
        for record in records:
            # Bỏ qua log hệ thống tự sinh (auto_rejection) để tránh đệ quy vô hạn
            if self.env.context.get("is_auto_rejection"):
                continue
            if record.direction not in ("in", "out"):
                continue

            # Kích hoạt kiểm duyệt bảo mật
            # ---> Gọi hàm: _check_access_security_rules() tại L208 trong file này (gk_access_log.py)
            record._check_access_security_rules()
            # Cập nhật trạng thái hiện diện (sẽ bị bỏ qua nếu phát hiện vi phạm ở dòng trên)
            # ---> Gọi hàm: _update_presence_state() tại L172 trong file này (gk_access_log.py)
            record._update_presence_state()

        return records

    def write(self, vals):
        """Bảo vệ tính bất biến của access log.

        Chỉ cho phép sửa sync_status và các field phi cốt lõi.
        Bypass được khi có context allow_access_log_write=True (dành cho hệ thống nội bộ).
        """
        # Cho phép bypass nếu có context nội bộ (VD: hệ thống tự cập nhật trạng thái)
        if self.env.context.get("allow_access_log_write"):
            return super().write(vals)
        if any(
            field in vals
            for field in [
                "employee_id",
                "access_time",
                "device_id",
                "controller_id",
                "direction",
                "verification_type",
            ]
        ):
            raise ValidationError(
                _("Không được phép sửa nhật ký ra vào, ngoại trừ: sync_status")
            )
        return super().write(vals)

    def unlink(self):
        """Ngăn xóa log — nhật ký ra/vào là bất biến theo thiết kế."""
        raise ValidationError(_("Không được phép xóa nhật ký ra vào."))

    # Được gọi bởi: create() tại L143 trong file này (gk_access_log.py)
    def _update_presence_state(self):
        """Cập nhật trạng thái hiện diện của nhân viên sau khi quẹt thẻ.

        - Nếu log vi phạm (có area_warning gắn với log này):
            + direction=in (không phải anti-passback): tạo log 'out' giả tránh khóa sai presence_state.
            + Không cập nhật presence_state.
        - Nếu hợp lệ: cập nhật presence_state và current_area_id của nhân viên.
        """
        self.ensure_one()
        emp = self.employee_id
        if not emp:
            return

        # Kiểm tra có cảnh báo vi phạm nào được tạo từ log này không
        active_warnings = self.env["t4.gate_keeper.area_warning"].search(
            [("access_log_id", "=", self.id), ("state", "=", "warning")],
            limit=1,
        )

        if active_warnings:
            # Kiểm tra có phải anti-passback không
            is_antipassback = any(
                w.warning_type_id.condition_type == "invalid_sequence"
                for w in active_warnings
            )
            # Vi phạm giờ/khu vực (không phải anti-passback) + quẹt vào:
            # Tạo log 'out' giả để tránh khóa sai trạng thái hiện diện
            if self.direction == "in" and not is_antipassback:
                from datetime import timedelta

                fake_out_time = self.access_time + timedelta(seconds=1)
                self.env["t4.gate_keeper.access_log"].with_context(
                    is_auto_rejection=True
                ).create(
                    {
                        "employee_id": emp.id,
                        "device_id": self.device_id.id if self.device_id else False,
                        "controller_id": (
                            self.controller_id.id if self.controller_id else False
                        ),
                        "access_time": fake_out_time,
                        "direction": "out",
                        "verification_type": self.verification_type,
                        "is_system_generated": True,
                    }
                )
            # Vi phạm: không cập nhật presence_state
            return

        # Hợp lệ: cập nhật presence_state và current_area_id
        new_state = "inside" if self.direction == "in" else "outside"
        new_area = self.area_id if new_state == "inside" else False
        emp.with_context(allow_employee_presence_write=True).write(
            {
                "presence_state": new_state,
                "current_area_id": new_area.id if new_area else False,
            }
        )

    # Được gọi bởi: create() tại L140 trong file này (gk_access_log.py)
    def _check_access_security_rules(self):
        """Điểm vào kiểm tra bảo mật — gọi engine đánh giá chính sách.

        Bỏ qua nếu log không gắn với thiết bị (không thể xác định khu vực).
        """
        self.ensure_one()
        if not self.device_id:
            return

        # ---> Gọi hàm: _evaluate_policy_rules() ngay bên dưới trong file này (gk_access_log.py)
        self._evaluate_policy_rules()

    # Được gọi bởi: _check_access_security_rules() tại L245 trong file này (gk_access_log.py)
    def _evaluate_policy_rules(self):
        """Duyệt qua các chính sách đang khớp (branch/area/group) và tạo cảnh báo khi vi phạm."""
        # ---> Gọi hàm: _get_matching_policies() trong file models/gk_alert_policy.py để tìm các chính sách bảo mật phù hợp
        policies = self.env["t4.gate_keeper.alert_policy"]._get_matching_policies(self)
        for policy in policies:
            # ---> Gọi hàm: _evaluate() trong file models/gk_alert_policy.py để đánh giá cụ thể luật lệ của chính sách
            triggered, reason = policy._evaluate(self)
            if triggered:
                # ---> Gọi hàm: create_from_log() trong file models/gk_area_warning.py để ghi nhận cảnh báo bảo mật mới
                self.env["t4.gate_keeper.area_warning"].create_from_log(
                    self, policy.warning_type_id.code, reason, policy=policy
                )
