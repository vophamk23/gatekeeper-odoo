# -*- coding: utf-8 -*-
# Mục đích: Quản lý các khu vực (zone) trong chi nhánh và theo dõi cảnh báo theo khu vực.

from odoo import api, fields, models, _

AREA_STATUS = [
    ("warning", "Warning"),
    ("normal", "Normal"),
]


class GateKeeperArea(models.Model):
    _name = "t4.gate_keeper.area"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Gate Keeper Area"
    _order = "name"

    name = fields.Char(
        string="Area Name",
        required=True,
        help="Name of the area, e.g., lobby, parking lot, warehouse.",
    )

    branch_id = fields.Many2one(
        "t4.gate_keeper.branch",
        string="Branch",
        required=True,
        ondelete="cascade",
        index=True,
        help="Branch where this area is located.",
    )

    device_ids = fields.One2many(
        "t4.gate_keeper.device",
        "area_id",
        string="Devices",
    )

    warning_ids = fields.One2many(
        "t4.gate_keeper.area_warning",
        "area_id",
        string="Warnings",
    )

    status = fields.Selection(
        selection=AREA_STATUS,
        string="Status",
        compute="_compute_status",
        store=True,
        default="normal",
        tracking=True,
    )

    warning_count = fields.Integer(
        string="Warning Count",
        compute="_compute_warning_count",
    )

    @api.depends("warning_ids.state")
    def _compute_status(self):
        """Tính trạng thái khu vực dựa trên cảnh báo đang mở.

        normal  → không có cảnh báo nào đang active.
        warning → có ít nhất 1 cảnh báo state='warning'.
        """
        for area in self:
            active_warnings = area.warning_ids.filtered(lambda w: w.state == "warning")
            area.status = "warning" if active_warnings else "normal"

    @api.depends("warning_ids")
    def _compute_warning_count(self):
        """Đếm tổng số cảnh báo (cả đã giải quyết) trong khu vực."""
        for area in self:
            area.warning_count = len(area.warning_ids)

    def action_view_warnings(self):
        """Mở danh sách cảnh báo thuộc khu vực này."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Warnings: %s") % self.name,
            "res_model": "t4.gate_keeper.area_warning",
            "view_mode": "list,form",
            "domain": [("area_id", "=", self.id)],
            "context": {
                "default_area_id": self.id,
            },
        }
