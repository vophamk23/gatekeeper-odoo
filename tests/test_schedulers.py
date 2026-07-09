# -*- coding: utf-8 -*-
# Mục đích: Kiểm thử các tác vụ nền chạy ngầm định kỳ (cron jobs) phục vụ quản lý thiết bị và cảnh báo tại chi nhánh công ty.
# Chủ đề: Hệ thống tác vụ tự động tại chi nhánh doanh nghiệp (Automated Office Branch Operations).
# Nội dung bao gồm:
#   - Tác vụ tự động quét kết nối (Heartbeat Watchdog) phát hiện thiết bị/bộ điều khiển chi nhánh bị mất kết nối quá 5 phút.
#   - Tác vụ tự động đồng bộ hồ sơ nhân sự mới tuyển dụng từ phân hệ HR gốc sang phân hệ Gate Keeper của chi nhánh.
#   - Tác vụ tự động leo thang mức độ ưu tiên của cảnh báo (escalate warning) khi cảnh báo bị tồn đọng chưa xử lý.
#   - Tác vụ tự động kiểm tra thời gian làm việc quá giờ (Overtime Check) của nhân viên tại văn phòng chi nhánh công ty.

from odoo.tests import common
from odoo.fields import Datetime
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestSchedulers(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestSchedulers, cls).setUpClass()

        # 1. Khởi tạo Chi nhánh công ty mẫu (Company Branch)
        cls.branch = cls.env["t4.gate_keeper.branch"].create({
            "name": "Chi nhánh Đà Nẵng - Công ty Tech",
            "timezone": "Asia/Ho_Chi_Minh",
        })

        # 2. Khởi tạo Khu vực kho hàng của chi nhánh (Office Branch Warehouse Area)
        cls.area = cls.env["t4.gate_keeper.area"].create({
            "name": "Khu Vực Kho Chi Nhánh Đà Nẵng",
            "branch_id": cls.branch.id,
        })

        # 3. Khởi tạo Bộ điều khiển cửa Kho hàng (Controller)
        cls.controller = cls.env["t4.gate_keeper.controller"].create({
            "name": "Bộ điều khiển cửa Kho Đà Nẵng",
            "serial_number": "CTRL-OFFICE-002",
            "branch_id": cls.branch.id,
            "status": "online",
        })

        # 4. Khởi tạo Thiết bị đầu đọc thẻ gắn tại Kho hàng (Device)
        cls.device = cls.env["t4.gate_keeper.device"].create({
            "name": "Đầu đọc thẻ RFID cửa Kho",
            "controller_id": cls.controller.id,
            "area_id": cls.area.id,
            "serial_number": "DEV-READER-002",
            "status": "online",
        })

        # 5. Khởi tạo Nhân sự mẫu ở phân hệ HR gốc (Odoo HR Employee)
        cls.hr_employee = cls.env["hr.employee"].create({
            "name": "Trần Văn Nhân Viên",
        })

        # 6. Khởi tạo Hồ sơ liên kết nhân sự tại phân hệ Gate Keeper
        cls.employee = cls.env["t4.gate_keeper.employee"].create({
            "name": "Trần Văn Nhân Viên",
            "hr_employee_id": cls.hr_employee.id,
            "branch_id": cls.branch.id,
        })

        # 7. Tìm loại cảnh báo Overtime (Làm việc quá giờ cấm) mặc định từ hệ thống
        cls.warning_type_overtime = cls.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "overtime")], limit=1)

    def test_01_cron_update_hardware_status(self):
        """Hàm kiểm thử: Tác vụ tự động quét trạng thái thiết bị ngoại vi tại văn phòng (Hardware Status Watchdog).
        Mục đích: Đảm bảo tự động chuyển trạng thái Bộ điều khiển sang 'offline' và Đầu đọc thẻ sang 'controller_offline'
                  khi không nhận được tín hiệu heartbeat/last seen quá 5 phút. Đồng thời tự động phát sinh cảnh báo lỗi thiết bị (device_issue).
        """
        # Bước 1: Giả lập thời gian nhận tín hiệu cuối cùng cách đây 10 phút (vượt quá 5 phút timeout cho phép)
        timeout_time = Datetime.now() - timedelta(minutes=10)
        self.controller.write({
            "last_heartbeat_at": timeout_time,
        })
        self.device.write({
            "last_seen_at": timeout_time,
        })

        # Bước 2: Kích hoạt tác vụ chạy định kỳ quét trạng thái phần cứng
        self.env["t4.gate_keeper.scheduler"].cron_update_hardware_status()

        # Xác thực 1: Bộ điều khiển phải chuyển sang trạng thái offline và Thiết bị con chuyển sang controller_offline
        self.assertEqual(self.controller.status, "offline")
        self.assertEqual(self.device.status, "controller_offline")

        # Xác thực 2: Hệ thống phải tự động tạo bản ghi Cảnh báo lỗi thiết bị (device_issue) gắn với đầu đọc thẻ này
        warning_type_device = self.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "device_issue")], limit=1)
        warning = self.env["t4.gate_keeper.area_warning"].search([
            ("device_id", "=", self.device.id),
            ("warning_type_id", "=", warning_type_device.id),
            ("state", "=", "warning"),
        ])
        self.assertTrue(warning)
        self.assertIn("is offline", warning.description)

    def test_02_cron_sync_missing_employees(self):
        """Hàm kiểm thử: Tác vụ tự động đồng bộ nhân sự mới tuyển từ HR gốc (Missing Employee Sync).
        Mục đích: Đảm bảo tự động phát hiện các nhân viên mới tạo ở module HR gốc của Odoo và tự sinh hồ sơ Gate Keeper tương ứng
                  để quản lý quyền ra vào văn phòng chi nhánh.
        """
        # Bước 1: Tạo mới một nhân sự HR gốc (nhân sự mới tuyển, chưa có hồ sơ Gate Keeper chi nhánh)
        new_hr_employee = self.env["hr.employee"].create({
            "name": "Lê Thị Nhân Viên Mới",
        })

        # Bước 2: Kích hoạt tác vụ chạy định kỳ đồng bộ nhân sự
        self.env["t4.gate_keeper.scheduler"].cron_sync_missing_employees()

        # Xác thực: Hồ sơ Gate Keeper tương ứng của nhân viên mới phải được tạo tự động với mã emp_id duy nhất
        gk_employee = self.env["t4.gate_keeper.employee"].search([("hr_employee_id", "=", new_hr_employee.id)], limit=1)
        self.assertTrue(gk_employee)
        self.assertEqual(gk_employee.name, "Lê Thị Nhân Viên Mới")
        self.assertTrue(gk_employee.emp_id)

    def test_03_cron_escalate_warnings(self):
        """Hàm kiểm thử: Tác vụ tự động leo thang cảnh báo chưa giải quyết quá hạn (Warning Escalation).
        Mục đích: Đảm bảo tự động nâng mức độ nghiêm trọng của cảnh báo (ví dụ từ low lên medium) nếu cảnh báo an ninh
                  văn phòng chi nhánh chưa được ban quản lý xử lý sau 15 phút cooldown.
        """
        # Bước 1: Khởi tạo bản ghi cảnh báo an ninh với mức độ ban đầu là thấp (low) và chưa xử lý (warning)
        warning = self.env["t4.gate_keeper.area_warning"].create({
            "area_id": self.area.id,
            "employee_id": self.employee.id,
            "warning_type_id": self.env.ref("t4_gate_keeper.warning_type_unknown_card").id,
            "priority": "low",
            "state": "warning",
        })

        # Giả lập thời điểm leo thang gần nhất cách đây 20 phút (vượt qua mốc cooldown 15 phút)
        warning.write({
            "escalated_at": Datetime.now() - timedelta(minutes=20),
        })

        # Bước 2: Kích hoạt tác vụ chạy định kỳ leo thang cảnh báo
        self.env["t4.gate_keeper.scheduler"].cron_escalate_warnings()

        # Xác thực: Mức độ ưu tiên của cảnh báo an ninh văn phòng phải tự động được tăng lên trung bình (medium)
        self.assertEqual(warning.priority, "medium")

    def test_04_cron_overtime_check(self):
        """Hàm kiểm thử: Tác vụ tự động quét và cảnh báo làm việc quá giờ quy định tại chi nhánh (Overtime Check).
        Mục đích: Phát hiện các nhân viên ở lại văn phòng/kho hàng liên tục vượt ngưỡng 9 giờ và tự động sinh cảnh báo làm quá giờ.
        """
        # Bước 1: Giả lập trạng thái nhân viên đang ở trong Kho chi nhánh Đà Nẵng
        self.employee.with_context(allow_employee_presence_write=True).write({
            "presence_state": "inside",
            "current_area_id": self.area.id,
        })

        # Bước 2: Tạo log quẹt thẻ VÀO cửa kho cách đây 10 giờ (vượt quá ngưỡng 9 giờ cho phép)
        access_time = Datetime.now() - timedelta(hours=10)
        log = self.env["t4.gate_keeper.access_log"].create({
            "employee_id": self.employee.id,
            "device_id": self.device.id,
            "direction": "in",
            "access_time": access_time,
        })

        # Bước 3: Kích hoạt tác vụ chạy định kỳ quét làm việc quá giờ
        self.env["t4.gate_keeper.scheduler"].cron_overtime_check()

        # Xác thực: Bản ghi cảnh báo Overtime đã được sinh ra kèm mô tả thời gian chi tiết
        warning = self.env["t4.gate_keeper.area_warning"].search([
            ("employee_id", "=", self.employee.id),
            ("area_id", "=", self.area.id),
            ("warning_type_id", "=", self.warning_type_overtime.id),
            ("state", "=", "warning"),
        ])
        self.assertTrue(warning)
        self.assertIn("vượt ngưỡng overtime", warning.description)
