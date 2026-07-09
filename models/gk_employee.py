# -*- coding: utf-8 -*-
# Mục đích: Quản lý hồ sơ nhân viên trong Gate Keeper và liên kết sinh trắc học.

import uuid

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class GateKeeperEmployee(models.Model):
    _name = "t4.gate_keeper.employee"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Gate Keeper Employee"
    _order = "name"

    name = fields.Char(string="Employee Name", required=True, tracking=True)
    emp_id = fields.Char(string="Employee ID", required=True, copy=False, readonly=True, tracking=True)
    hr_employee_id = fields.Many2one(
        "hr.employee", string="HR Employee", ondelete="set null", tracking=True
    )

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        string="Branch",
        tracking=True,
        help="Branch restriction for employee sync.",
    )

    biometric_ids = fields.One2many(
        comodel_name="t4.gate_keeper.employee.biometric",
        inverse_name="employee_id",
        string="Biometrics",
    )

    auth_info_ids = fields.One2many(
        comodel_name="t4.gate_keeper.auth_info",
        inverse_name="employee_id",
        string="Auth Info (Cards)",
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
        tracking=True,
    )

    current_area_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area",
        string="Current Area",
        readonly=True,
        tracking=True,
    )


    active = fields.Boolean(string="Active", default=True, tracking=True)
    avatar = fields.Image(related="hr_employee_id.image_1920", string="Avatar", readonly=False)

    _sql_constraints = [
        ("emp_id_unique", "UNIQUE(emp_id)", "Employee ID must be unique."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        """Tạo hồ sơ nhân viên Gate Keeper và tự động sinh emp_id độc lập.

        Ưu tiên ir.sequence, fallback sang UUID nếu chưa có sequence được khai báo.
        emp_id là định danh riêng của GateKeeper, không liên quan hr.employee.
        """
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
        """Ngăn thay đổi emp_id sau khi đã tạo.

        emp_id là mã bất biến gắn với thiết bị sinh trắc học.
        Thay đổi sẽ phá vỡ liên kết phần cứng — không được phép.
        """
        if "emp_id" in vals:
            for record in self:
                if vals.get("emp_id") != record.emp_id:
                    raise ValidationError(_("Mã nhân viên (emp_id) không thể thay đổi sau khi tạo."))

        if any(field in vals for field in ["presence_state", "current_area_id"]):
            if not self.env.context.get("allow_employee_presence_write"):
                raise ValidationError(_("Không được phép tự ý thay đổi trạng thái hiện diện của nhân viên."))

        return super().write(vals)

    def _generate_emp_id(self):
        """Sinh emp_id dự phòng khi ir.sequence chưa được khai báo.

        Định dạng: GK-YYYYMMDDHHMMSS-XXXXXX
        Suffix ngẫu nhiên để tránh trùng khi bulk create trong cùng 1 giây.
        """
        # Fallback khi chưa khai báo ir.sequence cho model này.
        # Thêm suffix ngẫu nhiên để tránh trùng khi bulk create nhiều bản ghi trong cùng 1 giây
        # (ví dụ: cron_sync_missing_employees tạo hàng loạt).
        timestamp = fields.Datetime.now().strftime("%Y%m%d%H%M%S")
        suffix = uuid.uuid4().hex[:6].upper()
        return "GK-%s-%s" % (timestamp, suffix)
