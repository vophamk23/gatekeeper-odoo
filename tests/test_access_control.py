# -*- coding: utf-8 -*-
# Mục đích: Kiểm thử các luồng kiểm soát cửa ra/vào tại chi nhánh công ty và các chính sách cảnh báo an ninh văn phòng.
# Chủ đề: Hệ thống kiểm soát an ninh chi nhánh doanh nghiệp (Corporate Branch & Office Access Control).
# Nội dung bao gồm:
#   - Xác nhận lượt quẹt thẻ VÀO/RA hợp lệ của nhân viên công ty.
#   - Lọc trùng lặp lượt quẹt thẻ (chống quẹt đúp/double-scan trong vòng 10 giây tại cùng 1 đầu đọc).
#   - Phát hiện thẻ lạ chưa đăng ký trong cơ sở dữ liệu công ty và bắn cảnh báo thẻ lạ.
#   - Giám sát giờ cấm truy cập văn phòng ngoài giờ hành chính tại chi nhánh và sinh log OUT giả lập để giải phóng trạng thái nhân viên.
#   - Phát hiện vi phạm quy tắc chống xoay vòng thẻ (Anti-passback) khi nhân viên quẹt thẻ không đúng trình tự vào/ra.
#   - Chặn và cảnh báo khi nhân viên thuộc phòng ban không được cấp quyền cố tình truy cập khu vực giới hạn (ví dụ: phòng máy chủ).

