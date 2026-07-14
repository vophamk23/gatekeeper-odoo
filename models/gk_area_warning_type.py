# -*- coding: utf-8 -*-
# Mục đích: Định nghĩa các loại cảnh báo và điều kiện kích hoạt tương ứng.

from odoo import fields, models


class GateKeeperAreaWarningType(models.Model):
    _name = "t4.gate_keeper.area_warning_type"
    _description = "Gate Keeper Area Warning Type"
    _order = "name"

    name = fields.Char(string="Warning Type Name", required=True)
    code = fields.Char(
        string="Code",
        required=True,
        help="Code used in business logic to identify the warning type.",
    )
    description = fields.Text(string="Description")
    condition_type = fields.Selection(
        selection=[
            ("unauthorized_time", "Unauthorized Time"),
            ("invalid_sequence", "Invalid Sequence"),
            ("device_offline", "Device Offline"),
            ("overtime", "Overtime"),
            ("unknown_card", "Unknown Card"),
            ("unauthorized_area", "Unauthorized Area"),
        ],
        string="Condition Type",
        default="unauthorized_time",
    )

    _code_unique = models.Constraint(
        "unique(code)", "Warning type code must be unique."
    )
