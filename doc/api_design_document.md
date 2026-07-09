# Tài liệu Thiết kế API: Luồng Giao Tiếp từ Controller đến Backend

Tài liệu này đặc tả thiết kế bộ API phục vụ cho luồng giao tiếp giữa **Thiết bị điều khiển vật lý (Controller)** và **Hệ thống Backend (Odoo)** của module `t4_gate_keeper`.

---

## 1. Kiến Trúc Tổng Quan & Luồng Giao Tiếp

Hệ thống hoạt động theo cơ chế **Controller-initiated** (tất cả các kết nối đều do Controller vật lý khởi xướng lên Backend). Điều này giúp hệ thống hoạt động ổn định mà không cần mở cổng mạng (port forwarding) tại các chi nhánh.

Các API được khai báo sử dụng decorator `@endpoint` của framework `t4_coreapi`. Toàn bộ dữ liệu truyền tải sử dụng định dạng JSON.

---

## 2. Định Dạng Phản Hồi Chuẩn (Standard Response Format)

Theo quy định của `t4_coreapi`, định dạng phản hồi JSON chuẩn từ Backend sẽ như sau:

- **Thành công (Success):**
  ```json
  {
    "status": "200 OK",
    "message": "Successful",
    "data": { ... }
  }
  ```
- **Thất bại (Error):**
  ```json
  {
    "status": "401 Unauthorized, ",
    "message": "Nội dung lỗi chi tiết từ hệ thống",
    "data": null
  }
  ```

---

## 3. Chi Tiết Thiết Kế các Endpoint API

### 3.1 Nhóm Khởi động & Nhận Cấu hình

#### 3.1.1 `ControllerRegister` (Đăng ký / Xác thực Controller)

- **Mục đích**: Thiết bị gửi thông tin phần cứng khi khởi động hoặc cắm mạng lần đầu để hệ thống Backend ghi nhận địa chỉ mạng và kích hoạt trạng thái.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/controller-register`
- **Yêu cầu dữ liệu (Request Body)**:
  ```json
  {
    "controller_id": "CON-HW-998877",
    "hardware_model": "T4-GATE-PRO",
    "firmware_version": "v2.1.0",
    "ip_address": "192.168.1.15",
    "mac_address": "00:1B:44:11:3A:B7",
    "connection_type": "tcp_ip"
  }
  ```
- **Dữ liệu phản hồi (`data`)**:
  ```json
  {
    "message": "Success",
    "controller_id": 15,
    "name": "Bộ điều khiển Cổng Chính - Chi nhánh HN",
    "status": "200 OK"
  }
  ```
- **Quy trình xử lý tại Backend**:
  1. Kiểm tra sự tồn tại của `serial_number`.
  2. Tìm kiếm bản ghi `t4.gate_keeper.controller` tương ứng. Nếu không tìm thấy, từ chối (Chỉ cho phép thiết bị đã được khai báo trước bởi Admin kết nối).
  3. Cập nhật các thông số mạng (`ip_address`, `mac_address`, `firmware_version`) cùng thời gian hoạt động mới nhất `last_heartbeat_at = Datetime.now()`, đồng thời đặt `status = "online"`.
  4. Kích hoạt đổi trạng thái cascade cho tất cả thiết bị con đang ở trạng thái `controller_offline` sang `online`.

#### 3.1.2 `DeviceRegister` (Đăng ký / Xác thực Device)

- **Mục đích**: Thiết bị gửi thông tin phần cứng khi khởi động hoặc cắm mạng lần đầu để hệ thống Backend ghi nhận địa chỉ mạng và kích hoạt trạng thái.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/device-register`
- **Yêu cầu dữ liệu (Request Body)**:
  ```json
  {
    "device_sn": "DN91058915",
    "area": "Cổng trước/sau", //de minh set
    "device-model": "ZKTeco",
    "firmware_version": "v2.1.0",
    "port/channel": "relay_01",
    "firmware_version": "version01",
    "system_version": "version02"
  }
  ```
- **Dữ liệu phản hồi (`data`)**:
  ```json
  {
    "message": "Success",
    "status": "200 OK",
    "device_id": 15,
    "controller_name": "Bộ điều khiển Cổng Chính - Chi nhánh HN",
    "device_name": "Cửa ra/vào sảnh",
    "status": "200 OK"
  }
  ```
