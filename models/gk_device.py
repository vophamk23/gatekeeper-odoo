# -*- coding: utf-8 -*-
# Mục đích: Quản lý thiết bị đầu cuối vật lý (Device), trạng thái hoạt động và cảnh báo liên quan.

from odoo import api, _, fields, models

DEVICE_STATUS = [
    ("online", "Online"),
    ("offline", "Offline"),
    ("controller_offline", "Controller Offline"),
]


class GateKeeperDevice(models.Model):
    _name = "t4.gate_keeper.device"
    _description = "Gate Keeper Device"
    _order = "controller_id, id"

    name = fields.Char(
        string="Device Name",
        required=True,
        help="Human-readable name used to identify this device.",
    )

    controller_id = fields.Many2one(
        comodel_name="t4.gate_keeper.controller",
        string="Controller",
        required=True,
        ondelete="cascade",
        index=True,
        help="Controller that manages this device.",
    )

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        related="controller_id.branch_id",
        string="Branch",
        store=True,
        readonly=True,
    )

    timezone = fields.Selection(
        related="controller_id.branch_id.timezone",
        string="Timezone",
        readonly=True,
        store=True,
    )

    area_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area",
        string="Area",
        domain="[('branch_id', '=', branch_id)]",
        help="Area within the branch where this device is located.",
    )

    vendor = fields.Char(
        string="Vendor",
        help="Device manufacturer, for example ZKTeco, Hikvision, or Suprema.",
    )

    device_model_id = fields.Many2one(
        comodel_name="t4.gate_keeper.device_model",
        string="Device Model",
        help="Specific model name or number of the hardware device.",
    )

    serial_number = fields.Char(
        string="Serial Number",
        copy=False,
        index=True,
        help="Physical serial number of the device.",
    )

    port_or_channel = fields.Char(
        string="Port / Channel",
        help="Physical port or channel on the controller, for example relay 1 or input 2.",
    )

    firmware_version = fields.Char(
        string="Firmware Version",
        help="Firmware version installed on the device.",
    )

    system_version = fields.Char(
        string="System Version",
        help="Operating system or embedded application version installed on the device.",
    )

    algorithm_ids = fields.Many2many(
        related="device_model_id.algorithm_ids",
        readonly=True,
        string="Supported Algorithms",
        help="Face, fingerprint, or other recognition algorithms supported by this device.",
    )

    status = fields.Selection(
        selection=DEVICE_STATUS,
        string="Status",
        default="offline",
        tracking=True,
    )

    last_seen_at = fields.Datetime(
        string="Last Seen",
        readonly=True,
        help="Last time the controller received a response from this device.",
    )

    installed_at = fields.Date(
        string="Installed On",
    )

    last_sync_at = fields.Datetime(
        string="Last Sync",
        readonly=True,
        help="Last successful permission or template synchronization.",
    )

    employee_sync_status = fields.Selection(
        selection=[
            ("synced", "Synced"),
            ("out_of_sync", "Out of Sync"),
        ],
        string="Employee Sync Status",
        compute="_compute_employee_sync_status",
        help="Indicates whether the device has synchronized the latest employee updates.",
    )

    _sql_constraints = [
        (
            "controller_port_unique",
            "UNIQUE(controller_id, port_or_channel)",
            "Device port or channel must be unique per controller.",
        )
    ]

    def _compute_employee_sync_status(self):
        # TODO: Hoàn thiện logic kiểm tra trạng thái đồng bộ dữ liệu cho thiết bị
        for device in self:
            if device.last_sync_at:
                device.employee_sync_status = "synced"
            else:
                device.employee_sync_status = "out_of_sync"

    @api.model_create_multi
    def create(self, vals_list):
        # Không gọi _handle_device_issue_warning() ở đây: device mới tạo (mặc định
        # "offline" vì chưa từng kết nối) không được coi là một sự cố cần cảnh báo.
        # Warning chỉ nên phát sinh khi status THAY ĐỔI sau khi device đã hoạt động (xem write()).
        return super(GateKeeperDevice, self).create(vals_list)

    def write(self, vals):
        res = super(GateKeeperDevice, self).write(vals)
        if "status" in vals or "area_id" in vals:
            for record in self:
                if record.status in ("offline", "controller_offline"):
                    record._handle_device_issue_warning()
                elif record.status == "online":
                    record._resolve_device_issue_warnings()
        return res

    def _handle_device_issue_warning(self):
        self.ensure_one()
        if not self.area_id:
            self._resolve_device_issue_warnings()
            return

        warning_type = self.env["t4.gate_keeper.area_warning_type"].search(
            [("code", "=", "device_issue")], limit=1
        )
        if not warning_type:
            return

        active_warning = self.env["t4.gate_keeper.area_warning"].search(
            [
                ("device_id", "=", self.id),
                ("warning_type_id", "=", warning_type.id),
                ("state", "=", "warning"),
            ],
            limit=1,
        )

        if active_warning:
            if active_warning.area_id != self.area_id:
                active_warning.write({"area_id": self.area_id.id})
        else:
            status_label = dict(self._fields["status"].selection).get(
                self.status, self.status
            )
            self.env["t4.gate_keeper.area_warning"].create(
                {
                    "area_id": self.area_id.id,
                    "device_id": self.id,
                    "warning_type_id": warning_type.id,
                    "description": _("Device %s is offline. Status: %s")
                    % (self.name, status_label),
                }
            )

    def _resolve_device_issue_warnings(self):
        self.ensure_one()
        warning_type = self.env["t4.gate_keeper.area_warning_type"].search(
            [("code", "=", "device_issue")], limit=1
        )
        if not warning_type:
            return

        active_warnings = self.env["t4.gate_keeper.area_warning"].search(
            [
                ("device_id", "=", self.id),
                ("warning_type_id", "=", warning_type.id),
                ("state", "=", "warning"),
            ]
        )
        if active_warnings:
            active_warnings.action_resolve()
