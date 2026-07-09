# -*- coding: utf-8 -*-
# Mục đích: Quản lý các chi nhánh (vị trí vật lý) và múi giờ tương ứng.

try:
    import pytz
    TIMEZONE_SELECTION = [(tz, tz) for tz in sorted(pytz.common_timezones)]
except ImportError:
    TIMEZONE_SELECTION = [("Asia/Ho_Chi_Minh", "Asia/Ho_Chi_Minh")]

from odoo import api, fields, models


class GateKeeperBranch(models.Model):
    _name = "t4.gate_keeper.branch"
    _description = "Gate Keeper Branch"
    _order = "name"

    name = fields.Char(
        string="Branch Name",
        required=True,
        help="Name of the branch or physical site.",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
        help="Company that owns this branch.",
    )

    timezone = fields.Selection(
        selection=TIMEZONE_SELECTION,
        string="Timezone",
        default="Asia/Ho_Chi_Minh",
        required=True,
        help="Timezone used for branch-level time evaluation.",
    )

    address = fields.Text(
        string="Address",
        help="Physical address of the branch.",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    area_ids = fields.One2many(
        comodel_name="t4.gate_keeper.area",
        inverse_name="branch_id",
        string="Areas",
    )

    controller_ids = fields.One2many(
        comodel_name="t4.gate_keeper.controller",
        inverse_name="branch_id",
        string="Controllers",
    )

    device_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.device",
        string="Devices",
        compute="_compute_device_ids",
    )

    @api.depends("controller_ids", "controller_ids.device_ids")
    def _compute_device_ids(self):
        """Tính tập hợp thiết bị thuộc chi nhánh thông qua các controller.

        Làm phẳng quan hệ Branch → Controller → Device thành một Many2many
        để hiển thị nhanh và lọc dữ liệu theo chi nhánh.
        """
        for branch in self:
            branch.device_ids = branch.controller_ids.device_ids
