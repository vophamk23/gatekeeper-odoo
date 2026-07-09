# -*- coding: utf-8 -*-
# Mục đích: Quản lý vòng đời cảnh báo bảo mật theo khu vực, bao gồm tạo, leo thang và giải quyết.

from odoo import api, fields, models


class GateKeeperAreaWarning(models.Model):
    _name = "t4.gate_keeper.area_warning"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Gate Keeper Area Warning"
    _order = "create_date desc"

    area_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area",
        string="Area",
        required=True,
        ondelete="cascade",
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

    access_log_id = fields.Many2one(
        comodel_name="t4.gate_keeper.access_log",
        string="Related Access Log",
        ondelete="set null",
    )

    warning_type_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area_warning_type",
        string="Warning Type",
        required=True,
        ondelete="restrict",
    )

    policy_id = fields.Many2one(
        comodel_name="t4.gate_keeper.alert_policy",
        string="Alert Policy",
        ondelete="set null",
    )

    description = fields.Text(string="Description")

    state = fields.Selection(
        selection=[("warning", "Warning"), ("resolved", "Resolved")],
        string="State",
        default="warning",
        required=True,
        tracking=True,
    )

    priority = fields.Selection(
        selection=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Mức độ ưu tiên",
        default="low",
        tracking=True,
        help="Copy từ policy khi tạo. Tự động leo thang nếu không được xử lý.",
    )


    # Dùng bởi cron leo thang: ghi lại thời điểm leo thang cuối để tránh leo thang 2 lần trong cùng chu kỳ
    escalated_at = fields.Datetime(string="Escalated At")

    resolved_by_id = fields.Many2one("res.users", string="Resolved By", readonly=True)
    resolved_at = fields.Datetime(string="Resolved At", readonly=True)
    resolution_notes = fields.Text(string="Resolution Notes")

    def action_resolve(self):
        """Đánh dấu các cảnh báo được chọn là đã giải quyết.

        Ghi lại người giải quyết (resolved_by_id) và thời điểm giải quyết (resolved_at).
        Khi tất cả cảnh báo trong khu vực được resolve → area.status tự chuyển về 'normal'.
        """
        for warning in self:
            warning.write(
                {
                    "state": "resolved",
                    "resolved_by_id": self.env.user.id,
                    "resolved_at": fields.Datetime.now(),
                }
            )

    # Được gọi bởi: _evaluate_policy_rules() tại L253 trong file models/gk_access_log.py
    @api.model
    def create_from_log(self, access_log, condition_type, description, policy=False):
        """Tạo bản ghi cảnh báo gắn với access log được truyền vào.

        Tìm warning_type qua code (condition_type), bỏ qua nếu:
        - Không tìm thấy warning_type tương ứng.
        - Đã có cảnh báo cùng loại và cùng log đang mở (tránh trùng).
        """
        warning_type = self.env["t4.gate_keeper.area_warning_type"].search(
            [("code", "=", condition_type)], limit=1
        )
        if not warning_type:
            return False

        existing = self.search(
            [
                ("access_log_id", "=", access_log.id),
                ("warning_type_id", "=", warning_type.id),
                ("state", "=", "warning"),
            ],
            limit=1,
        )
        if existing:
            return existing

        values = {
            "area_id": access_log.area_id.id if access_log.area_id else False,
            "device_id": access_log.device_id.id if access_log.device_id else False,
            "employee_id": access_log.employee_id.id if access_log.employee_id else False,
            "access_log_id": access_log.id,
            "warning_type_id": warning_type.id,
            "description": description,
            "priority": policy.priority if policy else "low",
        }
        if policy:
            values["policy_id"] = policy.id

        return self.create(values)
