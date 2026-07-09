# -*- coding: utf-8 -*-
# Mục đích: Định nghĩa model lệnh điều khiển từ xa (Command) gửi đến thiết bị.

from odoo import fields, models


class GateKeeperCommand(models.Model):
    _name = "t4.gate_keeper.command"
    _description = "Gate Keeper Remote Command"
    _order = "id desc"

    controller_id = fields.Many2one(
        comodel_name="t4.gate_keeper.controller",
        string="Controller",
        required=True,
        index=True,
        ondelete="cascade",
    )

    device_id = fields.Many2one(
        comodel_name="t4.gate_keeper.device",
        string="Device",
        index=True,
        ondelete="cascade",
    )

    action_type = fields.Selection(
        selection=[
            ("open_door", "Open Door"),
            ("close_door", "Close Door"),
            ("lock_down", "Lock Down"),
        ],
        string="Action Type",
        required=True,
        help="The specific hardware control action to execute.",
    )

    parameters = fields.Char(
        string="Parameters",
        help="Optional parameters in JSON format or plain text.",
    )

    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("sending", "Sending"),
            ("success", "Success"),
            ("failed", "Failed"),
        ],
        string="Status",
        default="pending",
        required=True,
        help="Lifecycle state of the command.",
    )

    execution_message = fields.Text(
        string="Execution Message",
        help="Status message or error logs sent back by the controller hardware.",
    )
