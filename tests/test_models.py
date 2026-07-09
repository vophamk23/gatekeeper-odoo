# -*- coding: utf-8 -*-
# Mục đích: Kiểm thử các logic tính toán nội bộ (compute fields) và các ràng buộc dữ liệu (unique constraints)
#           của các mô hình (models) thuộc hệ thống quản lý an ninh chi nhánh công ty ở cả mức ORM và Database.
# Chủ đề: Ràng buộc mô hình quản lý chi nhánh doanh nghiệp (Enterprise Models & Constraints).
# Nội dung bao gồm:
#   - Gom danh sách thiết bị tự động của chi nhánh công ty (Branch device_ids compute).
#   - Tính toán trạng thái an ninh của khu vực văn phòng dựa trên số lượng cảnh báo tồn đọng.
#   - Đổi trạng thái thiết bị hàng loạt khi bộ điều khiển chi nhánh thay đổi trạng thái (Cascade status).
#   - Sinh tự động và bảo vệ mã số định danh nhân viên văn phòng chi nhánh (bất biến/immutability).
#   - Thực thi các ràng buộc duy nhất (Unique database constraints) chặn trùng mã nhân viên và serial bộ điều khiển.

from odoo.tests import common
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError
from odoo.tools import mute_logger

class TestModels(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestModels, cls).setUpClass()

        # 1. Khởi tạo Chi nhánh công ty mẫu (Company Branch)
        cls.branch = cls.env["t4.gate_keeper.branch"].create({
            "name": "Chi nhánh HCM - Công ty Tech",
            "timezone": "Asia/Ho_Chi_Minh",
        })

        # 2. Khởi tạo Khu vực văn phòng mẫu (Office Area)
        cls.area = cls.env["t4.gate_keeper.area"].create({
            "name": "Khu Vực Văn Phòng Làm Việc",
            "branch_id": cls.branch.id,
        })

        # 3. Khởi tạo Bộ điều khiển cửa văn phòng mẫu (Controller)
        cls.controller = cls.env["t4.gate_keeper.controller"].create({
            "name": "Bộ điều khiển cửa chính văn phòng",
            "serial_number": "CTRL-OFFICE-999",
            "branch_id": cls.branch.id,
            "status": "online",
        })

        # 4. Khởi tạo Đầu đọc thẻ cửa văn phòng mẫu (Device)
        cls.device = cls.env["t4.gate_keeper.device"].create({
            "name": "Đầu đọc thẻ RFID cửa chính văn phòng",
            "controller_id": cls.controller.id,
            "area_id": cls.area.id,
            "serial_number": "DEV-READER-999",
            "status": "online",
        })

        # 5. Khởi tạo Nhân viên văn phòng chi nhánh mẫu (Employee)
        cls.employee = cls.env["t4.gate_keeper.employee"].create({
            "name": "Đặng Văn Nhân Viên",
            "branch_id": cls.branch.id,
        })

    def test_01_branch_device_ids_compute(self):
        """Hàm kiểm thử: Hàm tự động gom danh sách thiết bị thuộc Chi nhánh công ty (Branch device_ids compute).
        Mục đích: Đảm bảo khi bổ sung bộ điều khiển và thiết bị mới thuộc chi nhánh, chi nhánh đó tự động cập nhật
                  chính xác danh sách tổng các thiết bị trực thuộc.
        """
        # Bước 1: Xác thực ban đầu chi nhánh có 1 thiết bị trực thuộc
        self.branch._compute_device_ids()
        self.assertEqual(len(self.branch.device_ids), 1)
        self.assertIn(self.device.id, self.branch.device_ids.ids)

        # Bước 2: Tạo thêm một bộ điều khiển thứ 2 và một thiết bị đầu đọc thứ 2 thuộc cùng chi nhánh
        controller2 = self.env["t4.gate_keeper.controller"].create({
            "name": "Bộ điều khiển cửa phụ văn phòng",
            "serial_number": "CTRL-OFFICE-888",
            "branch_id": self.branch.id,
        })
        device2 = self.env["t4.gate_keeper.device"].create({
            "name": "Đầu đọc thẻ cửa phụ văn phòng",
            "controller_id": controller2.id,
            "area_id": self.area.id,
            "serial_number": "DEV-READER-888",
        })

        # Bước 3: Tính toán lại và xác thực số lượng thiết bị của chi nhánh công ty đã tăng lên 2
        self.branch._compute_device_ids()
        self.assertEqual(len(self.branch.device_ids), 2)
        self.assertIn(device2.id, self.branch.device_ids.ids)

    def test_02_area_warning_status_compute(self):
        """Hàm kiểm thử: Trạng thái an ninh khu vực văn phòng chi nhánh (Office Area warning status compute).
        Mục đích: Đảm bảo số lượng cảnh báo hoạt động (warning_count) và trạng thái an ninh của khu vực (status: 'normal' hoặc 'warning')
                  được cập nhật tức thời khi phát sinh cảnh báo mới hoặc khi quản lý văn phòng giải quyết cảnh báo.
        """
        # Bước 1: Trạng thái ban đầu của khu vực văn phòng phải hoàn toàn bình thường (normal, count = 0)
        self.assertEqual(self.area.warning_count, 0)
        self.assertEqual(self.area.status, "normal")

        # Bước 2: Tạo một bản ghi cảnh báo an ninh mới gắn với khu vực này (ví dụ cảnh báo lỗi kết nối thiết bị)
        warning_type = self.env["t4.gate_keeper.area_warning_type"].search([], limit=1)
        warning = self.env["t4.gate_keeper.area_warning"].create({
            "area_id": self.area.id,
            "warning_type_id": warning_type.id,
            "state": "warning",
        })

        # Bước 3: Tính toán lại và xác thực khu vực chuyển sang trạng thái cảnh báo nguy hiểm (warning, count = 1)
        self.area._compute_warning_count()
        self.area._compute_status()
        self.assertEqual(self.area.warning_count, 1)
        self.assertEqual(self.area.status, "warning")

        # Bước 4: Thực hiện hành động giải quyết cảnh báo (action_resolve) của quản trị viên chi nhánh
        warning.action_resolve()

        # Bước 5: Xác thực khu vực quay trở lại trạng thái an toàn bình thường (status='normal')
        self.area._compute_warning_count()
        self.area._compute_status()
        self.assertEqual(self.area.warning_count, 1)
        self.assertEqual(self.area.status, "normal")

    def test_03_controller_status_cascade_to_devices(self):
        """Hàm kiểm thử: Lan truyền trạng thái từ Bộ điều khiển xuống các thiết bị con (Cascade write status).
        Mục đích: Đảm bảo khi bộ điều khiển chi nhánh chuyển sang ngoại tuyến (offline), toàn bộ các thiết bị đầu đọc thẻ
                  kết nối qua nó cũng tự động đổi trạng thái sang 'controller_offline'. Khi bộ điều khiển trực tuyến lại,
                  các đầu đọc cũng quay lại 'online'.
        """
        # Bước 1: Xác thực trạng thái ban đầu đều trực tuyến (online)
        self.assertEqual(self.controller.status, "online")
        self.assertEqual(self.device.status, "online")

        # Bước 2: Thay đổi trạng thái bộ điều khiển sang ngoại tuyến (offline)
        self.controller.write({"status": "offline"})
        # Đọc lại từ database và xác thực thiết bị trực thuộc tự chuyển sang 'controller_offline'
        self.device.invalidate_recordset(["status"])
        self.assertEqual(self.device.status, "controller_offline")

        # Bước 3: Bộ điều khiển kết nối lại thành công, chuyển sang trực tuyến (online)
        self.controller.write({"status": "online"})
        # Xác thực đầu đọc thẻ tự động quay lại trạng thái online bình thường
        self.device.invalidate_recordset(["status"])
        self.assertEqual(self.device.status, "online")

    def test_04_employee_id_immutability(self):
        """Hàm kiểm thử: Tính tự sinh và bất biến của Mã nhân viên công ty (Employee ID immutability).
        Mục đích: Đảm bảo mã nhân sự duy nhất (emp_id) được sinh tự động ngay sau khi tạo và không cho phép
                  bất kỳ ai chỉnh sửa mã này để làm sai lệch mã đồng bộ trên thiết bị phần cứng.
        """
        # Bước 1: Xác thực mã emp_id đã được sinh tự động khi tạo nhân viên
        self.assertTrue(self.employee.emp_id)

        # Bước 2: Cố tình thay đổi mã emp_id -> Hệ thống phải ném lỗi ValidationError chặn lại
        with self.assertRaises(ValidationError):
            self.employee.write({"emp_id": "EMP_MODIFIED_999"})

    @mute_logger("odoo.sql_db")
    def test_05_sql_constraints(self):
        """Hàm kiểm thử: Các ràng buộc duy nhất ở mức Database SQL (Database Unique Constraints).
        Mục đích: Đảm bảo không thể tồn tại hai nhân viên trùng mã số định danh (emp_id) hoặc hai bộ điều khiển
                  trùng số Serial vật lý (serial_number) trong hệ thống dữ liệu công ty.
        """
        # Bước 1: Thử tạo trùng mã emp_id nhân viên -> Phải ném lỗi IntegrityError ở mức DB
        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                self.env["t4.gate_keeper.employee"].create({
                    "name": "Nhân viên trùng mã",
                    "emp_id": self.employee.emp_id,
                    "branch_id": self.branch.id,
                })

        # Bước 2: Thử tạo trùng số Serial bộ điều khiển -> Phải ném lỗi IntegrityError ở mức DB
        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                self.env["t4.gate_keeper.controller"].create({
                    "name": "Bộ điều khiển trùng Serial",
                    "serial_number": self.controller.serial_number,
                    "branch_id": self.branch.id,
                })

    def test_06_employee_presence_write_protection(self):
        """Hàm kiểm thử: Bảo vệ ghi đè trạng thái hiện diện (Presence State Protection).
        Mục đích: Đảm bảo không thể tự ý sửa đổi trường presence_state và current_area_id
                  của nhân viên nếu không truyền cờ context cho phép ghi nhận an ninh.
        """
        # Thử thay đổi trực tiếp presence_state -> Hệ thống phải chặn và ném lỗi ValidationError
        with self.assertRaises(ValidationError):
            self.employee.write({"presence_state": "inside"})

        # Thử thay đổi trực tiếp current_area_id -> Hệ thống phải chặn và ném lỗi ValidationError
        with self.assertRaises(ValidationError):
            self.employee.write({"current_area_id": self.area.id})

        # Khi truyền đúng context allow_employee_presence_write -> Thay đổi phải thành công
        self.employee.with_context(allow_employee_presence_write=True).write({
            "presence_state": "inside",
            "current_area_id": self.area.id,
        })
        self.assertEqual(self.employee.presence_state, "inside")