- **Quy trình xử lý tại Backend**:
  1. Kiểm tra sự tồn tại của `serial_number`.
  2. Tìm kiếm bản ghi `t4.gate_keeper.controller` tương ứng. Nếu không tìm thấy, từ chối (Chỉ cho phép thiết bị đã được khai báo trước bởi Admin kết nối).
  3. Cập nhật các thông số mạng (`ip_address`, `mac_address`, `firmware_version`) cùng thời gian hoạt động mới nhất `last_heartbeat_at = Datetime.now()`, đồng thời đặt `status = "online"`.
  4. Kích hoạt đổi trạng thái cascade cho tất cả thiết bị con đang ở trạng thái `controller_offline` sang `online`.

#### 3.1.3 `ControllerGetConfig` (Lấy cấu hình hoạt động)

- **Mục đích**: Tải thông số hoạt động chi tiết của Controller và danh sách các thiết bị con được kết nối trực tiếp.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/config`
- **Yêu cầu dữ liệu (Request Body)**:
  ```json
  {
    "serial_number": "CON-HW-998877"
  }
  ```
- **Dữ liệu phản hồi (`data`)**:
  ```json
  {
    "message": "Success",
    "status": "200 OK",
    "timezone": "Asia/Ho_Chi_Minh",
    "devices": [
      {
        "device_id": 42,
        "name": "Cửa ra/vào sảnh",
        "serial_number": "DEV-SN-556611",
        "port_or_channel": "relay_1",
        "supported_algorithms": [
          {
            "name": "ZKTeco Face 12.0",
            "type": "face",
            "version": "12.0"
          }
        ]
      },
      {
        "device_id": 43,
        "name": "Đầu đọc vân tay phụ",
        "serial_number": "DEV-SN-556612",
        "port_or_channel": "wiegand_2",
        "supported_algorithms": [
          {
            "name": "Finger 10.0",
            "type": "fingerprint",
            "version": "10.0"
          }
        ]
      }
    ]
  }
  ```
- **Quy trình xử lý tại Backend**:
  1. Tìm Controller dựa trên `serial_number`.
  2. Trích xuất múi giờ địa phương từ chi nhánh của Controller (`branch_id.timezone`).
  3. Tìm kiếm toàn bộ các thiết bị con liên kết thuộc model `t4.gate_keeper.device`.
  4. Trích xuất danh sách thuật toán sinh trắc học được hỗ trợ của từng thiết bị từ `device_model_id.algorithm_ids` để Controller biết loại định dạng dữ liệu sinh trắc học cần chuẩn bị.

---

### 3.2 Nhóm Giám sát Trạng thái (Keep-Alive)

#### 3.2.1 `ControllerHeartbeat`

- **Mục đích**: Định kỳ báo cáo trạng thái của Controller và các thiết bị con để phục vụ giám sát và xử lý cảnh báo lỗi.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/heartbeat`
- **Yêu cầu dữ liệu (Request Body)**:
  ```json
  {
    "controller_id": "CON-HW-998877", //controller_id
    "devices_status": [
      {
        "device_sn": "DEV-SN-556611", //device_sn
        "status": "online"
      },
      {
        "device_sn": "DEV-SN-556612", //device_sn
        "status": "offline"
      }
    ]
  }
  ```
- **Dữ liệu phản hồi (`data`)**:
  ```json
  {
    "message": "Success",
    "status": "200 OK"
  }
  ```
- **Quy trình xử lý tại Backend**:
  1. Cập nhật trường `last_heartbeat_at = Datetime.now()` và đặt `status = "online"` cho Controller tương ứng.
  2. Duyệt qua mảng `devices_status` để cập nhật trạng thái của từng bản ghi `t4.gate_keeper.device`:
     - Nếu thiết bị chuyển sang trạng thái ngoại tuyến (`offline` hoặc `controller_offline`) và thuộc một Khu vực (`area_id`), hệ thống kiểm tra và tự động tạo mới một cảnh báo loại `device_issue` (sự cố thiết bị) trong bảng `t4.gate_keeper.area_warning`.
     - Nếu thiết bị trực tuyến lại (`online`), hệ thống sẽ gọi phương thức `action_resolve()` để tự động đóng các cảnh báo ngoại tuyến liên quan của thiết bị này.

---

