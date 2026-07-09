# -*- coding: utf-8 -*-
# Mục đích: Kiểm thử các hàm xử lý API Endpoint phục vụ giao tiếp giữa Controller phần cứng và Odoo.
#           Bao gồm: API nhận Heartbeat, API đồng bộ nhân viên (delta sync),
#           API đẩy log quẹt thẻ RFID, và API đẩy log quẹt sinh trắc học (vân tay, khuôn mặt).
#           Sử dụng phương pháp mock request để giả lập dữ liệu JSON truyền từ thiết bị.

from odoo.tests import common
from odoo.fields import Datetime
from odoo.exceptions import ValidationError
from unittest.mock import patch, MagicMock


class TestApiEndpoints(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestApiEndpoints, cls).setUpClass()

        # 1. Khởi tạo Chi nhánh kiểm thử (Branch)
        cls.branch = cls.env["t4.gate_keeper.branch"].create({
            "name": "Branch Test API",
            "timezone": "Asia/Ho_Chi_Minh",
        })

        # 2. Khởi tạo Khu vực kiểm thử (Area)
        cls.area = cls.env["t4.gate_keeper.area"].create({
            "name": "Server Room API",
            "branch_id": cls.branch.id,
        })

        # 3. Khởi tạo Bộ điều khiển kiểm thử (Controller)
        cls.controller = cls.env["t4.gate_keeper.controller"].create({
            "name": "API Controller",
            "serial_number": "CTRL-API-999",
            "branch_id": cls.branch.id,
            "status": "offline",
        })

        # 4. Khởi tạo Thiết bị kiểm thử (Device)
        cls.device = cls.env["t4.gate_keeper.device"].create({
            "name": "API Card Reader",
            "controller_id": cls.controller.id,
            "area_id": cls.area.id,
            "serial_number": "DEV-API-999",
            "status": "offline",
        })

        # 5. Khởi tạo Thuật toán sinh trắc (Biometric Algorithm)
        cls.algorithm_face = cls.env["t4.gate_keeper.algorithm"].create({
            "name": "Face 3D",
            "code": "face_3d",
            "algorithm_type": "face",
            "version": "1.0",
        })

        # 6. Khởi tạo Nhân sự kiểm thử (Employee)
        cls.employee = cls.env["t4.gate_keeper.employee"].create({
            "name": "Nguyen Van API",
            "branch_id": cls.branch.id,
            "emp_id": "EMP_API_001",
        })

        # 7. Khởi tạo thẻ RFID cho Nhân sự
        cls.auth_info = cls.env["t4.gate_keeper.auth_info"].create({
            "employee_id": cls.employee.id,
            "card_code": "CARD_API_888",
        })

        # 8. Khởi tạo Mẫu sinh trắc học khuôn mặt (Biometric Face Template)
        cls.biometric = cls.env["t4.gate_keeper.employee.biometric"].create({
            "employee_id": cls.employee.id,
            "algorithm_id": cls.algorithm_face.id,
            "template": b"ZmFjZV90ZW1wbGF0ZV9kYXRhX3h5eg==",
        })

        # 9. Khởi tạo Loại cảnh báo và chính sách cảnh báo thẻ lạ
        cls.warning_type_unknown = cls.env["t4.gate_keeper.area_warning_type"].search([("code", "=", "unknown_card")], limit=1)
        cls.policy_unknown = cls.env["t4.gate_keeper.alert_policy"].create({
            "name": "API Unknown Card Alert",
            "code": "POL_API_UNKNOWN",
            "warning_type_id": cls.warning_type_unknown.id,
            "priority": "critical",
        })

    def _mock_request_and_body(self, payload):
        """Hàm hỗ trợ: Giả lập đối tượng request của Odoo và dữ liệu JSON tải lên (payload) từ thiết bị."""
        mock_req = MagicMock()
        mock_req.env = self.env
        # Giả lập API Odoo Core Response Helper
        mock_app = MagicMock()
        mock_req.env = MagicMock(wraps=self.env)
        mock_req.env.__getitem__.side_effect = lambda key: mock_app if key == 'core.api.application' else self.env[key]
        
        p_request = patch("odoo.addons.t4_coreapi.utils.core_api_utils.request", mock_req)
        p_body = patch("odoo.addons.t4_gate_keeper.models.gk_controller.get_body", return_value=payload)
        return p_request, p_body

    def test_01_controller_heartbeat_api(self):
        """Hàm kiểm thử: API nhận tín hiệu Heartbeat từ bộ điều khiển.
        Đảm bảo cập nhật trạng thái Controller thành 'online' và cập nhật thời gian last_heartbeat_at.
        """
        # Bước 1: Gửi tín hiệu Heartbeat hợp lệ
        payload = {"serial_number": "CTRL-API-999"}
        p_request, p_body = self._mock_request_and_body(payload)

        with p_request, p_body:
            self.controller.controller_heartbeat()

        # Xác thực Controller chuyển sang trạng thái online và cập nhật last_heartbeat_at
        self.assertEqual(self.controller.status, "online")
        self.assertTrue(self.controller.last_heartbeat_at)

        # Bước 2: Gửi tín hiệu Heartbeat với mã Serial sai -> Hệ thống phải ném lỗi ValidationError
        invalid_payload = {"serial_number": "CTRL-API-INVALID"}
        p_request2, p_body2 = self._mock_request_and_body(invalid_payload)
        with p_request2, p_body2:
            with self.assertRaises(ValidationError):
                self.controller.controller_heartbeat()

    def test_02_controller_employee_sync_api(self):
        """Hàm kiểm thử: API đồng bộ thông tin nhân sự và sinh trắc học sang bộ điều khiển (Employee Delta Sync).
        Đảm bảo xuất dữ liệu đúng định dạng delta sync (chỉ lấy các thay đổi mới nhất) và cập nhật last_sync_at.
        """
        payload = {"serial_number": "CTRL-API-999"}
        p_request, p_body = self._mock_request_and_body(payload)

        # Reset last_sync_at về False để lấy toàn bộ dữ liệu đồng bộ lần đầu
        self.controller.write({"last_sync_at": False})

        with p_request, p_body:
            res = self.controller.controller_employee_sync()

        # Xác thực 1: Cấu trúc JSON trả về chứa thông tin nhân sự và mẫu sinh trắc học
        self.assertIn("data", res)
        emp_data = next((e for e in res["data"] if e["emp_id"] == "EMP_API_001"), None)
        self.assertTrue(emp_data, "Không tìm thấy nhân viên test trong danh sách đồng bộ")
        self.assertEqual(emp_data["name"], "Nguyen Van API")
        self.assertEqual(len(emp_data["biometrics"]), 1)
        self.assertEqual(emp_data["biometrics"][0]["algorithm_code"], "face_3d")
        self.assertEqual(emp_data["biometrics"][0]["template_data"], "ZmFjZV90ZW1wbGF0ZV9kYXRhX3h5eg==")

        # Xác thực 2: Trường last_sync_at của Controller được cập nhật thời gian đồng bộ thành công
        self.assertTrue(self.controller.last_sync_at)

        # Bước 3: Đồng bộ lần thứ hai (không có thay đổi mới) -> Trả về thông báo "Already up-to-date" và danh sách trống
        from datetime import timedelta
        self.controller.write({"last_sync_at": Datetime.now() + timedelta(minutes=5)})
        with p_request, p_body:
            res2 = self.controller.controller_employee_sync()
        self.assertEqual(res2["message"], "Already up-to-date")
        self.assertEqual(len(res2["data"]), 0)

    def test_03_access_log_upload_rfid_card(self):
        """Hàm kiểm thử: API tải nhật ký quẹt thẻ vật lý (RFID Card Upload).
        Xác nhận hệ thống ghi nhận đúng nhân viên khi quẹt thẻ hợp lệ, và kích hoạt cảnh báo thẻ lạ khi quẹt thẻ chưa đăng ký.
        """
        # Bước 1: Quẹt thẻ hợp lệ (thẻ CARD_API_888 đã gắn cho nhân viên Nguyen Van API)
        payload_valid = {
            "serial_number": "CTRL-API-999",
            "device_serial": "DEV-API-999",
            "card_value": "CARD_API_888",
            "direction": "in",
            "verification_type": "card",
            "access_time": "2026-07-08 10:00:00"
        }
        p_request, p_body = self._mock_request_and_body(payload_valid)

        with p_request, p_body:
            res = self.controller.access_log_upload()

        # Xác thực: Trả về tên nhân sự tương ứng và không có cảnh báo
        self.assertEqual(res["data"]["employee_name"], "Nguyen Van API")
        self.assertFalse(res["data"]["has_warning"])

        # Kiểm tra bản ghi access log thực tế trong Database
        log = self.env["t4.gate_keeper.access_log"].browse(res["data"]["log_id"])
        self.assertTrue(log.exists())
        self.assertEqual(log.employee_id.id, self.employee.id)
        self.assertEqual(log.direction, "in")

        # Bước 2: Quẹt thẻ lạ (CARD_UNKNOWN_999 chưa được đăng ký trong hệ thống)
        payload_unknown = {
            "serial_number": "CTRL-API-999",
            "device_serial": "DEV-API-999",
            "card_value": "CARD_UNKNOWN_999",
            "direction": "in",
            "verification_type": "card"
        }
        p_request2, p_body2 = self._mock_request_and_body(payload_unknown)

        with p_request2, p_body2:
            res_unknown = self.controller.access_log_upload()

        # Xác thực: Hệ thống trả về cảnh báo an ninh (has_warning = True)
        self.assertTrue(res_unknown["data"]["has_warning"])
        log_unknown = self.env["t4.gate_keeper.access_log"].browse(res_unknown["data"]["log_id"])
        self.assertFalse(log_unknown.employee_id) # Không liên kết nhân sự

        # Xác thực: Cảnh báo thẻ lạ được tạo tự động liên kết với log này
        warning = self.env["t4.gate_keeper.area_warning"].search([
            ("access_log_id", "=", log_unknown.id),
            ("warning_type_id", "=", self.warning_type_unknown.id),
        ])
        self.assertTrue(warning)

    def test_04_access_log_upload_biometric(self):
        """Hàm kiểm thử: API tải nhật ký nhận diện bằng Sinh trắc học (Biometric Recognition Upload).
        Xác nhận hệ thống xác thực thành công khuôn mặt đã đăng ký mẫu, và tạo cảnh báo thẻ lạ/quẹt lỗi khi vân tay chưa đăng ký.
        """
        # Bước 1: Quẹt khuôn mặt hợp lệ (Nhân viên có đăng ký mẫu Face template trong hệ thống)
        payload_valid_face = {
            "serial_number": "CTRL-API-999",
            "device_serial": "DEV-API-999",
            "card_value": "EMP_API_001",
            "direction": "in",
            "verification_type": "face"
        }
        p_request, p_body = self._mock_request_and_body(payload_valid_face)

        with p_request, p_body:
            res = self.controller.access_log_upload()

        # Xác thực: Trả về tên nhân viên và không có cảnh báo
        self.assertEqual(res["data"]["employee_name"], "Nguyen Van API")
        self.assertFalse(res["data"]["has_warning"])

        # Bước 2: Quẹt bằng Vân tay (Nhân viên chưa đăng ký mẫu Vân tay, chỉ đăng ký mẫu Face)
        payload_invalid_finger = {
            "serial_number": "CTRL-API-999",
            "device_serial": "DEV-API-999",
            "card_value": "EMP_API_001",
            "direction": "in",
            "verification_type": "fingerprint"
        }
        p_request2, p_body2 = self._mock_request_and_body(payload_invalid_finger)

        with p_request2, p_body2:
            res_finger = self.controller.access_log_upload()

        # Xác thực: Hệ thống phải báo lỗi cảnh báo an ninh do mẫu vân tay không trùng khớp/chưa đăng ký
        self.assertTrue(res_finger["data"]["has_warning"])
        log_finger = self.env["t4.gate_keeper.access_log"].browse(res_finger["data"]["log_id"])
        self.assertFalse(log_finger.employee_id) # Log không gán nhân viên (coi như quẹt lỗi)

    def test_05_access_log_upload_password_and_other_auth(self):
        """Hàm kiểm thử: API tải nhật ký xác thực bằng Password và Other.
        Đảm bảo khi quẹt bằng Password hoặc Other, hệ thống tìm đúng nhân viên theo emp_id và không bắn cảnh báo thẻ lạ.
        """
        # Bước 1: Quẹt mật khẩu hợp lệ (card_value chứa emp_id)
        payload_password = {
            "serial_number": "CTRL-API-999",
            "device_serial": "DEV-API-999",
            "card_value": "EMP_API_001",
            "direction": "in",
            "verification_type": "password",
            "access_time": "2026-07-08 11:00:00"
        }
        p_request, p_body = self._mock_request_and_body(payload_password)

        with p_request, p_body:
            res = self.controller.access_log_upload()

        self.assertEqual(res["data"]["employee_name"], "Nguyen Van API")
        self.assertFalse(res["data"]["has_warning"])

        # Bước 2: Quẹt bằng hình thức khác (other) hợp lệ (card_value chứa emp_id)
        payload_other = {
            "serial_number": "CTRL-API-999",
            "device_serial": "DEV-API-999",
            "card_value": "EMP_API_001",
            "direction": "in",
            "verification_type": "other",
            "access_time": "2026-07-08 11:00:15"
        }
        p_request2, p_body2 = self._mock_request_and_body(payload_other)

        with p_request2, p_body2:
            res_other = self.controller.access_log_upload()

        self.assertEqual(res_other["data"]["employee_name"], "Nguyen Van API")
        self.assertFalse(res_other["data"]["has_warning"])
