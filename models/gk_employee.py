# -*- coding: utf-8 -*-
# Mục đích: Quản lý hồ sơ nhân viên trong Gate Keeper và liên kết sinh trắc học.

import uuid

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GateKeeperEmployee(models.Model):
    _name = "t4.gate_keeper.employee"
    _description = "Gate Keeper Employee"
    _order = "name"

    name = fields.Char(string="Employee Name", required=True)
    emp_id = fields.Char(string="Employee ID", required=True, copy=False, readonly=True)
    hr_employee_id = fields.Many2one(
        "hr.employee", string="HR Employee", ondelete="set null"
    )

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        string="Branch",
        help="Branch restriction for employee sync.",
    )

    biometric_ids = fields.One2many(
        comodel_name="t4.gate_keeper.employee.biometric",
        inverse_name="employee_id",
        string="Biometrics",
    )

    group_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.employee_group",
        string="Groups",
    )

    presence_state = fields.Selection(
        selection=[
            ("inside", "Inside"),
            ("outside", "Outside"),
            ("unknown", "Unknown"),
        ],
        string="Presence State",
        default="outside",
        readonly=True,
    )

    current_area_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area",
        string="Current Area",
        readonly=True,
    )

    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ("emp_id_unique", "UNIQUE(emp_id)", "Employee ID must be unique."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("emp_id"):
                vals["emp_id"] = (
                    self.env["ir.sequence"]
                    .sudo()
                    .next_by_code("t4.gate_keeper.employee")
                )
            if not vals.get("emp_id"):
                vals["emp_id"] = self._generate_emp_id()
        return super().create(vals_list)

    def write(self, vals):
        if "emp_id" in vals:
            for record in self:
                if vals.get("emp_id") != record.emp_id:
                    raise ValidationError(_("Employee ID cannot be changed."))
        return super().write(vals)

    def _generate_emp_id(self):
        # Fallback khi chưa khai báo ir.sequence cho model này.
        # Thêm suffix ngẫu nhiên để tránh trùng khi bulk create nhiều bản ghi trong cùng 1 giây
        # (ví dụ: cron_sync_missing_employees tạo hàng loạt).
        timestamp = fields.Datetime.now().strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:6].upper()
        return "GK-%s-%s" % (timestamp, suffix)
