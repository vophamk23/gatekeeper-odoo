# -*- coding: utf-8 -*-
# Mục đích: Quản lý danh mục model phần cứng và các thuật toán mà model đó hỗ trợ.

from odoo import models, fields


class GateKeeperDeviceModel(models.Model):
    _name = "t4.gate_keeper.device_model"
    _description = "Gate Keeper Device Model"
    _order = "name"

    name = fields.Char(
        string="Model Name",
        required=True,
        help="Specific model name or number of the hardware device, e.g., SpeedFace V5L.",
    )

    algorithm_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.algorithm",
        relation="t4_gate_keeper_device_model_algorithm_rel",
        column1="device_model_id",
        column2="algorithm_id",
        string="Supported Algorithms",
        help="Face, fingerprint, or other recognition algorithms supported by this model.",
    )
