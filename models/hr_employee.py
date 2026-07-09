# -*- coding: utf-8 -*-
# Mục đích: Kế thừa hr.employee để đồng bộ dữ liệu nhân sự vào Gate Keeper.

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    emp_id = fields.Char(string="Mã số nhân viên", default=False)

    _sql_constraints = [
        ("employee_id_custom_unique", "UNIQUE(emp_id)", "Employee ID must be unique.")
    ]

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        gk_employee_env = self.env["t4.gate_keeper.employee"].sudo()
        for emp in employees:
            gk_emp = False
            if emp.emp_id:
                gk_emp = gk_employee_env.search([("emp_id", "=", emp.emp_id)], limit=1)
            
            if gk_emp:
                gk_emp.write({"hr_employee_id": emp.id})
            else:
                gk_emp = gk_employee_env.create(
                    {
                        "name": emp.name,
                        "emp_id": emp.emp_id,
                        "hr_employee_id": emp.id,
                    }
                )
            if not emp.emp_id:
                emp.emp_id = gk_emp.emp_id
        return employees

    def write(self, vals):
        res = super(HrEmployee, self).write(vals)

        if "name" in vals:
            # Using sudo() because HR users might not have access to gate keeper models
            gk_employee_env = self.env["t4.gate_keeper.employee"].sudo()
            for emp in self:
                gk_emp = gk_employee_env.search(
                    [("hr_employee_id", "=", emp.id)], limit=1
                )

                if gk_emp:
                    gk_emp.write({"name": emp.name})

        return res
