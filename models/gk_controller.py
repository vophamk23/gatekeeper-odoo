# -*- coding: utf-8 -*-
# Mục đích: Quản lý thiết bị điều khiển vật lý (Controller), cài đặt kết nối, heartbeat và các API đồng bộ.

import logging

from odoo import api, _, fields, models
from odoo.addons.t4_coreapi.utils import endpoint, get_body
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

CONTROLLER_STATUS = [
    ("online", "Online"),
    ("offline", "Offline"),
    ("maintenance", "Maintenance"),
    ("disabled", "Disabled"),
]


class T4GateKeeperController(models.Model):
    _name = "t4.gate_keeper.controller"
    _description = "Gate Keeper Controller"
    _order = "last_heartbeat_at desc, id desc"

    name = fields.Char(
        string="Controller Name",
        required=True,
        help="Human-readable name used to identify this controller.",
    )

    serial_number = fields.Char(
        string="Serial Number",
        required=True,
        copy=False,
        index=True,
        help="Physical serial number used for maintenance and hardware replacement checks.",
    )

    branch_id = fields.Many2one(
        "t4.gate_keeper.branch",
        string="Branch",
        required=True,
        index=True,
    )

    timezone = fields.Selection(
        related="branch_id.timezone",
        string="Timezone",
        readonly=True,
        store=True,
    )

    device_ids = fields.One2many(
        "t4.gate_keeper.device",
        "controller_id",
        string="Devices",
    )

    hardware_model = fields.Char(
        string="Hardware Model",
        help="Controller model or product line.",
    )

    firmware_version = fields.Char(
        string="Firmware Version",
        help="Firmware version installed on the controller.",
    )

    ip_address = fields.Char(
        string="IP Address",
        help="Connection address when the controller uses TCP/IP.",
    )

    mac_address = fields.Char(
        string="MAC Address",
        help="Hardware identifier useful when DHCP changes the IP address.",
    )

    connection_type = fields.Selection(
        selection=[
            ("tcp_ip", "TCP/IP"),
            ("rs485", "RS485"),
            ("wiegand", "Wiegand"),
        ],
        string="Connection Type",
        required=True,
        default="tcp_ip",
        help="Communication method used by this controller.",
    )

    status = fields.Selection(
        selection=CONTROLLER_STATUS,
        string="Status",
        default="offline",
        tracking=True,
    )

    last_heartbeat_at = fields.Datetime(
        string="Last Heartbeat",
        readonly=True,
        help="Last time this controller reported that it was online.",
    )

    last_sync_at = fields.Datetime(
        string="Last Sync",
        readonly=True,
        help="Last successful permission or template synchronization.",
    )

    installed_at = fields.Date(
        string="Installed On",
        help="Installation date used for maintenance planning.",
    )

    employee_sync_status = fields.Selection(
        selection=[
            ("synced", "Synced"),
            ("out_of_sync", "Out of Sync"),
        ],
        string="Employee Sync Status",
        compute="_compute_employee_sync_status",
        help="Indicates whether the controller has synchronized the latest employee updates.",
    )

    _sql_constraints = [
        ("serial_number_unique", "UNIQUE(serial_number)", "Controller serial number must be unique.")
    ]

    def _compute_employee_sync_status(self):
        # TODO: Hoàn thiện logic tính trạng thái đồng bộ nhân viên dựa trên write_date của các bản ghi con
        for controller in self:
            domain = controller._get_employee_sync_domain(controller)
            unsynced_count = self.env["t4.gate_keeper.employee"].search_count(domain)
            if unsynced_count == 0:
                controller.employee_sync_status = "synced"
            else:
                controller.employee_sync_status = "out_of_sync"

    def _find_controller(self, serial_number):
        return self.search([
            ("serial_number", "=", serial_number),
        ], limit=1)

    @endpoint(name="ControllerHeartbeat")
    def controller_heartbeat(self):
        # TODO: Tái cấu trúc và tối ưu lại bước xác thực payload của endpoint heartbeat
        body = get_body(self.env)
        serial_number = body.get("serial_number", False)

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(f"Can not find controller with serial {serial_number}")

        heartbeat_at = fields.Datetime.now()
        controller.write({
            "last_heartbeat_at": heartbeat_at,
            "status": "online",
        })

    @endpoint(name="ControllerEmployeeSync")
    def controller_employee_sync(self):
        # TODO: Hoàn thiện việc lấy dữ liệu đồng bộ nhân viên dựa trên delta write_date
        body = get_body()
        serial_number = body.get("serial_number", False)

        if not serial_number:
            raise ValidationError(_("Serial number is required."))

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with serial %s") % serial_number)

        domain = self._get_employee_sync_domain(controller)
        employees = self._get_employees_to_sync(domain)

        current_time = fields.Datetime.now()
        
        if not employees:
            controller.write({
                "last_sync_at": current_time,
                "status": "online",
            })
            return {
                "message": _("Already up-to-date"),
                "data": []
            }
            
        data = []
        for emp in employees:
            data.append({
                "name": emp.name,
                "emp_id": emp.emp_id,
            })
            
        controller.write({
            "last_sync_at": current_time,
            "status": "online",
        })
        
        return data

    def write(self, vals):
        res = super(T4GateKeeperController, self).write(vals)
        if 'status' in vals:
            for controller in self:
                if controller.status == 'online':
                    devices_to_update = controller.device_ids.filtered(lambda d: d.status == 'controller_offline')
                    if devices_to_update:
                        devices_to_update.write({'status': 'online'})
                else:
                    devices_to_update = controller.device_ids.filtered(lambda d: d.status != 'controller_offline')
                    if devices_to_update:
                        devices_to_update.write({'status': 'controller_offline'})
        return res

    def _get_employee_sync_domain(self, controller):
        domain = [
            '|', 
            ('branch_id', '=', False), 
            ('branch_id', '=', controller.branch_id.id)
        ]
        
        if controller.last_sync_at:
            domain.append(('write_date', '>', controller.last_sync_at))
            
        return domain

    def _get_employees_to_sync(self, domain):
        return self.env["t4.gate_keeper.employee"].search(domain)
