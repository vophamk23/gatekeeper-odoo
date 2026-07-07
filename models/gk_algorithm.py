# -*- coding: utf-8 -*-
# Mục đích: Quản lý các thuật toán nhận diện sinh trắc học (vân tay, kữún mặt, thẻ, v.v.).

from odoo import models, fields, api, _

ALGORITHM_TYPES = [
    ("face", "Face Recognition"),
    ("fingerprint", "Fingerprint Recognition"),
    ("card", "Card Recognition"),
    ("other", "Other"),
]


class GateKeeperAlgorithm(models.Model):
    _name = "t4.gate_keeper.algorithm"
    _description = "Gate Keeper Algorithm"
    _order = "algorithm_type, name, version"

    name = fields.Char(
        string="Algorithm Name",
        required=True,
        help="Commercial or technical name of the recognition algorithm.",
    )

    algorithm_type = fields.Selection(
        selection=ALGORITHM_TYPES,
        string="Algorithm Type",
        required=True,
        default="other",
    )

    version = fields.Char(
        string="Algorithm Version",
        required=True,
        help="Version of this recognition algorithm.",
    )

    template_format = fields.Char(
        string="Template Format",
        help="Biometric template format produced or consumed by this algorithm.",
    )

    notes = fields.Text(
        string="Notes",
    )

    _sql_constraints = [
        (
            "algorithm_version_unique",
            "UNIQUE(name, algorithm_type, version)",
            "Algorithm version must be unique per name, type and version."
        )
    ]