### 3.3 Nhóm Đồng bộ dữ liệu Nhân viên & Sinh trắc học

#### 3.3.1 `ControllerEmployeeSync` (Danh sách cập nhật nhân viên)

- **Mục đích**: Lấy danh sách mã nhân viên cần thêm mới, cập nhật hoặc xóa khỏi bộ nhớ thiết bị tính từ lần đồng bộ thành công gần nhất.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/employee-sync`
- **Yêu cầu dữ liệu (Request Body)**: //gioi han do lon paging
  ```json
  {
    "serial_number": "CON-HW-998877",
    "last_sync_at": "2026-07-02 08:00:00" //ko can
  }
  ```
- **Dữ liệu phản hồi (`data`)**:

  ```json
  {
    "message": "Success",
    "status": "200 OK",
    "sync_timestamp": "2026-07-02 08:32:00",
    "changes": [
      //truyen them cac thong tin khac
      {
        "emp_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "action": "update" //action cua odoo
      },
      {
        "emp_id": "8c2deb4d-4c7d-4cad-8cdd-3c0d7c3dcb7c",
        "action": "delete" //action cua odoo
      }
    ]
  }
  ```

  //2 phuong an
  //

- **Quy trình xử lý tại Backend**:
  1. Xác định chi nhánh của Controller để lọc đúng danh sách nhân viên thuộc chi nhánh đó (hoặc nhân viên được gán dùng chung cho toàn bộ hệ thống).
  2. So sánh `write_date` của bản ghi nhân viên (`t4.gate_keeper.employee`) với thời điểm `last_sync_at` để lọc danh sách các nhân viên cần ghi đè/thêm mới (`upsert`).
  3. Tìm kiếm các nhân viên đã bị xóa hoặc chuyển chi nhánh ra khỏi phạm vi của Controller để phát lệnh xóa (`delete`).

#### 3.3.2 `EmployeeBiometricGet` (Tải dữ liệu mẫu sinh trắc học)

- **Mục đích**: Tải dữ liệu vân tay/khuôn mặt/thẻ chi tiết của một nhân viên cụ thể về lưu vào bộ nhớ thiết bị.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/biometric`
- **Yêu cầu dữ liệu (Request Body)**:
  ```json
  {
    "controller_id": "CON-HW-998877", //controller_id
    "emp_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
  }
  ```
- **Dữ liệu phản hồi (`data`)**:
  ```json
  {
    "message": "Success",
    "status": "200 OK",
    "emp_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "name": "Nguyễn Văn A",
    "biometrics": [
      {
        "biometric_type": "fingerprint",
        "finger_index": 0, //0-9
        "algorithm_name": "Finger 10.0",
        "algorithm_version": "10.0",
        "template": "Base64StringOfFingerprintTemplateData..."
      },
      {
        "biometric_type": "face",
        "finger_index": 0,
        "algorithm_name": "ZKTeco Face 12.0",
        "algorithm_version": "12.0",
        "template": "Base64StringOfFaceTemplateData..."
      }
    ]
  }
  ```
- **Quy trình xử lý tại Backend**:
  1. Tìm bản ghi nhân viên dựa theo mã UUID duy nhất `emp_id` trong `t4.gate_keeper.employee`.
  2. Truy vấn dữ liệu liên kết từ bảng sinh trắc học `t4.gate_keeper.employee.biometric`.
  3. Lọc chỉ lấy các dữ liệu sinh trắc học có thuật toán tương thích với danh sách thuật toán của thiết bị con thuộc Controller hiện tại.
  4. Mã hóa trường dữ liệu nhị phân `template` sang chuỗi `Base64` để gửi đi an toàn qua JSON.

#### 3.3.3 `ControllerSyncAck` (Xác nhận hoàn thành đồng bộ)