from odoo.tests import common
from odoo.fields import Datetime
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class TestAccessControl(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccessControl, cls).setUpClass()

        # 1. Thiết lập Chi nhánh công ty mẫu (Company Branch)
        cls.branch = cls.env["t4.gate_keeper.branch"].create({
            "name": "Chi nhánh Hà Nội - Công ty Tech",
            "timezone": "Asia/Ho_Chi_Minh",
        })

        # 2. Thiết lập Khu vực văn phòng giới hạn (Restricted Office Area)
        cls.area = cls.env["t4.gate_keeper.area"].create({
            "name": "Phòng Máy Chủ Chi Nhánh",
            "branch_id": cls.branch.id,
        })

        # 3. Thiết lập Bộ điều khiển cửa (Controller) kết nối mạng TCP/IP tại chi nhánh
        cls.controller = cls.env["t4.gate_keeper.controller"].create({
            "name": "Bộ điều khiển cửa phòng máy chủ",
            "serial_number": "CTRL-OFFICE-001",
            "branch_id": cls.branch.id,
        })

        # 4. Thiết lập Thiết bị đầu đọc thẻ (Device) gắn tại cửa phòng máy chủ
        cls.device = cls.env["t4.gate_keeper.device"].create({
            "name": "Đầu đọc thẻ RFID cửa chính phòng máy chủ",
            "controller_id": cls.controller.id,
            "area_id": cls.area.id,
            "serial_number": "DEV-READER-001",
        })

        # 5. Thiết lập Nhân sự mẫu ở phân hệ HR gốc (Odoo HR Employee)
        cls.hr_employee = cls.env["hr.employee"].create({
            "name": "Nguyễn Văn Nhân Viên",
        })

        # 6. Thiết lập Hồ sơ liên kết nhân sự tại phân hệ Gate Keeper để quản lý ra vào chi nhánh
        cls.employee = cls.env["t4.gate_keeper.employee"].create({
            "name": "Nguyễn Văn Nhân Viên",
            "hr_employee_id": cls.hr_employee.id,
            "branch_id": cls.branch.id,
        })

        # 7. Đăng ký thông tin thẻ RFID (thẻ từ nhân viên) gán cho nhân sự mẫu
        cls.auth_info = cls.env["t4.gate_keeper.auth_info"].create({
            "employee_id": cls.employee.id,
            "card_code": "RFID_CARD_OFFICE_123",
        })

        # 8. Tra cứu các loại cảnh báo an ninh được định nghĩa sẵn trong hệ thống phục vụ test
        cls.warning_type_unknown = cls.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "unknown_card")], limit=1)
        cls.warning_type_time = cls.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "unauthorized_time")], limit=1)
        cls.warning_type_seq = cls.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "invalid_sequence")], limit=1)
        cls.warning_type_area = cls.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "unauthorized_area")], limit=1)

    def test_01_valid_access_in_out(self):
        """Hàm kiểm thử: Xác thực lượt quẹt thẻ VÀO và RA văn phòng hợp lệ.
        Mục đích: Đảm bảo khi nhân viên quẹt thẻ đúng trình tự, hệ thống ghi nhận chính xác trạng thái hiện diện (presence_state)
                  ở 'inside' hoặc 'outside' và cập nhật vị trí khu vực (current_area_id) hiện tại của họ.
        """
        # Bước 1: Nhân viên quẹt thẻ VÀO (direction='in') cửa phòng máy chủ chi nhánh
        log_in = self.env["t4.gate_keeper.access_log"].create({
            "employee_id": self.employee.id,
            "device_id": self.device.id,
            "direction": "in",
            "access_time": Datetime.now(),
        })
        # Xác thực: Nhân viên phải có trạng thái hiện diện là đang ở trong (inside) và thuộc Phòng Máy Chủ Chi Nhánh
        self.assertEqual(self.employee.presence_state, "inside")
        self.assertEqual(self.employee.current_area_id.id, self.area.id)

        # Bước 2: Nhân viên quẹt thẻ RA (direction='out') cửa phòng máy chủ sau 15 giây (để vượt qua rule chống quẹt trùng 10s)
        log_out = self.env["t4.gate_keeper.access_log"].create({
            "employee_id": self.employee.id,
            "device_id": self.device.id,
            "direction": "out",
            "access_time": Datetime.now() + timedelta(seconds=15),
        })
        # Xác thực: Trạng thái hiện diện của nhân viên phải chuyển thành ở ngoài (outside) và khu vực hiện tại trống (False)
        self.assertEqual(self.employee.presence_state, "outside")
        self.assertFalse(self.employee.current_area_id)

    def test_02_double_scan_prevention(self):
        """Hàm kiểm thử: Cơ chế chặn quẹt thẻ trùng lặp (Double-Scan Prevention).
        Mục đích: Đảm bảo nếu nhân viên cố ý hoặc vô tình quẹt thẻ liên tiếp nhiều lần tại cùng một đầu đọc trong vòng 10 giây,
                  hệ thống chỉ ghi nhận lượt quẹt đầu tiên và tự động bỏ qua các lượt quẹt trùng lặp sau đó để tránh rác log.
        """
        now = Datetime.now()
        # Bước 1: Lượt quẹt thẻ VÀO đầu tiên của nhân viên (hợp lệ)
        log1 = self.env["t4.gate_keeper.access_log"].create({
            "employee_id": self.employee.id,
            "device_id": self.device.id,
            "direction": "in",
            "access_time": now,
        })
        self.assertTrue(log1)

        # Bước 2: Lượt quẹt thẻ VÀO thứ hai của cùng nhân viên đó tại cùng đầu đọc chỉ sau 5 giây (trùng lặp)
        log2 = self.env["t4.gate_keeper.access_log"].create({
            "employee_id": self.employee.id,
            "device_id": self.device.id,
            "direction": "in",
            "access_time": now + timedelta(seconds=5),
        })
        # Xác thực: Bản ghi log thứ hai không được tạo (trả về recordset rỗng)
        self.assertFalse(log2.exists())

    def test_03_unknown_card_policy(self):
        """Hàm kiểm thử: Chính sách cảnh báo thẻ lạ chưa đăng ký (Unknown Card Alert Policy).
        Mục đích: Đảm bảo khi phát hiện một mã thẻ RFID lạ quẹt tại cửa chi nhánh mà không khớp với bất kỳ nhân sự nào,
                  hệ thống phải tự động phát sinh một cảnh báo an ninh loại 'unknown_card' với độ ưu tiên cao nhất.
        """
        # Bước 1: Tạo chính sách giám sát thẻ lạ tại văn phòng chi nhánh
        policy = self.env["t4.gate_keeper.alert_policy"].create({
            "name": "Giám sát thẻ lạ ra vào văn phòng",
            "code": "POL_OFFICE_UNKNOWN",
            "warning_type_id": self.warning_type_unknown.id,
            "priority": "high",
        })

        # Bước 2: Tạo log quẹt thẻ từ một thẻ lạ (employee_id bằng False)
        log = self.env["t4.gate_keeper.access_log"].create({
            "device_id": self.device.id,
            "direction": "in",
            "access_time": Datetime.now(),
        })

        # Xác thực: Hệ thống phải tự tạo bản ghi Cảnh báo thẻ lạ (state='warning') gắn với log quẹt thẻ này và có mức độ 'high'
        warning = self.env["t4.gate_keeper.area_warning"].search([
            ("access_log_id", "=", log.id),
            ("warning_type_id", "=", self.warning_type_unknown.id),
        ])
        self.assertTrue(warning)
        self.assertEqual(warning.state, "warning")
        self.assertEqual(warning.priority, "high")

    def test_04_unauthorized_time_policy(self):
        """Hàm kiểm thử: Giám sát giờ cấm truy cập văn phòng chi nhánh (Office Curfew Policy).
        Mục đích: Chặn nhân viên đi vào văn phòng ngoài giờ làm việc (ví dụ cấm từ 18h tối đến 7h sáng).
                  Đồng thời sinh cảnh báo ngoài giờ, giữ nguyên trạng thái ở ngoài (outside) và sinh log OUT giả lập
                  để giải phóng trạng thái nhân viên, tránh treo trạng thái 'inside'.
        """
        # Bước 1: Thiết lập chính sách cấm ra vào văn phòng ngoài giờ hành chính (từ 18.0 tối đến 7.0 sáng hôm sau)
        policy = self.env["t4.gate_keeper.alert_policy"].create({
            "name": "Giờ giới nghiêm an ninh văn phòng",
            "code": "POL_OFFICE_TIME",
            "warning_type_id": self.warning_type_time.id,
            "priority": "medium",
            "start_hour": 18.0,
            "end_hour": 7.0,
        })

        # Bước 2: Giả lập nhân viên quẹt thẻ vào lúc 20:00 (Múi giờ Việt Nam +7, tương ứng 13:00 UTC)
        utc_curfew_time = datetime(2026, 7, 8, 13, 0, 0)

        log = self.env["t4.gate_keeper.access_log"].create({
            "employee_id": self.employee.id,
            "device_id": self.device.id,
            "direction": "in",
            "access_time": utc_curfew_time,
        })

        # Xác thực 1: Phải tự động phát sinh bản ghi cảnh báo truy cập ngoài giờ hành chính
        warning = self.env["t4.gate_keeper.area_warning"].search([
            ("access_log_id", "=", log.id),
            ("warning_type_id", "=", self.warning_type_time.id),
        ])
        self.assertTrue(warning)

        # Xác thực 2: Nhân viên bị từ chối vào nên trạng thái hiện diện vẫn phải là ở ngoài (outside)
        self.assertEqual(self.employee.presence_state, "outside")

        # Xác thực 3: Hệ thống phải tự sinh một log RA (direction='out') giả lập để tránh kẹt trạng thái
        fake_out_log = self.env["t4.gate_keeper.access_log"].search([
            ("employee_id", "=", self.employee.id),
            ("is_system_generated", "=", True),
            ("direction", "=", "out"),
        ])
        self.assertTrue(fake_out_log)

    def test_05_anti_passback_policy(self):
        """Hàm kiểm thử: Quy tắc chống quay vòng thẻ (Anti-passback Policy).
        Mục đích: Phát hiện hành vi quẹt thẻ RA khi nhân sự đang ở ngoài hoặc quẹt thẻ VÀO khi đang ở trong.
                  Ngăn chặn hành vi một thẻ được truyền tay cho nhiều người đi qua cửa.
        """
        # Bước 1: Thiết lập chính sách giám sát quy trình ra vào chi nhánh
        policy = self.env["t4.gate_keeper.alert_policy"].create({
            "name": "Chống quay vòng thẻ anti-passback văn phòng",
            "code": "POL_OFFICE_APB",
            "warning_type_id": self.warning_type_seq.id,
            "priority": "critical",
        })

        # Đặt trạng thái ban đầu của nhân viên là ở ngoài văn phòng (outside)
        self.employee.with_context(allow_employee_presence_write=True).write({
            "presence_state": "outside",
            "current_area_id": False,
        })

        # Bước 2: Nhân viên cố tình quẹt thẻ RA (out) khi đang có trạng thái ở ngoài -> Vi phạm Anti-passback!
        log = self.env["t4.gate_keeper.access_log"].create({
            "employee_id": self.employee.id,
            "device_id": self.device.id,
            "direction": "out",
            "access_time": Datetime.now(),
        })

        # Xác thực: Hệ thống tự động tạo cảnh báo vi phạm trình tự với độ ưu tiên cực kỳ nghiêm trọng (critical)
        warning = self.env["t4.gate_keeper.area_warning"].search([
            ("access_log_id", "=", log.id),
            ("warning_type_id", "=", self.warning_type_seq.id),
        ])
        self.assertTrue(warning)
        self.assertEqual(warning.priority, "critical")

    def test_06_unauthorized_area_policy(self):
        """Hàm kiểm thử: Phân quyền truy cập khu vực giới hạn của chi nhánh (Restricted Area Access Control).
        Mục đích: Đảm bảo chặn và tạo cảnh báo ngay lập tức khi một nhân viên thuộc phòng ban không có quyền
                  cố tình quẹt thẻ truy cập vào khu vực cấm (ví dụ: nhân sự phòng Hành chính đi vào Phòng Máy Chủ).
        """
        # Bước 1: Tạo nhóm phòng ban được phép (ví dụ nhóm Kỹ thuật/IT) và nhóm không được phép (nhóm Guest/Hành chính)
        group_allowed = self.env["t4.gate_keeper.employee_group"].create({"name": "Phòng Kỹ thuật IT", "code": "IT_DEPT"})
        group_other = self.env["t4.gate_keeper.employee_group"].create({"name": "Phòng Hành chính Nhân sự", "code": "HR_DEPT"})

        # Gán nhân viên mẫu vào phòng ban không có quyền truy cập (Hành chính Nhân sự)
        self.employee.write({"group_ids": [(6, 0, [group_other.id])]})

        # Bước 2: Thiết lập chính sách bảo mật: Khu vực Phòng Máy Chủ chỉ cho phép nhóm Kỹ thuật IT đi vào
        policy = self.env["t4.gate_keeper.alert_policy"].create({
            "name": "Chỉ nhóm kỹ thuật IT được phép vào Phòng Máy Chủ",
            "code": "POL_OFFICE_AREA",
            "warning_type_id": self.warning_type_area.id,
            "area_ids": [(6, 0, [self.area.id])],
            "allowed_group_ids": [(6, 0, [group_allowed.id])],
            "priority": "critical",
        })

        # Bước 3: Nhân viên phòng Hành chính Nhân sự quẹt thẻ đi vào phòng máy chủ
        log = self.env["t4.gate_keeper.access_log"].create({
            "employee_id": self.employee.id,
            "device_id": self.device.id,
            "direction": "in",
            "access_time": Datetime.now(),
        })

        # Xác thực: Hệ thống tự động tạo cảnh báo vi phạm khu vực cấm (unauthorized_area)
        warning = self.env["t4.gate_keeper.area_warning"].search([
            ("access_log_id", "=", log.id),
            ("warning_type_id", "=", self.warning_type_area.id),
        ])
        self.assertTrue(warning)

    def test_07_anti_passback_empty_current_area(self):
        """Hàm kiểm thử: Quy tắc chống quay vòng thẻ khi current_area_id là rỗng.
        Mục đích: Đảm bảo khi nhân viên đang ở trạng thái 'inside' nhưng current_area_id bằng False,
                  nếu họ cố tình quẹt VÀO một khu vực có định danh, hệ thống vẫn phải kích hoạt cảnh báo anti-passback.
        """
        # Đặt chính sách anti-passback
        self.env["t4.gate_keeper.alert_policy"].create({
            "name": "Chống quay vòng thẻ APB",
            "code": "POL_APB_TEST",
            "warning_type_id": self.warning_type_seq.id,
            "priority": "critical",
        })

        # Đặt trạng thái ban đầu của nhân viên là inside nhưng current_area_id = False
        self.employee.with_context(allow_employee_presence_write=True).write({
            "presence_state": "inside",
            "current_area_id": False,
        })

        # Nhân viên cố tình quẹt VÀO (in) một khu vực
        log = self.env["t4.gate_keeper.access_log"].create({
            "employee_id": self.employee.id,
            "device_id": self.device.id,
            "direction": "in",
            "access_time": Datetime.now(),
        })

        # Xác thực: Hệ thống phát sinh cảnh báo vi phạm anti-passback
        warning = self.env["t4.gate_keeper.area_warning"].search([
            ("access_log_id", "=", log.id),
            ("warning_type_id", "=", self.warning_type_seq.id),
        ])
        self.assertTrue(warning)
