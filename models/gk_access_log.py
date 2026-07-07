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
        records = super().create(vals_list)
        for record in records:
            if record.device_id:
                record._check_access_security_rules()
        return records

    def write(self, vals):
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
                _("Access logs are immutable except for system-managed fields.")
            )
        return super().write(vals)

    def unlink(self):
        raise ValidationError(_("Access logs cannot be deleted."))

    def _check_access_security_rules(self):
        self.ensure_one()
        if not self.device_id:
            return

        self._evaluate_policy_rules()

    def _evaluate_policy_rules(self):
        """Duyệt qua các chính sách đang khớp (branch/area/group) và tạo cảnh báo khi vi phạm."""
        policies = self.env["t4.gate_keeper.alert_policy"]._get_matching_policies(self)
        for policy in policies:
            triggered, reason = policy._evaluate(self)
            if triggered:
                self._create_warning(policy.warning_type_id.code, reason, policy=policy)

    def _create_warning(self, condition_type, description, policy=False):
        warning_type = self.env["t4.gate_keeper.area_warning_type"].search(
            [("code", "=", condition_type)], limit=1
        )
        if not warning_type:
            return

        existing = self.env["t4.gate_keeper.area_warning"].search(
            [
                ("access_log_id", "=", self.id),
                ("warning_type_id", "=", warning_type.id),
                ("state", "=", "warning"),
            ],
            limit=1,
        )
        if existing:
            return

        values = {
            "area_id": self.area_id.id if self.area_id else False,
            "device_id": self.device_id.id if self.device_id else False,
            "employee_id": self.employee_id.id if self.employee_id else False,
            "access_log_id": self.id,
            "warning_type_id": warning_type.id,
            "description": description,
            "priority": 10,
        }
        if policy:
            values["policy_id"] = policy.id

        self.env["t4.gate_keeper.area_warning"].create(values)
