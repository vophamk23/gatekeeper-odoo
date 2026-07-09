from . import models
from . import utils


def post_init_hook(env):
    hr_employees = env['hr.employee'].search([])
    gk_employee_env = env['t4.gate_keeper.employee']
    
    for emp in hr_employees:
        existing = gk_employee_env.search([('hr_employee_id', '=', emp.id)], limit=1)
        if not existing and emp.emp_id:
            existing = gk_employee_env.search([('emp_id', '=', emp.emp_id)], limit=1)
            if existing:
                existing.write({'hr_employee_id': emp.id})
                
        if not existing:
            gk_emp = gk_employee_env.create({
                'name': emp.name,
                'emp_id': emp.emp_id,
                'hr_employee_id': emp.id,
            })
            if not emp.emp_id:
                emp.emp_id = gk_emp.emp_id

