# -*- coding: utf-8 -*-
# Mục đích: Quản lý thiết bị điều khiển vật lý (Controller), cài đặt kết nối, heartbeat và các API đồng bộ.

import logging

from odoo import api, _, fields, models
from odoo.addons.t4_coreapi.utils import endpoint, get_body, require_fields

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
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Gate Keeper Controller"
    _order = "last_heartbeat_at desc, id desc"

    name = fields.Char(
        string="Controller Name",
        required=True,
        tracking=True,
        help="Human-readable name used to identify this controller.",
    )

    serial_number = fields.Char(
        string="Serial Number",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help="Physical serial number used for maintenance and hardware replacement checks.",
    )

    branch_id = fields.Many2one(
        "t4.gate_keeper.branch",
        string="Branch",
        required=True,
        index=True,
        tracking=True,
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
        (
            "serial_number_unique",
            "UNIQUE(serial_number)",
            "Controller serial number must be unique.",
        )
    ]

    def _compute_employee_sync_status(self):
        """Tính trạng thái đồng bộ nhân viên cho controller.

        Logic: Nếu chưa sync lần nào hoặc có nhân viên mới/thay đổi
        sau last_sync_at → out_of_sync.
        """
        for controller in self:
            # ---> Gọi hàm: _get_employee_sync_domain() tại L251 trong file này (gk_controller.py)
            domain = controller._get_employee_sync_domain(controller)
            unsynced_count = self.env["t4.gate_keeper.employee"].search_count(domain)
            controller.employee_sync_status = (
                "out_of_sync" if unsynced_count else "synced"
            )

    def _find_controller(self, serial_number):
        return self.search(
            [
                ("serial_number", "=", serial_number),
            ],
            limit=1,
        )

    # Cấu hình API - ĐIỂM KHỞI ĐẦU LUỒNG HEARTBEAT (Gửi từ thiết bị phần cứng để duy trì kết nối)
    # Được gọi bởi: Thiết bị Controller gửi HTTP POST đến đường dẫn API: /api/ControllerHeartbeat
    @endpoint(name="ControllerHeartbeat")
    def controller_heartbeat(self):
        """Nhận heartbeat từ controller vàt cập nhật trạng thái online.

        Payload: { "serial_number": "<serial>" }
        """
        body = get_body()
        require_fields(body, ["serial_number"])
        serial_number = body.get("serial_number")

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy controller với serial: %s") % serial_number
            )

        # ---> Gọi hàm: write() tại L233 trong file này (gk_controller.py) để lưu trạng thái & cascade sang thiết bị
        controller.write(
            {
                "last_heartbeat_at": fields.Datetime.now(),
                "status": "online",
            }
        )

    # Cấu hình API - ĐIỂM KHỞI ĐẦU LUỒNG ĐỒNG BỘ NHÂN VIÊN (Thiết bị gọi để tải danh sách vân tay/khuôn mặt mới)
    # Được gọi bởi: Thiết bị Controller gửi HTTP POST đến đường dẫn API: /api/ControllerEmployeeSync
    @endpoint(name="ControllerEmployeeSync")
    def controller_employee_sync(self):
        """Trả về danh sách nhân viên cần đồng bộ (delta sync theo write_date).

        Payload: { "serial_number": "<serial>" }
        Response data: danh sách { emp_id, name, biometrics[] }
        """
        body = get_body()
        require_fields(body, ["serial_number"])
        serial_number = body.get("serial_number")

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy controller với serial: %s") % serial_number
            )

        # ---> Gọi hàm: _get_employee_sync_domain() tại L251 trong file này (gk_controller.py)
        domain = self._get_employee_sync_domain(controller)
        # ---> Gọi hàm: _get_employees_to_sync() tại L263 trong file này (gk_controller.py)
        employees = self._get_employees_to_sync(domain)

        current_time = fields.Datetime.now()

        if not employees:
            # ---> Gọi hàm: write() tại L233 trong file này (gk_controller.py)
            controller.write({"last_sync_at": current_time, "status": "online"})
            return {"message": _("Already up-to-date"), "data": []}

        data = []
        for emp in employees:
            # Lấy thông tin sinh trắc học của nhân viên
            biometrics = []
            for bio in emp.biometric_ids:
                biometrics.append(
                    {
                        "algorithm": bio.algorithm_id.name if bio.algorithm_id else "",
                        "algorithm_code": (
                            bio.algorithm_id.code if bio.algorithm_id else ""
                        ),
                        "template_data": bio.template.decode("utf-8") if isinstance(bio.template, bytes) else (bio.template or ""),
                    }
                )
            data.append(
                {
                    "emp_id": emp.emp_id,
                    "name": emp.name,
                    "biometrics": biometrics,
                }
            )

        # ---> Gọi hàm: write() ngay bên dưới trong file này (gk_controller.py)
        controller.write({"last_sync_at": current_time, "status": "online"})
        return {"message": _("%d nhân viên cần đồng bộ") % len(data), "data": data}

    # Cấu hình ghi đè hàm write để xử lý logic ghi log trạng thái
    def write(self, vals):
        res = super(T4GateKeeperController, self).write(vals)
        if "status" in vals:
            for controller in self:
                if controller.status == "online":
                    devices_to_update = controller.device_ids.filtered(
                        lambda d: d.status == "controller_offline"
                    )
                    if devices_to_update:
                        # ---> Chuyển sang: Gọi hàm write() trong file models/gk_device.py để cập nhật trạng thái thiết bị thành online và ghi log
                        devices_to_update.write({"status": "online"})
                else:
                    devices_to_update = controller.device_ids.filtered(
                        lambda d: d.status != "controller_offline"
                    )
                    if devices_to_update:
                        # ---> Chuyển sang: Gọi hàm write() trong file models/gk_device.py để cập nhật trạng thái thiết bị thành controller_offline và ghi log
                        devices_to_update.write({"status": "controller_offline"})
        return res

    # Cấu hình lấy danh sách nhân viên cần đồng bộ (chỉ nhân viên có cập nhật gần đây)
    # Được gọi bởi: Hàm controller_employee_sync() trong file models/gk_controller.py
    def _get_employee_sync_domain(self, controller):
        domain = [
            "|",
            ("branch_id", "=", False),
            ("branch_id", "=", controller.branch_id.id),
        ]

        if controller.last_sync_at:
            domain.append(("write_date", ">", controller.last_sync_at))

        return domain

    def _get_employees_to_sync(self, domain):
        return self.env["t4.gate_keeper.employee"].search(domain)

    # Cấu hình API - ĐIỂM KHỞI ĐẦU LUỒNG QUẸT THẺ (Gửi từ thiết bị phần cứng / Postman)
    # Được gọi bởi: Thiết bị Controller gửi HTTP POST đến đường dẫn API: /api/ControllerAccessLogUpload
    @endpoint(name="AccessLogUpload")
    def access_log_upload(self):
        """API nhận sự kiện quẹt thẻ từ thiết bị/controller và ghi nhận vào access log.

        Payload JSON:
        {
            "serial_number": "CTRL-123456",       # Serial của Controller
            "device_serial": "DEV-098765",       # Serial của Device trực thuộc
            "card_value": "EMP0001",              # Mã nhân viên (emp_id) hoặc mã thẻ RFID
            "direction": "in",                    # 'in' hoặc 'out' (mặc định: 'in')
            "verification_type": "card",          # 'card', 'fingerprint', 'face', 'password' (mặc định: 'card')
            "access_time": "2026-07-08 08:30:00"  # Thời gian quẹt (định dạng YYYY-MM-DD HH:MM:SS, tùy chọn)
        }
        """
        body = get_body()
        require_fields(body, ["serial_number", "device_serial", "card_value"])

        serial_number = body.get("serial_number")
        device_serial = body.get("device_serial")
        card_value = body.get("card_value")
        v_type = body.get("verification_type") or "card"

        # 1. Tra cứu Controller
        # ---> Gọi hàm: _find_controller() tại L147 trong file này (gk_controller.py)
        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy Controller với serial: %s") % serial_number
            )

        # 2. Tìm Thiết bị thuộc Controller này
        # ---> Tra cứu thiết bị trong file models/gk_device.py để liên kết log với vị trí vật lý
        device = self.env["t4.gate_keeper.device"].search(
            [
                ("serial_number", "=", device_serial),
                ("controller_id", "=", controller.id),
            ],
            limit=1,
        )
        if not device:
            raise ValidationError(
                _("Không tìm thấy Thiết bị với serial %s thuộc Controller %s")
                % (device_serial, serial_number)
            )

        # 3. Xác thực thẻ RFID hoặc Sinh trắc học để tìm Nhân viên
        # - Nếu verification_type là 'card' -> Tìm trong t4.gate_keeper.auth_info
        # - Nếu là 'fingerprint' hoặc 'face' -> Tìm trong t4.gate_keeper.employee.biometric
        employee = self.env["t4.gate_keeper.employee"]

        if v_type == "card":
            # Tra cứu mã thẻ RFID trong bảng thông tin xác thực
            # ---> Tra cứu thẻ trong file models/gk_auth_info.py để lấy hồ sơ nhân viên sở hữu thẻ
            auth_info = self.env["t4.gate_keeper.auth_info"].search(
                [("card_code", "=", card_value), ("active", "=", True)], limit=1
            )
            if auth_info:
                employee = auth_info.employee_id
        elif v_type in ("fingerprint", "face"):
            # Tìm nhân viên theo emp_id
            # ---> Tra cứu nhân viên trong file models/gk_employee.py theo mã ID
            emp = self.env["t4.gate_keeper.employee"].search(
                [("emp_id", "=", card_value), ("active", "=", True)], limit=1
            )
            if emp:
                # Kiểm tra nhân viên này đã đăng ký sinh trắc học tương ứng chưa
                # biometric_type liên quan đến algorithm_id.algorithm_type
                # ---> Tra cứu thông tin sinh trắc học trong file models/gk_employee_biometric.py để xác thực mẫu đã đăng ký
                biometric = self.env["t4.gate_keeper.employee.biometric"].search(
                    [("employee_id", "=", emp.id), ("biometric_type", "=", v_type)],
                    limit=1,
                )
                if biometric:
                    employee = emp
        elif v_type in ("password", "other"):
            # Tìm nhân viên theo emp_id cho kiểu xác thực mật khẩu hoặc khác
            emp = self.env["t4.gate_keeper.employee"].search(
                [("emp_id", "=", card_value), ("active", "=", True)], limit=1
            )
            if emp:
                employee = emp

        # 4. Ghi nhận lượt quẹt thẻ (Nếu employee rỗng -> log sẽ kích hoạt cảnh báo Thẻ lạ)
        log_vals = {
            "controller_id": controller.id,
            "device_id": device.id,
            "employee_id": employee.id if employee else False,
            "direction": body.get("direction") or "in",
            "verification_type": v_type,
        }
        if body.get("access_time"):
            log_vals["access_time"] = body.get("access_time")

        # Tạo bản ghi log (sẽ kích hoạt các rule kiểm tra an ninh tự động)
        # Gọi hàm create() trong file models/gk_access_log.py
        log = self.env["t4.gate_keeper.access_log"].create(log_vals)

        # Trả về kết quả JSON phản hồi
        return {
            "message": _("Ghi nhận lượt quẹt thẻ thành công"),
            "data": {
                "log_id": log.id,
                "employee_name": (
                    employee.name
                    if employee
                    else _("Unknown/Unregistered Card or Biometrics")
                ),
                "device_name": device.name,
                "has_warning": bool(
                    self.env["t4.gate_keeper.area_warning"].search(
                        [("access_log_id", "=", log.id)]
                    )
                ),
            },
        }
