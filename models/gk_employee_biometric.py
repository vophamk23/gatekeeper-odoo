# -*- coding: utf-8 -*-
# Mục đích: Lưu trữ mẫu sinh trắc học (vân tay, khuôn mặt) của từng nhân viên theo thuật toán.

from odoo import models, fields, api, _

class GateKeeperEmployeeBiometric(models.Model):
    _name = "t4.gate_keeper.employee.biometric"
    _description = "Employee Biometric"
    _order = "employee_id, biometric_type, finger_index"

    employee_id = fields.Many2one(
        comodel_name="t4.gate_keeper.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
        index=True,
    )

    algorithm_id = fields.Many2one(
        comodel_name="t4.gate_keeper.algorithm",
        string="Algorithm",
        required=True,
        ondelete="restrict",
        index=True,
    )

    biometric_type = fields.Selection(
        related="algorithm_id.algorithm_type",
        string="Biometric Type",
        store=True,
        readonly=True,
    )

    template = fields.Binary(
        string="Biometric Template",
        required=True,
        help="Biometric template data (e.g., face template or fingerprint template).",
    )

    finger_index = fields.Integer(
        string="Finger/Slot Index",
        default=0,
        help="Index of the finger (usually 0-9) or slot number for the biometric template.",
    )

    description = fields.Char(
        string="Description",
    )

    _employee_biometric_unique = models.Constraint(
        "unique(employee_id, algorithm_id, finger_index)",
        "A biometric template already exists for this employee, algorithm, and finger/slot index.",
    )