- **Mục đích**: Controller xác nhận đã ghi nhận và nạp đầy đủ dữ liệu mới nhất thành công vào phần cứng.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/sync`
- **Yêu cầu dữ liệu (Request Body)**:
  ```json
  {
    "controller_id": "CON-HW-998877", //controller_id
    //"status": "success",
    "sync_timestamp": "2026-07-02 08:32:00"
  }
  ```
- **Dữ liệu phản hồi (`data`)**:
  ```json
  {
    "message": "Success",
    "status": "200 OK"
  }
  ```
- **Quy trình xử lý tại Backend**:
  1. Tìm kiếm Controller theo `serial_number`.
  2. Cập nhật trường `last_sync_at` của Controller bằng giá trị `sync_timestamp`.
  3. Khi đó, trường tính toán trạng thái đồng bộ nhân viên (`employee_sync_status`) của Controller tự động chuyển về trạng thái đồng bộ hoàn tất (`synced`).

---

### 3.4 Nhóm Nhật ký sự kiện & Cảnh báo an ninh

#### 3.4.1 `AccessLogUpload` (Tải lên lịch sử truy cập)

- **Mục đích**: Controller gửi hàng loạt sự kiện quét vân tay/khuôn mặt/thẻ thu thập được từ các thiết bị con về hệ thống Backend.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/log`
- **Yêu cầu dữ liệu (Request Body)**:
  ```json
  {
    "controller_id": "CON-HW-998877", //controller_id
    "logs": [
      {
        "device_serial": "DEV-SN-556611",
        "emp_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
        "access_time": "2026-07-02 18:30:00",
        "direction": "out", //ko day len (in, out, unknown)
        "verification_type": "face"
        //"status": "success"
      },
      {
        "device_serial": "DEV-SN-556611",
        "emp_id": "8c2deb4d-4c7d-4cad-8cdd-3c0d7c3dcb7c",
        "access_time": "2026-07-02 19:15:00",
        "direction": "in", //ko day len
        "verification_type": "fingerprint"
        //"status": "fail"
      }
    ]
  }
  ```
- **Dữ liệu phản hồi (`data`)**:
  ```json
  {
    "message": "Success",
    "status": "200 OK",
    "processed_count": 2
  }
  ```
- **Quy trình xử lý tại Backend**:
  1. Xác thực Controller dựa trên `serial_number`.
  2. Duyệt qua mảng `logs` để ánh xạ thông tin phần cứng sang bản ghi Odoo:
     - Ánh xạ `device_serial` tìm ra `device_id` (`t4.gate_keeper.device`).
     - Ánh xạ `emp_id` tìm ra `employee_id` (`t4.gate_keeper.employee`).
  3. Tạo mới bản ghi trong `t4.gate_keeper.access_log` với trạng thái `sync_status = "success"`.
  4. **Cơ chế Hook tự động kiểm tra bảo mật**:
     - Trong hàm tạo `create()` của `t4.gate_keeper.access_log`, hệ thống tự động kích hoạt hàm kiểm tra `_check_access_security_rules`.
     - Hệ thống chuyển đổi thời gian `access_time` sang giờ địa phương sử dụng Múi giờ của chi nhánh (`branch_id.timezone`).
     - Kiểm tra xem sự kiện có diễn ra vào các ngày cuối tuần (Thứ 7, Chủ nhật) hoặc ngoài khung giờ làm việc tiêu chuẩn (08:00 - 17:00).
     - Nếu phát hiện vi phạm giờ giấc và thiết bị con nằm trong một Khu vực (`area_id`), hệ thống sẽ tạo mới một cảnh báo trong bảng `t4.gate_keeper.area_warning` với loại cảnh báo là `invalid_access` nhằm đẩy lên màn hình giám sát trung tâm.

---

### 3.5 Nhóm Lệnh điều khiển từ xa (Pull-Command Queue)

Do tính chất các Controller vật lý nằm ở mạng nội bộ, cơ chế lấy lệnh từ xa sử dụng luồng kéo (polling).

#### 3.5.1 `ControllerCommandPoll` (Lấy lệnh điều khiển chờ thực thi) //ControllerCommandConfig

