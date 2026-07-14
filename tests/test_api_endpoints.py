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
        payload = {"controller_sn": "CTRL-API-999"}
        p_request, p_body = self._mock_request_and_body(payload)

        with p_request, p_body:
            self.controller.controller_heartbeat()

        # Xác thực Controller chuyển sang trạng thái online và cập nhật last_heartbeat_at
        self.assertEqual(self.controller.status, "online")
        self.assertTrue(self.controller.last_heartbeat_at)

        # Bước 2: Gửi tín hiệu Heartbeat với mã Serial sai -> Hệ thống phải ném lỗi ValidationError
        invalid_payload = {"controller_sn": "CTRL-API-INVALID"}
        p_request2, p_body2 = self._mock_request_and_body(invalid_payload)
        with p_request2, p_body2:
            with self.assertRaises(ValidationError):
                self.controller.controller_heartbeat()

    def test_02_controller_employee_sync_api(self):
        """Hàm kiểm thử: API đồng bộ thông tin nhân sự và sinh trắc học sang bộ điều khiển (Employee Delta Sync).
        Đảm bảo xuất dữ liệu đúng định dạng new/update/deleted và cập nhật last_sync_at.
        """
        payload = {"controller_sn": "CTRL-API-999"}
        p_request, p_body = self._mock_request_and_body(payload)

        # Reset last_sync_at về False để lấy toàn bộ dữ liệu đồng bộ lần đầu
        self.controller.write({"last_sync_at": False})

        with p_request, p_body:
            res = self.controller.controller_employee_sync()

        # Xác thực 1: Cấu trúc JSON trả về chứa danh sách new/update/deleted
        self.assertIn("data", res)
        data_list = res["data"]
        self.assertTrue(len(data_list) > 0)
        data = data_list[0]
        self.assertIn("new", data)
        self.assertIn("update", data)
        self.assertIn("deleted", data)
        # Lần đầu sync: nhân viên test phải nằm trong danh sách "new"
        emp_data = next((e for e in data["new"] if e["id"] == self.employee.id), None)
        self.assertTrue(emp_data, "Không tìm thấy nhân viên test trong danh sách new")

        # Bước 3: Đồng bộ lần thứ hai (không có thay đổi mới) -> Trả về danh sách rỗng
        from datetime import timedelta
        self.controller.write({"last_sync_at": Datetime.now() + timedelta(minutes=5)})
        with p_request, p_body:
            res2 = self.controller.controller_employee_sync()
        data2 = res2["data"][0]
        self.assertEqual(len(data2["new"]) + len(data2["update"]) + len(data2["deleted"]), 0)

    def test_03_access_log_upload_rfid_card(self):
        """Hàm kiểm thử: API tải nhật ký quẹt thẻ vật lý (RFID Card Upload).
        Xác nhận hệ thống ghi nhận đúng nhân viên khi quẹt thẻ hợp lệ, và kích hoạt cảnh báo thẻ lạ khi quẹt thẻ chưa đăng ký.
        """
        # Bước 1: Quẹt thẻ hợp lệ (thẻ CARD_API_888 đã gắn cho nhân viên Nguyen Van API)
        payload_valid = {
            "controller_id": "CTRL-API-999",
            "logs": [{
                "device_serial": "DEV-API-999",
                "card_code": "CARD_API_888",
                "direction": "in",
                "verification_type": "card",
                "access_time": "2026-07-08 10:00:00"
            }]
        }
        p_request, p_body = self._mock_request_and_body(payload_valid)

        with p_request, p_body:
            res = self.controller.upload_logs()

        # Xác thực: Trả về số lượng log đã xử lý
        self.assertEqual(res["data"]["processed_count"], 1)

        # Kiểm tra bản ghi access log thực tế trong Database
        log = self.env["t4.gate_keeper.access_log"].search([
            ("card_code", "=", "CARD_API_888"),
            ("direction", "=", "in"),
        ], limit=1)
        self.assertTrue(log.exists())
        self.assertEqual(log.employee_id.id, self.employee.id)
        self.assertEqual(log.direction, "in")

        # Bước 2: Quẹt thẻ lạ (CARD_UNKNOWN_999 chưa được đăng ký trong hệ thống)
        payload_unknown = {
            "controller_id": "CTRL-API-999",
            "logs": [{
                "device_serial": "DEV-API-999",
                "card_code": "CARD_UNKNOWN_999",
                "direction": "in",
                "verification_type": "card",
                "access_time": "2026-07-08 10:05:00"
            }]
        }
        p_request2, p_body2 = self._mock_request_and_body(payload_unknown)

        with p_request2, p_body2:
            res_unknown = self.controller.upload_logs()

        self.assertEqual(res_unknown["data"]["processed_count"], 1)
        log_unknown = self.env["t4.gate_keeper.access_log"].search([
            ("card_code", "=", "CARD_UNKNOWN_999"),
            ("direction", "=", "in"),
        ], limit=1)
        self.assertTrue(log_unknown.exists())
        self.assertFalse(log_unknown.employee_id) # Không liên kết nhân sự

        # Xác thực: Cảnh báo thẻ lạ được tạo tự động liên kết với log này
        warning = self.env["t4.gate_keeper.area_warning"].search([
            ("access_log_id", "=", log_unknown.id),
            ("warning_type_id", "=", self.warning_type_unknown.id),
        ])
        self.assertTrue(warning)

    def test_04_access_log_upload_biometric(self):
        """Hàm kiểm thử: API tải nhật ký nhận diện bằng Sinh trắc học (Biometric Recognition Upload).
        Xác nhận hệ thống xác thực thành công khuôn mặt đã đăng ký mẫu.
        """
        # Bước 1: Quẹt khuôn mặt hợp lệ (Nhân viên có đăng ký mẫu Face template trong hệ thống)
        payload_valid_face = {
            "controller_id": "CTRL-API-999",
            "logs": [{
                "device_serial": "DEV-API-999",
                "emp_id": "EMP_API_001",
                "direction": "in",
                "verification_type": "face",
                "access_time": "2026-07-08 10:10:00"
            }]
        }
        p_request, p_body = self._mock_request_and_body(payload_valid_face)

        with p_request, p_body:
            res = self.controller.upload_logs()

        self.assertEqual(res["data"]["processed_count"], 1)
        log = self.env["t4.gate_keeper.access_log"].search([
            ("employee_id", "=", self.employee.id),
            ("verification_type", "=", "face"),
        ], limit=1)
        self.assertTrue(log.exists())

        # Bước 2: Quẹt bằng Vân tay (Hợp lệ về mặt định danh nhưng vân tay chưa khai báo - hệ thống vẫn nhận dạng log từ controller)
        payload_invalid_finger = {
            "controller_id": "CTRL-API-999",
            "logs": [{
                "device_serial": "DEV-API-999",
                "emp_id": "EMP_API_001",
                "direction": "in",
                "verification_type": "fingerprint",
                "access_time": "2026-07-08 10:15:00"
            }]
        }
        p_request2, p_body2 = self._mock_request_and_body(payload_invalid_finger)

        with p_request2, p_body2:
            res_finger = self.controller.upload_logs()

        self.assertEqual(res_finger["data"]["processed_count"], 1)
        log_finger = self.env["t4.gate_keeper.access_log"].search([
            ("employee_id", "=", self.employee.id),
            ("verification_type", "=", "fingerprint"),
        ], limit=1)
        self.assertTrue(log_finger.exists())

    def test_05_access_log_upload_password_and_other_auth(self):
        """Hàm kiểm thử: API tải nhật ký xác thực bằng Password và Other.
        Đảm bảo khi quẹt bằng Password hoặc Other, hệ thống tìm đúng nhân viên theo emp_id.
        """
        # Bước 1: Quẹt mật khẩu hợp lệ (logs chứa emp_id)
        payload_password = {
            "controller_id": "CTRL-API-999",
            "logs": [{
                "device_serial": "DEV-API-999",
                "emp_id": "EMP_API_001",
                "direction": "in",
                "verification_type": "password",
                "access_time": "2026-07-08 11:00:00"
            }]
        }
        p_request, p_body = self._mock_request_and_body(payload_password)

        with p_request, p_body:
            res = self.controller.upload_logs()

        self.assertEqual(res["data"]["processed_count"], 1)
        log = self.env["t4.gate_keeper.access_log"].search([
            ("employee_id", "=", self.employee.id),
            ("verification_type", "=", "password"),
        ], limit=1)
        self.assertTrue(log.exists())

        # Bước 2: Quẹt bằng hình thức khác (other) hợp lệ
        payload_other = {
            "controller_id": "CTRL-API-999",
            "logs": [{
                "device_serial": "DEV-API-999",
                "emp_id": "EMP_API_001",
                "direction": "in",
                "verification_type": "other",
                "access_time": "2026-07-08 11:00:15"
            }]
        }
        p_request2, p_body2 = self._mock_request_and_body(payload_other)

        with p_request2, p_body2:
            res_other = self.controller.upload_logs()

        self.assertEqual(res_other["data"]["processed_count"], 1)
        log_other = self.env["t4.gate_keeper.access_log"].search([
            ("employee_id", "=", self.employee.id),
            ("verification_type", "=", "other"),
        ], limit=1)
        self.assertTrue(log_other.exists())

    def test_06_employee_biometric_get_api(self):
        """Hàm kiểm thử: API lấy thông tin sinh trắc học và thẻ của nhân viên (EmployeeBiometricGet)."""
        # Bước 1: Gửi yêu cầu hợp lệ (cùng chi nhánh)
        payload_valid = {
            "controller_id": "CTRL-API-999",
            "emp_id": "EMP_API_001",
        }
        p_request, p_body = self._mock_request_and_body(payload_valid)
        with p_request, p_body:
            res = self.controller.get_biometric()

        self.assertEqual(res["message"], "Success")
        self.assertEqual(res["data"]["emp_id"], "EMP_API_001")
        self.assertIn("CARD_API_888", res["data"]["cards"])

        # Bước 2: Gửi yêu cầu chéo chi nhánh (Khác chi nhánh)
        other_branch = self.env["t4.gate_keeper.branch"].create({
            "name": "Other Branch Test",
            "timezone": "Asia/Ho_Chi_Minh",
        })
        self.env["t4.gate_keeper.device_model"].create({
            "name": "Generic Model",
        })
        other_employee = self.env["t4.gate_keeper.employee"].create({
            "name": "Other Employee",
            "branch_id": other_branch.id,
            "emp_id": "EMP_API_OTHER",
        })

        payload_invalid = {
            "controller_id": "CTRL-API-999",
            "emp_id": "EMP_API_OTHER",
        }
        p_request2, p_body2 = self._mock_request_and_body(payload_invalid)
        with p_request2, p_body2:
            with self.assertRaises(ValidationError):
                self.controller.get_biometric()
