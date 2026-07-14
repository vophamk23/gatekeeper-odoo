# -*- coding: utf-8 -*-
# Mục đích: Quản lý thiết bị điều khiển vật lý (Controller), cài đặt kết nối, heartbeat và các API đồng bộ.

import logging
import base64

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

    _serial_number_unique = models.Constraint(
        "unique(serial_number)",
        "Controller serial number must be unique.",
    )

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

    # Cấu hình ghi đè hàm write để xử lý logic ghi log trạng thái
    def write(self, vals):
        res = super(T4GateKeeperController, self).write(vals)
        if "status" in vals:
            for controller in self:
                if controller.status == "online":
                    # Nếu Controller online trở lại, tự động phục hồi trạng thái cho các thiết bị con
                    devices_to_update = controller.device_ids.filtered(
                        lambda d: d.status == "controller_offline"
                    )
                    if devices_to_update:
                        # ---> Chuyển sang: Gọi hàm write() trong file models/gk_device.py để cập nhật trạng thái thiết bị thành online và ghi log
                        devices_to_update.write({"status": "online"})
                else:
                    # Nếu Controller mất kết nối, tự động chuyển các thiết bị con sang trạng thái mất kết nối theo Controller
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

    # ----------------------------------------------------
    # API 1: ControllerRegister (Đăng ký Controller)
    # ----------------------------------------------------
    @endpoint(name="ControllerRegister")
    def controller_register(self):
        """API nhận thông tin đăng ký phần cứng từ Controller vật lý khi khởi động.

        - Input: serial_number (bắt buộc), branch_code (bắt buộc), hardware_model,
                 firmware_version, ip_address, mac_address, connection_type, installed_at.
        - Logic: Tìm Controller theo serial_number.
                 Nếu chưa tồn tại: tạo mới, tìm Branch theo tên branch_code.
                 Nếu đã tồn tại: cập nhật thông tin phần cứng.
                 Chuyển status sang online, cập nhật last_heartbeat_at.
        - Output: controller id cùng thông báo đăng ký thành công.
        """
        body = get_body()
        require_fields(body, ["serial_number", "branch_code"])
        serial_number = body.get("serial_number")
        branch_code = body.get("branch_code")

        # Tìm Branch theo tên (branch_code map với Branch name)
        branch = self.env["t4.gate_keeper.branch"].search(
            [("name", "ilike", branch_code)], limit=1
        )
        if not branch:
            raise ValidationError(
                _("Không tìm thấy Branch với mã: %s") % branch_code
            )

        # Tìm Controller theo serial_number
        controller = self._find_controller(serial_number)

        write_vals = {
            "hardware_model": body.get("hardware_model"),
            "firmware_version": body.get("firmware_version"),
            "ip_address": body.get("ip_address"),
            "mac_address": body.get("mac_address"),
            "connection_type": body.get("connection_type") or "tcp_ip",
            "status": "online",
            "last_heartbeat_at": fields.Datetime.now(),
        }
        if body.get("installed_at"):
            write_vals["installed_at"] = body.get("installed_at")

        if controller:
            # Controller đã tồn tại: chỉ cập nhật thông tin phần cứng
            controller.write(write_vals)
        else:
            # Controller chưa tồn tại: tạo mới
            write_vals.update({
                "name": body.get("name") or serial_number,
                "serial_number": serial_number,
                "branch_id": branch.id,
            })
            controller = self.create(write_vals)

        return {
            "message": "Controller registered successfully",
            "data": {
                "id": controller.id,
            },
        }

    # ----------------------------------------------------
    # API 2: DeviceRegister (Đăng ký Device con)
    # ----------------------------------------------------
    @endpoint(name="DeviceRegister")
    def device_register(self):
        """API nhận thông tin đăng ký thiết bị đầu cuối vật lý (Device con).

        - Input: serial_number (device_sn), port_or_channel, firmware_version, system_version.
        - Logic: Tìm Device con theo device_sn, cập nhật kênh/cổng, phiên bản firmware,
                 chuyển status sang online.
        - Output: Trạng thái 200 OK cùng ID/tên thiết bị và tên Controller cha.
        """
        body = get_body()
        require_fields(body, ["device_sn"])
        device_sn = body.get("device_sn")

        # Tìm thiết bị đầu cuối vật lý theo số Serial Number
        device = self.env["t4.gate_keeper.device"].search(
            [("serial_number", "=", device_sn)], limit=1
        )
        if not device:
            raise ValidationError(
                _("Không tìm thấy Device con với serial: %s") % device_sn
            )

        device.write(
            {
                "port_or_channel": body.get("port/channel")
                or body.get("port_or_channel"),
                "firmware_version": body.get("firmware_version"),
                "system_version": body.get("system_version"),
                "status": "online",
            }
        )

        return {
            "message": "Success",
            "data": {
                "status": "200 OK",
                "device_id": device.id,
                "controller_name": device.controller_id.name,
                "device_name": device.name,
            },
        }

    # ----------------------------------------------------
    # API 3: ControllerGetConfig (Tải cấu hình Controller)
    # ----------------------------------------------------
    @endpoint(name="ControllerGetConfig")
    def controller_get_config(self):
        """API tải thông số cấu hình và danh sách đầu đọc vật lý của Controller.

        - Input: serial_number.
        - Logic: Tìm Controller, duyệt danh sách Device con để lấy thông tin cổng, serial và
                 danh sách các thuật toán sinh trắc học được hỗ trợ.
        - Output: Múi giờ của Controller và danh sách các Devices con cùng thuật toán tương ứng.
        """
        # Nhận dữ liệu request, bắt buộc có serial_number (mã thiết bị)
        body = get_body()
        require_fields(body, ["serial_number"])
        serial = body.get("serial_number")

        controller = self._find_controller(serial)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy Controller với serial: %s") % serial
            )

        devices_data = []
        # Duyệt danh sách các thiết bị con được gán cho Controller này
        for dev in controller.device_ids:
            algos = []
            for algo in dev.algorithm_ids:
                algos.append(
                    {
                        "name": algo.name,
                        "type": algo.algorithm_type,
                        "version": algo.version or "1.0",
                    }
                )
            devices_data.append(
                {
                    "device_id": dev.id,
                    "name": dev.name,
                    "serial_number": dev.serial_number,
                    "port_or_channel": dev.port_or_channel,
                    "supported_algorithms": algos,
                }
            )

        return {
            "message": "Success",
            "data": {
                "status": "200 OK",
                "timezone": controller.timezone or "Asia/Ho_Chi_Minh",
                "devices": devices_data,
            },
        }

    # ----------------------------------------------------
    # API 4: ControllerHeartbeat (Heartbeat của Controller)
    # ----------------------------------------------------
    @endpoint(name="ControllerHeartbeat")
    def controller_heartbeat(self):
        """API nhận nhịp tim định kỳ và cập nhật trạng thái kết nối các thiết bị.

        - Input: controller_sn, devices_status (danh sách trạng thái online/offline của từng device_sn).
        - Logic: Cập nhật status của Controller thành online, ghi nhận last_heartbeat_at.
                 Duyệt qua từng device_sn để cập nhật status tương ứng.
        - Output: Trạng thái 200 OK.
        """
        body = get_body()
        require_fields(body, ["controller_sn"])
        controller_sn = body.get("controller_sn")
        devices_status = body.get("devices_status", [])

        controller = self._find_controller(controller_sn)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy Controller với serial: %s") % controller_sn
            )

        # Cập nhật trạng thái Controller thành online và ghi nhận thời gian nhận heartbeat
        controller.write(
            {
                "status": "online",
                "last_heartbeat_at": fields.Datetime.now(),
            }
        )

        # Cập nhật trạng thái hoạt động của từng thiết bị con từ phần cứng báo cáo lên
        for dev_info in devices_status:
            dev_sn = dev_info.get("device_sn")
            status = dev_info.get("status")
            if dev_sn and status:
                device = self.env["t4.gate_keeper.device"].search(
                    [
                        ("serial_number", "=", dev_sn),
                        ("controller_id", "=", controller.id),
                    ],
                    limit=1,
                )
                if device:
                    device.write({"status": status})

        return {
            "message": "Success",
            "status": "200 OK",
        }

    # ----------------------------------------------------
    # API 5: ControllerEmployeeSync (Đồng bộ danh sách nhân sự)
    # ----------------------------------------------------
    @endpoint(name="ControllerEmployeeSync")
    def controller_employee_sync(self):
        """API lấy danh sách thay đổi nhân sự (delta sync) để thêm/sửa/xóa trên thiết bị.

        - Input: controller_sn (serial number của Controller).
        - Logic:
            + Nếu chưa sync lần nào: tất cả nhân viên active thuộc branch → "new".
            + Nếu đã sync trước đó:
                * Nhân viên mới tạo sau last_sync_at → "new".
                * Nhân viên cập nhật sau last_sync_at và còn active → "update".
                * Nhân viên inactive hoặc không thuộc branch sau last_sync_at → "deleted".
        - Output: danh sách new/update/deleted với id, name, branch_id.
        """
        body = get_body()
        require_fields(body, ["controller_sn"])
        controller_sn = body.get("controller_sn")

        controller = self._find_controller(controller_sn)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy Controller với serial: %s") % controller_sn
            )

        last_sync = controller.last_sync_at

        # Helper: chuyển employee thành dict response
        def _emp_dict(emp):
            return {
                "id": emp.id,
                "name": emp.name,
                "branch_id": emp.branch_id.id if emp.branch_id else False,
            }

        # Helper: nhân viên thuộc branch của controller (hoặc không giới hạn branch)
        def _belongs_to_branch(emp):
            return not emp.branch_id or emp.branch_id.id == controller.branch_id.id

        new_list = []
        update_list = []
        deleted_list = []

        if not last_sync:
            # Lần đầu sync: tất cả nhân viên active thuộc branch → "new"
            employees = self.env["t4.gate_keeper.employee"].search([])
            for emp in employees:
                if _belongs_to_branch(emp):
                    new_list.append(_emp_dict(emp))
        else:
            # Delta sync: chỉ lấy nhân viên có thay đổi kể từ last_sync
            employees = (
                self.env["t4.gate_keeper.employee"]
                .with_context(active_test=False)
                .search([("write_date", ">", last_sync)])
            )
            for emp in employees:
                belongs = _belongs_to_branch(emp)
                if not emp.active or not belongs:
                    deleted_list.append(_emp_dict(emp))
                elif emp.create_date > last_sync:
                    new_list.append(_emp_dict(emp))
                else:
                    update_list.append(_emp_dict(emp))

        return {
            "message": "Employee Sync Completed",
            "data": [{
                "new": new_list,
                "update": update_list,
                "deleted": deleted_list,
            }],
        }

    # ----------------------------------------------------
    # API 6: ControllerEmployeeSyncStatus (Kiểm tra trạng thái đồng bộ nhân sự)
    # ----------------------------------------------------
    @endpoint(name="ControllerEmployeeSyncStatus")
    def controller_employee_sync_status(self):
        """API kiểm tra controller có cần đồng bộ nhân sự hay không.

        - Input: controller_sn (serial number của Controller).
        - Logic: Tìm Controller, kiểm tra employee_sync_status.
        - Output: {"update": True} nếu cần sync, {"update": False} nếu đã sync đủ.
        """
        body = get_body()
        require_fields(body, ["controller_sn"])
        controller_sn = body.get("controller_sn")

        controller = self._find_controller(controller_sn)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy Controller với serial: %s") % controller_sn
            )

        needs_update = controller.employee_sync_status == "out_of_sync"

        return {
            "message": "Success",
            "data": {
                "update": needs_update,
            },
        }

    # ----------------------------------------------------
    # API 7: EmployeeBiometricGet (Tải dữ liệu mẫu sinh trắc học Base64)
    # ----------------------------------------------------
    @endpoint(name="EmployeeBiometricGet")
    def get_biometric(self):
        """API tải mã thẻ RFID và mẫu sinh trắc học Base64 của nhân viên cụ thể.

        - Input: controller_id, emp_id.
        - Logic:
            + Tìm Controller và Nhân viên. Kiểm tra ràng buộc chi nhánh.
            + Tìm các mẫu sinh trắc học (biometrics) của nhân viên khớp với các thuật toán
              mà thiết bị con của Controller này hỗ trợ.
            + Lấy danh sách mã thẻ RFID đang hoạt động.
            + Encode các mẫu template sinh trắc học sang định dạng Base64.
        - Output: emp_id, tên nhân viên, danh sách mã thẻ và các mẫu sinh trắc học kèm thông tin thuật toán.
        """
        body = get_body()
        require_fields(body, ["controller_id", "emp_id"])
        controller_id = body.get("controller_id")
        emp_id = body.get("emp_id")

        controller = self._find_controller(controller_id)
        employee = self.env["t4.gate_keeper.employee"].search(
            [("emp_id", "=", emp_id)], limit=1
        )

        if not controller or not employee:
            raise ValidationError(_("Không tìm thấy Controller hoặc Nhân viên hợp lệ"))

        # Ràng buộc bảo mật chi nhánh: Nhân viên phải thuộc cùng chi nhánh với Controller hoặc là nhân viên dùng chung (không có branch_id)
        if (
            employee.branch_id
            and controller.branch_id
            and employee.branch_id.id != controller.branch_id.id
        ):
            raise ValidationError(
                _("Nhân viên không thuộc chi nhánh của bộ điều khiển này")
            )

        # Lấy ID của các thuật toán sinh trắc học mà các đầu đọc con của Controller này hỗ trợ
        supported_algos = controller.device_ids.mapped(
            "device_model_id.algorithm_ids.id"
        )
        biometrics = self.env["t4.gate_keeper.employee.biometric"].search(
            [("employee_id", "=", employee.id), ("algorithm_id", "in", supported_algos)]
        )

        cards = employee.auth_info_ids.filtered(lambda a: a.active).mapped("card_code")

        templates = []
        for bio in biometrics:
            templates.append(
                {
                    "biometric_type": bio.biometric_type,
                    "finger_index": bio.finger_index or 0,
                    "algorithm_name": bio.algorithm_id.name if bio.algorithm_id else "",
                    "algorithm_version": bio.algorithm_id.version or "1.0",
                    # Mã hóa dữ liệu nhị phân sinh trắc học sang dạng chuỗi Base64 để truyền tải qua API
                    "template": (
                        base64.b64encode(bio.template).decode("utf-8")
                        if bio.template
                        else ""
                    ),
                }
            )

        return {
            "message": "Success",
            "data": {
                "status": "200 OK",
                "emp_id": employee.emp_id,
                "name": employee.name,
                "cards": cards,
                "biometrics": templates,
            },
        }

    # ----------------------------------------------------
    # API 8: ControllerSyncAck (Xác nhận hoàn thành đồng bộ)
    # ----------------------------------------------------
    @endpoint(name="ControllerSyncAck")
    def sync_ack(self):
        """API nhận xác nhận nạp dữ liệu thành công từ thiết bị.

        - Input: controller_id, sync_timestamp.
        - Logic: Tìm Controller và cập nhật thời điểm đồng bộ cuối cùng `last_sync_at` thành
                 sync_timestamp (hoặc thời gian hiện tại nếu rỗng).
        - Output: Trạng thái 200 OK.
        """
        # Nhận dữ liệu request, bắt buộc có controller_id
        body = get_body()
        require_fields(body, ["controller_id"])
        controller_id = body.get("controller_id")
        sync_time_str = body.get("sync_timestamp")

        controller = self._find_controller(controller_id)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy Controller với serial: %s") % controller_id
            )

        sync_time = (
            fields.Datetime.from_string(sync_time_str)
            if sync_time_str
            else fields.Datetime.now()
        )
        controller.write(
            {
                "last_sync_at": sync_time,
            }
        )

        return {
            "message": "Success",
            "data": {
                "status": "200 OK",
            },
        }

    # ----------------------------------------------------
    # API 9: AccessLogUpload (Tiếp nhận lô quẹt thẻ offline)
    # ----------------------------------------------------
    @endpoint(name="AccessLogUpload")
    def upload_logs(self):
        """API nhận tải lên theo lô các sự kiện quẹt thẻ thực tế của nhân viên.

        - Input: controller_id, logs (mảng các log gồm device_serial, emp_id, card_code, direction,
                 verification_type, access_time).
        - Logic:
            + Tìm Controller, chuyển status thành online và cập nhật last_heartbeat_at.
            + Sắp xếp logs theo thời gian tăng dần để xử lý tuần tự.
            + Với mỗi log: Tìm Device con. Tìm Employee bằng emp_id hoặc card_code.
            + Tạo bản ghi log `t4.gate_keeper.access_log` tương ứng với thông tin nhận được.
        - Output: Số lượng log đã được xử lý thành công.
        """
        body = get_body()
        require_fields(body, ["controller_id", "logs"])
        controller_id = body.get("controller_id")
        logs = body.get("logs", [])

        controller = self._find_controller(controller_id)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy Controller với serial: %s") % controller_id
            )

        controller.write(
            {
                "status": "online",
                "last_heartbeat_at": fields.Datetime.now(),
            }
        )

        # Sắp xếp các sự kiện quẹt thẻ theo thời gian tăng dần trước khi ghi nhận
        # Việc này cực kỳ quan trọng để trạng thái hiện diện (presence_state) của nhân viên được cập nhật đúng thứ tự
        sorted_logs = sorted(logs, key=lambda x: x.get("access_time") or "")
        created_count = 0

        for log_data in sorted_logs:
            device = self.env["t4.gate_keeper.device"].search(
                [
                    ("serial_number", "=", log_data.get("device_serial")),
                    ("controller_id", "=", controller.id),
                ],
                limit=1,
            )

            employee = self.env["t4.gate_keeper.employee"]
            emp_id = log_data.get("emp_id")
            card_code = log_data.get("card_code")

            # Xác định nhân viên:
            # - Trường hợp Vân tay/Khuôn mặt (thiết bị tự đối khớp offline thành công): Thiết bị sẽ gửi thẳng emp_id
            if emp_id:
                employee = self.env["t4.gate_keeper.employee"].search(
                    [("emp_id", "=", emp_id)], limit=1
                )
            # - Trường hợp Thẻ từ (card): Thiết bị chỉ gửi mã thẻ thô, hệ thống cần tra cứu xem thẻ đang gán cho ai
            elif card_code and log_data.get("verification_type") == "card":
                auth_info = self.env["t4.gate_keeper.auth_info"].search(
                    [("card_code", "=", card_code), ("active", "=", True)], limit=1
                )
                if auth_info:
                    employee = auth_info.employee_id

            if device:
                log_vals = {
                    "device_id": device.id,
                    "employee_id": employee.id if employee else False,
                    "card_code": card_code or "",
                    "direction": log_data.get("direction") or "in",
                    "verification_type": log_data.get("verification_type") or "card",
                    "sync_status": "success",
                }
                if log_data.get("access_time"):
                    log_vals["access_time"] = fields.Datetime.from_string(
                        log_data.get("access_time")
                    )

                # Tạo bản ghi log sự kiện quẹt thẻ. Bước này sẽ tự động kích hoạt Rule Engine kiểm tra cảnh báo vùng (Area Warning)
                self.env["t4.gate_keeper.access_log"].create(log_vals)
                created_count += 1

        return {
            "message": "Success",
            "data": {
                "status": "200 OK",
                "processed_count": created_count,
            },
        }

    # ----------------------------------------------------
    # API 10: ControllerCommandPoll (Quét lệnh điều khiển từ xa)
    # ----------------------------------------------------
    @endpoint(name="ControllerCommandPoll")
    def command_poll(self):
        """API phục vụ cơ chế Pull-based: Controller quét tìm lệnh điều khiển từ xa.

        - Input: controller_id.
        - Logic: Tìm các lệnh `t4.gate_keeper.command` đang ở trạng thái `pending` dành cho Controller này.
                 Chuyển trạng thái các lệnh thành `sending`.
        - Output: Danh sách các lệnh cần thực thi (command_id, action_type, device_serial, parameters).
        """
        # Nhận dữ liệu request, bắt buộc có controller_id
        body = get_body()
        require_fields(body, ["controller_id"])
        controller_id = body.get("controller_id")

        controller = self._find_controller(controller_id)
        if not controller:
            raise ValidationError(
                _("Không tìm thấy Controller với serial: %s") % controller_id
            )

        # Tìm các lệnh điều khiển từ xa đang ở trạng thái chờ gửi (pending)
        commands = self.env["t4.gate_keeper.command"].search(
            [
                ("controller_id", "=", controller.id),
                ("state", "=", "pending"),
            ]
        )

        res = []
        for cmd in commands:
            # Chuyển trạng thái sang sending để đánh dấu lệnh đang được gửi đi, tránh gửi trùng lặp
            cmd.write({"state": "sending"})
            res.append(
                {
                    "command_id": cmd.id,
                    "action": cmd.action_type,
                    "device_serial": (
                        cmd.device_id.serial_number if cmd.device_id else ""
                    ),
                    "parameters": cmd.parameters or "",
                }
            )

        return {
            "message": "Success",
            "data": {
                "status": "200 OK",
                "commands": res,
            },
        }

    # ----------------------------------------------------
    # API 11: ControllerCommandAck (Báo cáo kết quả thực thi lệnh)
    # ----------------------------------------------------
    @endpoint(name="ControllerCommandAck")
    def command_ack(self):
        """API nhận báo cáo kết quả thực thi lệnh mở cửa từ xa gửi từ rơ-le thiết bị.

        - Input: controller_id, command_id, execution_message.
        - Logic: Tìm lệnh theo command_id. Cập nhật state thành `success` hoặc `failed` dựa trên
                 nội dung execution_message, cập nhật thông báo thực thi.
        - Output: Trạng thái 200 OK.
        """
        body = get_body()
        require_fields(body, ["controller_id", "command_id"])
        command_id = body.get("command_id")
        msg = body.get("execution_message")

        command = self.env["t4.gate_keeper.command"].browse(command_id)
        if not command.exists():
            raise ValidationError(
                _("Không tìm thấy Lệnh điều khiển với ID: %s") % command_id
            )

        # Cập nhật kết quả thực thi lệnh dựa trên thông điệp trả về từ phần cứng
        command.write(
            {
                "state": (
                    "success" if not msg or "error" not in msg.lower() else "failed"
                ),
                "execution_message": msg or "Executed successfully.",
            }
        )

        return {
            "message": "Success",
            "data": {
                "status": "200 OK",
            },
        }