- **Mục đích**: Controller định kỳ (5-10 giây) gửi yêu cầu thăm dò để lấy các lệnh điều khiển khẩn cấp được kích hoạt từ Dashboard của Odoo.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/command`
- **Yêu cầu dữ liệu (Request Body)**:
  ```json
  {
    "controller_id": "CON-HW-998877"
  }
  ```
- **Dữ liệu phản hồi (`data`)**:
  ```json
  {
    "message": "Success",
    "status": "200 OK"
    "commands": [
      {
        "command_id": 1024,
        "action": "remote_open_door",
        "device_serial": "DEV-SN-556611",
        "parameters": {
          "hold_time_seconds": 15
        }
      }
    ]
  }
  ```
- **Quy trình xử lý tại Backend**:
  1. Tìm kiếm trong cơ sở dữ liệu các lệnh dành riêng cho Controller này đang ở trạng thái `pending`.
  2. Trả về danh sách lệnh và tự động chuyển trạng thái của lệnh sang `sending` để tránh trùng lặp.

#### 3.5.2 `ControllerCommandAck` (Xác nhận kết quả thực thi lệnh)

- **Mục đích**: Báo cáo lại kết quả thực thi lệnh điều khiển từ xa vật lý (Thành công / Thất bại) lên Odoo.
- **HTTP Method**: `POST`
- **Route**: `<domain>/<service code>/<version>/confirmation`
- **Yêu cầu dữ liệu (Request Body)**:
  ```json
  {
    "controller_id": "CON-HW-998877",
    "command_id": 1024,
    //"status": "success", //param command
    "execution_message": "Door was opened successfully for 15s."
  }
  ```
- **Dữ liệu phản hồi (`data`)**:
  ```json
  {
    "message": "Success",
    "status": "200 OK"
  }
  ```
- **Quy trình xử lý tại Backend**:
  1. Tìm bản ghi lệnh theo `command_id`.
  2. Cập nhật trạng thái lệnh (`status` = `"success"` hoặc `"failed"`) và lưu lại tin nhắn kết quả để cập nhật giao diện người dùng trên Odoo.

---

## 4. Các Nguyên Tắc An Toàn & Thiết Kế Bắt Buộc

1.  **Tính Độc Lập của Mã Định Danh (`emp_id`)**:
    Các API đồng bộ nhân viên sử dụng UUID v4 của trường `emp_id` thuộc model `t4.gate_keeper.employee`. Tuyệt đối không sử dụng mã định danh nhân viên của module HR Odoo (`hr.employee`). Việc này đảm bảo các chuỗi băm sinh trắc học đã lưu trên thiết bị không bị lỗi liên kết nếu mã nhân viên hành chính của Odoo HR bị sửa đổi.
2.  **Bảo mật dữ liệu Sinh trắc học**:
    Hệ thống backend tuyệt đối không được lưu hoặc in ra log (`_logger.info` / `_logger.warning`) các chuỗi ký tự thô đại diện cho mẫu vân tay/khuôn mặt (`template`) khi xử lý API nhằm bảo vệ thông tin cá nhân.
3.  **Xử lý Thời gian theo Múi giờ Chi nhánh**:
    Tất cả việc ghi nhận nhật ký và đánh giá vi phạm thời gian làm việc đều được thực hiện dựa trên trường `timezone` được lưu trữ tại `t4.gate_keeper.branch` thông qua hàm bổ trợ `check_outside_working_hours` để đảm bảo kết quả chính xác so với giờ địa phương của địa điểm lắp đặt thiết bị.

---

## 5. Ánh Xạ Task Redmine (Redmine Task Mapping)

Để phục vụ quản lý dự án trên Redmine, các công việc phát triển và tích hợp API được chia nhỏ thành các hạng mục (Issue/Task) chi tiết. Nhà phát triển có thể tham chiếu trực tiếp sơ đồ phân rã này để tạo và cập nhật trạng thái trên Redmine:

### [EPIC] Tích hợp giao tiếp API với Controller (Module 4)

#### 1. Nhóm Khởi động & Xác thực Thiết bị
*   **Redmine Task**: `[API] Hiện thực API Khởi động & Đăng ký thiết bị`
    *   **Subtask 1**: Viết endpoint `ControllerRegister` nhận dạng phần cứng Controller.
        *   *Vị trí file*: `models/gk_controller.py` (`@endpoint(name="ControllerRegister")`).
    *   **Subtask 2**: Viết endpoint `DeviceRegister` ghi nhận và gán cổng cho thiết bị con.
        *   *Vị trí file*: `models/gk_device.py` (`@endpoint(name="DeviceRegister")`).
    *   **Subtask 3**: Viết endpoint `ControllerGetConfig` xuất cấu hình múi giờ và thuật toán được hỗ trợ.
        *   *Vị trí file*: `models/gk_controller.py` (`@endpoint(name="ControllerGetConfig")`).

#### 2. Nhóm Giám sát Trạng thái (Heartbeat)
*   **Redmine Task**: `[API] Hiện thực API Giám sát Trạng thái & Ngoại tuyến`
    *   **Subtask**: Viết endpoint `ControllerHeartbeat` cập nhật `last_heartbeat_at`, đồng thời kích hoạt cảnh báo khu vực loại `device_issue` khi thiết bị ngoại tuyến.
        *   *Vị trí file*: `models/gk_controller.py` (`@endpoint(name="ControllerHeartbeat")`).

#### 3. Nhóm Đồng bộ Nhân sự & Sinh trắc học
*   **Redmine Task**: `[API] Hiện thực API Đồng bộ Hồ sơ & Biometric`
    *   **Subtask 1**: Viết endpoint `ControllerEmployeeSync` lọc danh sách thay đổi nhân sự (thêm/sửa/xóa) theo chi nhánh.
        *   *Vị trí file*: `models/gk_controller.py` (`@endpoint(name="ControllerEmployeeSync")`).
    *   **Subtask 2**: Viết endpoint `EmployeeBiometricGet` chuyển đổi và xuất chuỗi Base64 dữ liệu sinh trắc học vân tay/khuôn mặt.
        *   *Vị trí file*: `models/gk_employee.py` (`@endpoint(name="EmployeeBiometricGet")`).
    *   **Subtask 3**: Viết endpoint `ControllerSyncAck` ghi nhận thời điểm đồng bộ thành công `last_sync_at`.
        *   *Vị trí file*: `models/gk_controller.py` (`@endpoint(name="ControllerSyncAck")`).

#### 4. Nhóm Nhật ký quẹt thẻ & Cảnh báo an ninh
*   **Redmine Task**: `[API] Hiện thực API Tiếp nhận Nhật ký & Cảnh báo vi phạm`
    *   **Subtask**: Viết endpoint `AccessLogUpload` tiếp nhận hàng loạt sự kiện quét thẻ/biometric thô, chuẩn hóa lưu vào `t4.gate_keeper.access_log`, kích hoạt hook kiểm tra cảnh báo khu vực loại `invalid_access` (ngoài giờ hành chính, cuối tuần).
        *   *Vị trí file*: `models/gk_access_log.py` (`@endpoint(name="AccessLogUpload")`).

#### 5. Nhóm Lệnh điều khiển từ xa (Polling)
*   **Redmine Task**: `[API] Hiện thực API Gửi nhận Lệnh điều khiển từ xa`
    *   **Subtask 1**: Viết endpoint `ControllerCommandPoll` để Controller quét lấy lệnh `pending`.
        *   *Vị trí file*: `models/gk_controller.py` (`@endpoint(name="ControllerCommandPoll")`).
    *   **Subtask 2**: Viết endpoint `ControllerCommandAck` tiếp nhận phản hồi kết quả thực thi lệnh.
        *   *Vị trí file*: `models/gk_controller.py` (`@endpoint(name="ControllerCommandAck")`).

---

## 6. Hướng Dẫn Hiện Thực API cho Developer (README / Code Guide)

Để xây dựng hoặc bảo trì các Endpoint API trong phân hệ `t4_gate_keeper`, lập trình viên bắt buộc phải sử dụng framework **`t4_coreapi`** thay vì viết các HTTP controller (`http.Controller`) truyền thống của Odoo.

### 6.1 Các Thư Viện Cần Thiết
Import các helper functions và decorator trực tiếp vào Model của Odoo:
```python
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.addons.t4_coreapi.utils import (
    endpoint,     # Decorator đăng ký API
    get_body,     # Lấy Payload từ HTTP POST/PUT (JSON body)
    get_params,   # Lấy URL Query Parameters từ HTTP GET
)
import logging

