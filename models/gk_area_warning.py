# -*- coding: utf-8 -*-
# Mục đích: Quản lý vòng đời cảnh báo bảo mật theo khu vực, bao gồm tạo, leo thang và giải quyết.

from odoo import fields, models


class GateKeeperAreaWarning(models.Model):
    _name = "t4.gate_keeper.area_warning"
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
    )

    priority = fields.Integer(string="Priority", default=10)

    # Used by escalation cron: tracks the last escalation time to avoid multiple escalations in one cron cycle
    escalated_at = fields.Datetime(string="Escalated At")

    resolved_by_id = fields.Many2one("res.users", string="Resolved By", readonly=True)
    resolved_at = fields.Datetime(string="Resolved At", readonly=True)
    resolution_notes = fields.Text(string="Resolution Notes")

    def action_resolve(self):
        """Mark warning records as resolved with current user and timestamp."""
        for warning in self:
            warning.write(
                {
                    "state": "resolved",
                    "resolved_by_id": self.env.user.id,
                    "resolved_at": fields.Datetime.now(),
                }
            )
