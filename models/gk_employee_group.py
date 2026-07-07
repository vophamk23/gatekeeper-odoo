# -*- coding: utf-8 -*-
# Mục đích: Quản lý nhóm nhân viên dùng để cấu hình phạm vi chính sách cảnh báo.

from odoo import fields, models


class GateKeeperEmployeeGroup(models.Model):
    _name = "t4.gate_keeper.employee_group"
    _description = "Gate Keeper Employee Group"
    _order = "name"

    name = fields.Char(string="Group Name", required=True)
    code = fields.Char(string="Code", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        string="Branch",
        help="Branch where this group is used.",
    )

    employee_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.employee",
        string="Employees",
        help="Employees assigned to this group.",
    )
