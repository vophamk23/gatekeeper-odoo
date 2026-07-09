# -*- coding: utf-8 -*-
# Mục đích: Lưu lịch sử thay đổi trạng thái của thiết bị và controller (audit uptime/downtime).

from odoo import fields, models


class GateKeeperDeviceLog(models.Model):
    _name = "t4.gate_keeper.device_log"
    _description = "Gate Keeper Device Log"
    _order = "changed_at desc"

    device_id = fields.Many2one(
        comodel_name="t4.gate_keeper.device",
        string="Device",
        required=True,
        ondelete="cascade",
    )

    controller_id = fields.Many2one(
        comodel_name="t4.gate_keeper.controller",
        string="Controller",
        related="device_id.controller_id",
        store=True,
        readonly=True,
    )

    event_type = fields.Selection(
        selection=[
            ("status_changed", "Status Changed"),
            ("heartbeat", "Heartbeat"),
            ("offline", "Offline"),
            ("online", "Online"),
            ("maintenance", "Maintenance"),
        ],
        string="Event Type",
        required=True,
        default="status_changed",
    )

    changed_at = fields.Datetime(
        string="Changed At",
        default=fields.Datetime.now,
        required=True,
        help="Thời điểm thay đổi trạng thái.",
    )
    old_status = fields.Char(
        string="Old Status",
        help="Trạng thái cũ trước khi thay đổi.",
    )
    new_status = fields.Char(
        string="New Status",
        help="Trạng thái mới sau khi thay đổi.",
    )
    note = fields.Text(string="Note")