_logger = logging.getLogger(__name__)
```

### 6.2 Khai Báo API Endpoint Trong Model
Các hàm xử lý API được khai báo trực tiếp như là các phương thức của Odoo Model. Giao thức HTTP routing và routing table sẽ được decorator `@endpoint` tự động đăng ký và ánh xạ.

#### Ví dụ 1: Hiện thực Endpoint `ControllerHeartbeat`
Hàm nhận trạng thái hoạt động định kỳ của bộ điều khiển:

```python
class GateKeeperController(models.Model):
    _name = "t4.gate_keeper.controller"
    _description = "Gate Keeper Controller"

    @endpoint(name="ControllerHeartbeat")
    def controller_heartbeat(self):
        """
        API Endpoint: Tiếp nhận trạng thái heartbeat từ bộ điều khiển.
        URL mẫu: /api/v1/controller-heartbeat
        """
        # 1. Đọc dữ liệu từ request body JSON
        body = get_body() or {}
        controller_id = body.get("controller_id")
        devices_status = body.get("devices_status", [])

        # 2. Kiểm tra dữ liệu đầu vào bắt buộc
        if not controller_id:
            return {
                "success": False,
                "message": _("Controller identifier (controller_id) is required.")
            }

        # 3. Tìm bản ghi bộ điều khiển tương ứng
        controller = self.search([("name", "=", controller_id)], limit=1)
        if not controller:
            return {
                "success": False,
                "message": _("Controller '%s' is not registered in the system.") % controller_id
            }

        try:
            # 4. Gọi xử lý nghiệp vụ nội bộ trong model
            controller._process_heartbeat(devices_status)
            
            # 5. Trả về phản hồi JSON chuẩn
            return {
                "success": True,
                "message": _("Heartbeat processed successfully.")
            }
        except Exception as e:
            _logger.error("Error processing heartbeat for %s: %s", controller_id, str(e))
            return {
                "success": False,
                "message": _("Internal server error occurred.")
            }
