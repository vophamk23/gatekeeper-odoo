# -*- coding: utf-8 -*-
"""
ZKTeco to Odoo Gate Keeper Middleware Simulation.
This script demonstrates how to connect to a ZKTeco device via LAN (Port 4370),
retrieve the latest attendance logs, format them, and upload them to Odoo APIs.

Requirements:
    pip install pyzk requests
"""

import sys
import logging
import requests
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
_logger = logging.getLogger("ZK_Middleware")

try:
    from zk import ZK, const
except ImportError:
    _logger.error("Chưa cài đặt thư viện 'pyzk'. Vui lòng chạy lệnh: pip install pyzk")
    sys.exit(1)

# ==============================================================================
# CẤU HÌNH THÔNG TIN KẾT NỐI (Hãy điều chỉnh cho đúng thực tế)
# ==============================================================================
ZK_DEVICE_IP = "192.168.1.201"    # Địa chỉ IP của máy ZKTeco (Xem ở Bước 1)
ZK_DEVICE_PORT = 4370             # Cổng mặc định của ZKTeco SDK

ODOO_SERVER_URL = "http://localhost:8070"  # URL Odoo Server
CLIENT_ID = "app_bf343cac68c93ecce3f2f56e753999c1"
CLIENT_SECRET = "client_secret_123456"

CONTROLLER_SN = "CTRL-OFFICE-001" # Serial Number của Controller đã khai báo trên Odoo
DEVICE_SN = "DEV-READER-001"     # Serial Number của Device con đã khai báo trên Odoo


# ==============================================================================
# HÀM XÁC THỰC LẤY OAUTH2 TOKEN TỪ ODOO
# ==============================================================================
def get_odoo_token():
    url = f"{ODOO_SERVER_URL}/api/v1/auth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    _logger.info("Đang đăng nhập vào Odoo để lấy Access Token...")
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Trích xuất token dựa trên cấu trúc trả về của t4_coreapi
            token = data.get("api_token", {}).get("token") or data.get("data", {}).get("token")
            if token:
                _logger.info("Lấy Access Token thành công.")
                return token
        _logger.error(f"Đăng nhập thất bại. Mã lỗi: {response.status_code}, Chi tiết: {response.text}")
    except Exception as e:
        _logger.error(f"Lỗi khi kết nối tới Odoo Server: {e}")
    return None


# ==============================================================================
# HÀM ĐẨY NHẬT KÝ QUẸT THẺ (ACCESS LOGS) LÊN ODOO
# ==============================================================================
def upload_logs_to_odoo(token, logs):
    url = f"{ODOO_SERVER_URL}/api/v1/AccessLogUpload"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Định dạng lại dữ liệu thô từ máy ZK sang cấu trúc JSON mà Odoo yêu cầu
    formatted_logs = []
    for log in logs:
        # Ánh xạ loại xác thực từ máy ZK sang Odoo
        # 1: Vân tay, 4: Thẻ từ, 15: Khuôn mặt (tùy thuộc vào model ZK)
        v_type = "card"
        if log.punch == 1:
            v_type = "fingerprint"
        elif log.punch == 15:
            v_type = "face"
            
        formatted_logs.append({
            "device_serial": DEVICE_SN,
            "emp_id": f"GK-{log.user_id}", # Ánh xạ ID người dùng từ ZK sang emp_id của GateKeeper
            "card_code": "",               # Nếu quẹt vân tay/face thì để rỗng
            "direction": "in" if log.status == 0 else "out", # 0: Check-In, 1: Check-Out
            "verification_type": v_type,
            "access_time": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    payload = {
        "controller_id": CONTROLLER_SN,
        "logs": formatted_logs
    }

    _logger.info(f"Đang đẩy {len(formatted_logs)} lượt quẹt thẻ lên Odoo...")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            _logger.info("Đẩy dữ liệu lên Odoo thành công!")
            _logger.info(f"Phản hồi từ Odoo: {response.json()}")
            return True
        _logger.error(f"Đẩy dữ liệu thất bại. Mã lỗi: {response.status_code}, Chi tiết: {response.text}")
    except Exception as e:
        _logger.error(f"Lỗi khi đẩy dữ liệu lên Odoo: {e}")
    return False


# ==============================================================================
# HÀM CHÍNH KẾT NỐI MÁY ZK VÀ LẤY DỮ LIỆU
# ==============================================================================
def main():
    token = get_odoo_token()
    if not token:
        _logger.warning("Không thể lấy token Odoo. Script sẽ tiếp tục chạy ở chế độ KIỂM TRA KẾT NỐI THIẾT BỊ (Không đẩy dữ liệu lên Odoo).")

    zk = ZK(ZK_DEVICE_IP, port=ZK_DEVICE_PORT, timeout=5, force_udp=False)
    conn = None
    try:
        _logger.info(f"Đang kết nối tới máy ZKTeco tại {ZK_DEVICE_IP}:{ZK_DEVICE_PORT}...")
        conn = zk.connect()
        _logger.info("Kết nối tới máy ZKTeco thành công!")
        
        # Vô hiệu hóa thiết bị tạm thời trong lúc đọc dữ liệu để tránh xung đột
        conn.disable_device()
        
        # Đọc danh sách người dùng đã đăng ký trên máy ZK để hiển thị thông tin
        try:
            users = conn.get_users()
            _logger.info(f"Tìm thấy {len(users)} người dùng đăng ký trên máy ZK:")
            for user in users[:5]: # In thử 5 người đầu tiên
                _logger.info(f"  - User ID: {user.user_id} | Tên: {user.name} | Quyền: {user.privilege}")
        except Exception as ue:
            _logger.warning(f"Không thể đọc danh sách người dùng: {ue}")
        
        # Đọc danh sách logs quẹt thẻ từ bộ nhớ của máy ZK
        attendance = conn.get_attendance()
        _logger.info(f"Tìm thấy tổng cộng {len(attendance)} lượt quẹt thẻ trên máy ZK.")
        
        if attendance:
            # Lấy 10 logs gần nhất để in thử ra màn hình console
            _logger.info("10 lượt quẹt gần nhất trên thiết bị:")
            for log in attendance[-10:]:
                _logger.info(
                    f"  - User ID: {log.user_id} | Thời gian: {log.timestamp} | "
                    f"Trạng thái (In/Out): {log.status} | Cách quẹt: {log.punch}"
                )
            
            # Đẩy dữ liệu này lên Odoo nếu có token
            if token:
                upload_logs_to_odoo(token, attendance)
        else:
            _logger.info("Không có dữ liệu quẹt thẻ nào trên thiết bị.")
            
        # Bật lại thiết bị hoạt động bình thường
        conn.enable_device()
        
    except Exception as e:
        _logger.error(f"Lỗi trong quá trình giao tiếp với máy ZK: {e}")
    finally:
        if conn:
            conn.disconnect()
            _logger.info("Đã ngắt kết nối với máy ZKTeco.")

if __name__ == "__main__":
    main()
