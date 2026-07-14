# -*- coding: utf-8 -*-
# Mục đích: Quản lý thẻ RFID và thông tin xác thực của nhân viên.

from odoo import fields, models


class GateKeeperAuthInfo(models.Model):
    _name = "t4.gate_keeper.auth_info"
    _description = "Gate Keeper Authentication Information"
    _order = "card_code"

    employee_id = fields.Many2one(
        comodel_name="t4.gate_keeper.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
    )

    card_code = fields.Char(string="Card Code", required=True, copy=False)
    active = fields.Boolean(string="Active", default=True)
    description = fields.Text(string="Description")

    _card_code_unique = models.Constraint(
        "unique(card_code)",
        "Card code must be unique.",
    )