```

#### Ví dụ 2: Hiện thực Endpoint `AccessLogUpload`
Hàm tiếp nhận nhật ký sự kiện quẹt thẻ:

```python
class GateKeeperAccessLog(models.Model):
    _name = "t4.gate_keeper.access_log"
    _description = "Gate Keeper Access Log"

    @endpoint(name="AccessLogUpload")
    def access_log_upload(self):
        """
        API Endpoint: Tiếp nhận nhật ký quẹt thẻ của nhân viên từ thiết bị gửi lên.
        URL mẫu: /api/v1/access-log-upload
        """
        body = get_body() or {}
        controller_id = body.get("controller_id")
        logs = body.get("logs", [])

        if not controller_id or not logs:
            return {
                "success": False,
                "message": _("Missing controller_id or logs data.")
            }

        # Tìm bộ điều khiển để xác minh chi nhánh sở hữu
        controller = self.env["t4.gate_keeper.controller"].search([("name", "=", controller_id)], limit=1)
        if not controller:
            return {
                "success": False,
                "message": _("Controller not found.")
            }

        # Đẩy dữ liệu qua hàm xử lý lô (batch create) của model để đảm bảo hiệu năng
        processed_count = self._process_uploaded_logs(controller, logs)

        return {
            "success": True,
            "message": _("Access logs uploaded successfully."),
            "data": {
                "processed_count": processed_count
            }
        }
```

### 6.3 Quy Tắc Xử Lý Phản Hồi (Response Rules)
Khi phương thức được trang trí bởi `@endpoint` kết thúc:
1. **Nếu hàm trả về một Dictionary**:
   * Hệ thống tự động phân tích và chuyển đổi thành JSON response.
   * Nếu có trường `"success"` hoặc `"message"`, nó sẽ trích xuất và ánh xạ tương ứng.
   * Nếu không có các từ khóa chuẩn, toàn bộ dictionary sẽ được bọc lại trong trường `"data"`.
2. **Nếu hàm trả về kiểu dữ liệu khác (List, String, Boolean)**:
   * Framework `t4_coreapi` sẽ tự động đóng gói giá trị trả về đó vào trường `"data"` của cấu trúc JSON thành công tiêu chuẩn:
     ```json
     {
       "success": true,
       "message": "Successful",
       "data": <giá_trị_trả_về>
     }
     ```

### 6.4 Quy Tắc An Toàn Khi Coding API
* **Không dùng direct SQL**: Luôn sử dụng Odoo ORM (`search`, `create`, `write`) để đảm bảo tuân thủ Record Rules và Multi-company Security.
* **Không dùng `.sudo()` bừa bãi**: Chỉ sử dụng `.sudo()` khi thiết bị gọi API cần ghi nhận dữ liệu thuộc chi nhánh mà tài khoản tích hợp không có quyền ghi trực tiếp, và bắt buộc phải thêm comment giải thích rõ lý do.
* **Bảo mật logs**: Tuyệt đối không đưa trường dữ liệu sinh trắc học `template` (dưới dạng Base64 thô) vào hàm log `_logger.info` hay `_logger.warning`.
