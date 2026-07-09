# Cấu Trúc Issue Redmine Dự Án T4 Gate Keeper

Tài liệu này phân rã toàn bộ các tính năng, tác vụ lập trình (Feature) theo đúng kiến trúc và cấu trúc mã nguồn thực tế của dự án **T4 Gate Keeper** (Odoo 19 / Python 3 / PostgreSQL).

Mỗi **[PHẦN]** tương ứng với một **Epic**, mỗi **[NHÓM]** tương ứng với một **Parent Issue**, và mỗi **Feature** là một **Subtask** để import hoặc chỉnh sửa trực tiếp trên Redmine.

---

## PHẦN 0 — THIẾT LẬP DỰ ÁN VÀ CẤU HÌNH BAN ĐẦU
*Mục đích: Khởi tạo môi trường phát triển và cấu hình Redmine cho dự án.*

### [SETUP] Môi trường phát triển và Repo
* ├── **Feature**: Cài đặt Odoo 19 trên Docker local, kết nối PostgreSQL thành công.
  * **Mô tả chi tiết**: Khởi tạo file Docker Compose chạy Odoo 19 kết hợp PostgreSQL 16. Phân bổ cổng và cấu hình volume lưu trữ DB.
* ├── **Feature**: Tạo Git repository, cấu hình file `.gitignore` loại bỏ các file thừa Odoo.
  * **Mô tả chi tiết**: Khởi tạo Git repo, tạo các nhánh `main`, `develop`. Thêm `.gitignore` chặn các file `.pyc`, thư mục `.idea`, log và cache của Odoo.
* └── **Feature**: Tích hợp module nền tảng `t4_coreapi` vào thư mục addons, kích hoạt không lỗi.
  * **Mô tả chi tiết**: Cài đặt module `t4_coreapi` vào hệ thống, cập nhật danh sách module và cài đặt thử để kiểm tra tính tương thích hệ thống.

### [DOC] Tài liệu đặc tả hệ thống Gatekeeper (#11339)
* ├── **[DOC] Tài liệu SRS - Đặc tả yêu cầu phần mềm (#11340)**
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Tài liệu hóa toàn bộ yêu cầu nghiệp vụ và kỹ thuật của hệ thống kiểm soát ra vào Gate Keeper phục vụ cho các bên liên quan (Khách hàng, Lập trình viên, Tester).
    - *Nội dung chính*:
      - Đặc tả chi tiết các Use Case cốt lõi: Quản lý chi nhánh & khu vực; Quản lý Controller & Device con; Đồng bộ nhân viên từ HR hành chính; Tiếp nhận sự kiện Access Log; Đánh giá và tạo cảnh báo an ninh Area Warning.
      - Xác định rõ các tác nhân sử dụng hệ thống (Actor): Admin, Guard (Bảo vệ), Technician (Kỹ thuật viên) kèm theo ma trận phân quyền truy cập.
      - Định nghĩa các Tiêu chí chấp nhận (Acceptance Criteria) cho từng tính năng để làm cơ sở nghiệm thu sản phẩm.
* ├── **[DOC] Tài liệu ERD - Sơ đồ quan hệ dữ liệu (#11341)**
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Thiết kế và tài liệu hóa cấu trúc cơ sở dữ liệu vật lý của phân hệ Gate Keeper trên hệ quản trị PostgreSQL.
    - *Nội dung chính*:
      - Sơ đồ ERD trực quan (vẽ bằng draw.io hoặc dbdiagram.io) thể hiện mối liên kết giữa các bảng.
      - Đặc tả chi tiết từng bảng dữ liệu (Table Schema): `t4.gate_keeper.branch`, `t4.gate_keeper.area`, `t4.gate_keeper.controller`, `t4.gate_keeper.device`, `t4.gate_keeper.device_model`, `t4.gate_keeper.algorithm`, `t4.gate_keeper.employee`, `t4.gate_keeper.auth_info`, `t4.gate_keeper.employee.biometric`, `t4.gate_keeper.access_log`, `t4.gate_keeper.area_warning`, `t4.gate_keeper.alert_policy`...
      - Quy định rõ kiểu dữ liệu, các thuộc tính bắt buộc (required/nullable), khóa ngoại (Many2one), bảng liên kết Many2many, khóa chính và các ràng buộc duy nhất (Unique Constraints).
* ├── **[DOC] Tài liệu API - Thiết kế kết nối thiết bị (#11342)**
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Đặc tả chi tiết giao tiếp HTTP giữa Odoo Server và các Bộ điều khiển vật lý (Controller), làm tài liệu hướng dẫn cho lập trình viên nhúng phần cứng và lập trình viên Backend Odoo.
    - *Nội dung chính*:
      - Tài liệu hóa chi tiết cấu trúc JSON Request/Response của 10 API kết nối (đầu vào, đầu ra thành công/lỗi).
      - Hướng dẫn cấu trúc framework nền tảng `t4_coreapi`, cách sử dụng decorator `@endpoint`, cách lấy dữ liệu qua `get_body()` và `get_params()`.
      - Cơ chế bảo mật và xác thực gói tin từ thiết bị vật lý gửi lên hệ thống.
* ├── **[DOC] Tài liệu hướng dẫn sử dụng (#11343)**
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Hướng dẫn vận hành hệ thống Gate Keeper trên Odoo cho các bộ phận người dùng thực tế.
    - *Nội dung chính*:
      - **Dành cho Quản trị viên (Admin)**: Hướng dẫn khai báo chi nhánh, khu vực lắp đặt, thiết bị phần cứng, cấp phát thẻ RFID/biometric cho nhân viên, và thiết lập khung giờ giới hạn trong chính sách bảo mật.
      - **Dành cho Bảo vệ / Trực ban (Guard)**: Hướng dẫn giám sát danh sách sự kiện quẹt thẻ thời gian thực, theo dõi tình trạng cảnh báo an ninh khu vực, cách bấm nút đóng/giải quyết cảnh báo (Action Resolve Warning) và ghi nhận lý do.
      - **Dành cho Kỹ thuật viên (Technician)**: Hướng dẫn cấu hình kết nối mạng cho Controller, theo dõi trạng thái thiết bị con (online/offline) và kiểm tra nhật ký thô (Device Log) khi xảy ra lỗi.
* └── **[DOC] Tài liệu Kiểm thử Test Case (#11344)**
  * ├── **Feature #11345**: Viết bảng Test Case cho từng Use Case theo từng Tiêu chí Chấp nhận (Acceptance Criteria) trong SRS.
    - **Mô tả chi tiết**:
      - Xây dựng bảng kịch bản kiểm thử chi tiết (Excel/Markdown) cho toàn bộ 5 Module nghiệp vụ cốt lõi.
      - Xác định rõ các điều kiện tiền đề (Pre-conditions), các bước thực hiện (Steps), dữ liệu đầu vào (Test Data) và kết quả mong đợi (Expected Results).
  * ├── **Feature #11346**: Phân loại test case theo mức độ ưu tiên (Smoke test, Functional test, Edge case, Security/Timezone test).
    - **Mô tả chi tiết**:
      - Thiết lập ma trận phân chia mức độ quan trọng để tối ưu hóa thời gian chạy test (Smoke test chạy khi deploy nhanh, Functional test chạy khi nghiệm thu).
      - Thiết kế các ca kiểm thử biên (Edge cases) như: quẹt thẻ vào đúng 08:00 hoặc 17:00, quẹt thẻ liên tiếp nhiều lần tại cùng 1 đầu đọc, kiểm thử múi giờ chi nhánh lệch múi giờ máy chủ Odoo.
  * └── **Feature #11347**: Tạo bộ test API để dev tự kiểm tra luồng nhận dữ liệu từ thiết bị.
    - **Mô tả chi tiết**:
      - Xây dựng và đóng gói bộ Postman Collection hoặc các tệp `.http` chứa sẵn payload mẫu của 10 API kết nối.
      - Thiết lập sẵn các biến môi trường (Base URL, Secret Key) để dev có thể dễ dàng chạy giả lập các sự kiện gửi nhịp tim, đăng ký thiết bị con, gửi log quẹt thẻ và nhận lệnh điều khiển từ xa ngay trên môi trường local.

---

## PHẦN 1 — MODULE 1: QUẢN LÝ CHI NHÁNH VÀ KHU VỰC (t4_gate_keeper)
*Mục đích: Thiết lập hạ tầng địa lý và khu vực giám sát (Model: Branch, Area).*

### [MODEL] Xây dựng model Branch (Chi nhánh)
* ├── **Feature #11364**: Tạo class `GateKeeperBranch` (`t4.gate_keeper.branch` trong `models/gk_branch.py`) với đầy đủ field cơ bản (`name`, `code`, `address`, `active`, `timezone`).
  * **Mô tả chi tiết**: Khai báo các trường: Tên chi nhánh, Mã định danh (unique), Địa chỉ, Trạng thái kích hoạt (Boolean), và Múi giờ địa phương (`timezone` sử dụng pytz selection).
* ├── **Feature #11365**: Thêm ràng buộc duy nhất cho mã chi nhánh và Chặn xóa chi nhánh khi còn khu vực bên trong.
  * **Mô tả chi tiết**: Thêm constraint SQL `@api.constrains` kiểm tra duy nhất cho `code`. Viết hàm ghi đè `unlink()` để kiểm tra nếu chi nhánh còn chứa Area con thì không cho phép xóa và đưa ra cảnh báo lỗi (ValidationError).
* └── **Feature #11366**: Nhập dữ liệu mẫu 2-3 chi nhánh để test giao diện.
  * **Mô tả chi tiết**: Khởi tạo file data XML (`data/gk_branch_data.xml` hoặc tương đương) nạp sẵn 3 chi nhánh mẫu (Hà Nội, Đà Nẵng, TP.HCM) để phục vụ kiểm thử.

### [MODEL] Xây dựng model Area (Khu vực)
* ├── **Feature #11367**: Tạo class `GateKeeperArea` (`t4.gate_keeper.area` trong `models/gk_area.py`) liên kết Many2one với `branch_id` và các trường tính toán trạng thái động.
  * **Mô tả chi tiết**: Khai báo model Khu vực gồm: `name` (Tên khu vực), `branch_id` (Many2one với Chi nhánh), `status` (computed selection: `normal`/`warning` phụ thuộc vào sự tồn tại của cảnh báo đang hoạt động), và `warning_count` (computed đếm số cảnh báo).
* ├── **Feature #11368**: Liên kết khu vực với chi nhánh và thêm ràng buộc tên khu vực không trùng trong cùng một chi nhánh.
  * **Mô tả chi tiết**: Thiết lập mối liên hệ Many2one với Branch. Viết hàm kiểm tra constraint Python đảm bảo trong cùng một chi nhánh không được phép tồn tại hai khu vực trùng tên nhau.
* └── **Feature #11369**: Nhập dữ liệu mẫu 4-5 khu vực để test.
  * **Mô tả chi tiết**: Nạp sẵn các khu vực mẫu thông qua file XML dữ liệu demo (ví dụ: Phòng R&D, Kho thành phẩm, Sảnh chính, Phòng Server) thuộc các chi nhánh khác nhau.

### [VIEW] Xây dựng giao diện quản lý chi nhánh
* ├── **Feature #11370**: Trang list view danh sách chi nhánh dạng bảng hiển thị tên, mã chi nhánh, địa chỉ và trạng thái hoạt động (`views/gk_branch_views.xml`).
  * **Mô tả chi tiết**: Thiết kế List view hiển thị dạng bảng gồm các trường cơ bản. Cho phép tìm kiếm nhanh theo Tên hoặc Mã chi nhánh.
* ├── **Feature #11371**: Trang form view chi tiết chi nhánh hiển thị thông tin đầy đủ kèm danh sách khu vực con bên dưới.
  * **Mô tả chi tiết**: Thiết kế giao diện Form view gồm 2 nhóm chính: Thông tin chung (Tên, Mã, Múi giờ, Địa chỉ) và Danh sách Khu vực (thể hiện qua trường One2many hiển thị dạng bảng trực quan).
* └── **Feature #11372**: Ô tìm kiếm và lọc chi nhánh theo tên, mã hoặc trạng thái.
  * **Mô tả chi tiết**: Cấu hình thẻ `<search>` trong XML view, hỗ trợ các filter nhanh theo trạng thái kích hoạt (`active = True`/`False`) và gom nhóm (group by) theo múi giờ.

### [VIEW] Xây dựng giao diện quản lý khu vực
* ├── **Feature #11373**: Trang list view danh sách khu vực lọc theo từng chi nhánh (`views/gk_area_views.xml`).
  * **Mô tả chi tiết**: Tạo list view hiển thị: Tên khu vực, Chi nhánh quản lý, Trạng thái cảnh báo. Hỗ trợ ô tìm kiếm và panel lọc nhanh theo Chi nhánh.
* ├── **Feature #11374**: Trang form view chi tiết khu vực hiển thị danh sách thiết bị con và danh sách cảnh báo khu vực liên quan.
  * **Mô tả chi tiết**: Thiết kế Form view khu vực chứa: Thông tin chung, Danh sách Thiết bị lắp đặt tại khu vực này (One2many) và Danh sách các Cảnh báo vi phạm (One2many) đang hoạt động.
* └── **Feature #11375**: Hiển thị trực quan trạng thái cảnh báo khu vực (normal/warning) ngay trên trang danh sách list view.
  * **Mô tả chi tiết**: Cấu hình widget trang trí màu sắc (ví dụ: đỏ/vàng khi trạng thái là `warning`, xanh khi trạng thái là `normal`) bằng các class CSS bootstrap hoặc Odoo ribbon trên list/kanban view.

### [ACCESS] Phân quyền module chi nhánh và khu vực
* ├── **Feature #11376**: Cấu hình quyền Admin - toàn quyền chi nhánh và khu vực (`security/ir.model.access.csv`).
  * **Mô tả chi tiết**: Ghi nhận cấu hình phân quyền trong file CSV, cấp đầy đủ quyền Đọc, Ghi, Tạo, Xóa (1,1,1,1) cho nhóm người dùng quản trị Gate Keeper Admin.
* ├── **Feature #11377**: Cấu hình quyền Bảo vệ và Kỹ thuật viên - chỉ được xem chi nhánh và khu vực.
  * **Mô tả chi tiết**: Định cấu hình phân quyền chỉ cho phép Đọc (1,0,0,0) đối với vai trò Bảo vệ (Guard) và Kỹ thuật viên (Technician) đối với hai model Branch và Area.
* └── **Feature #11378**: Kiểm tra phân quyền đúng theo từng vai trò.
  * **Mô tả chi tiết**: Đăng nhập bằng các tài khoản kiểm thử đại diện cho từng phân quyền để xác minh hành vi chặn thêm mới/chỉnh sửa của nhân viên Bảo vệ đối với Chi nhánh.

---

## PHẦN 2 — MODULE 2: QUẢN LÝ BỘ ĐIỀU KHIỂN VÀ THIẾT BỊ
*Mục đích: Quản lý hạ tầng thiết bị phần cứng (Model: Controller, Device, Device Model, Algorithm).*

### [MODEL] Cơ sở dữ liệu Bộ điều khiển và Thiết bị
* ├── **Feature**: Tạo model Bộ điều khiển `t4.gate_keeper.controller` (`models/gk_controller.py`)
  * **Mô tả chi tiết**: Khai báo các trường: Tên, Số seri vật lý (`serial_number`, unique), địa chỉ IP, địa chỉ MAC, giao thức kết nối (`connection_type`), phiên bản phần mềm nhúng (`firmware_version`), trạng thái kết nối (`online/offline`), thời điểm nhịp tim cuối (`last_heartbeat_at`), thời điểm đồng bộ thành công gần nhất (`last_sync_at`), liên kết Chi nhánh (`branch_id`) và Công ty (`company_id`).
* ├── **Feature**: Tạo model Thiết bị con `t4.gate_keeper.device` (`models/gk_device.py`)
  * **Mô tả chi tiết**: Khai báo thiết bị con trực thuộc bộ điều khiển, gồm: Tên thiết bị, số seri thiết bị con (`serial_number`), cổng kết nối vật lý trên bộ điều khiển (`port_or_channel`), trạng thái hoạt động (`online`/`offline`/`controller_offline`), liên kết Many2one với bộ điều khiển cha (`controller_id`), liên kết Many2one khu vực lắp đặt (`area_id`), và liên kết Many2one với model thiết bị (`device_model_id`).
* └── **Feature**: Tạo các model phụ trợ Model thiết bị và Thuật toán sinh trắc học
  * **Mô tả chi tiết**: 
    - Tạo model `t4.gate_keeper.device_model` (`models/gk_device_model.py`) lưu thông tin hãng sản xuất thiết bị (ZKTeco, Hikvision, Dahua).
    - Tạo model `t4.gate_keeper.algorithm` (`models/gk_algorithm.py`) lưu danh sách các thuật toán sinh trắc học được hỗ trợ (Face v12.0, Finger v10.0).
    - Thiết lập liên kết Many2many giữa hai bảng này để xác định cấu hình thuật toán khả dụng của từng dòng máy.

### [LOGIC] Logic trạng thái và Tác vụ tự động (Scheduler)
* ├── **Feature**: Viết cơ chế cascade trạng thái kết nối
  * **Mô tả chi tiết**: Viết hàm ghi đè `write()` trên model `t4.gate_keeper.controller`. Khi trạng thái Controller chuyển sang `online`, tự động cập nhật trạng thái các thiết bị con của nó đang ở trạng thái `controller_offline` chuyển sang `online`. Khi Controller chuyển sang trạng thái ngoại tuyến (`offline`), tự động cập nhật toàn bộ thiết bị con sang trạng thái `controller_offline`.
* └── **Feature**: Cấu hình Scheduled Action tự động quét trạng thái thiết bị ngoại tuyến
  * **Mô tả chi tiết**: Khai báo một `ir.cron` (`data/scheduler_cron.xml`) chạy mỗi 5 phút. Logic cron gọi phương thức kiểm tra trong `models/gk_scheduler.py` để tìm các bộ điều khiển `online` chưa gửi heartbeat quá 15 phút, tự động chuyển chúng sang `offline` và cập nhật thiết bị con tương ứng.

### [VIEW] Giao diện quản lý Thiết bị phần cứng
* ├── **Feature**: Thiết kế List view và Form view cho Bộ điều khiển (`views/gk_controller_views.xml`)
  * **Mô tả chi tiết**: List view hiển thị: Tên, Số seri, Trạng thái kết nối, Chi nhánh, Thời điểm heartbeat cuối. Form view phân nhóm thông tin cấu hình mạng, hiển thị danh sách thiết bị con trực thuộc (One2many).
* ├── **Feature**: Thiết kế List view và Form view cho Thiết bị (`views/gk_device_views.xml`)
  * **Mô tả chi tiết**: List view hiển thị trạng thái thiết bị con bằng màu sắc trực quan (widget status). Form view cho phép cấu hình chọn bộ điều khiển cha quản lý, khu vực lắp đặt và dòng máy (device model) tương thích.
* ├── **Feature**: Thiết kế giao diện giám sát trạng thái đồng bộ nhân sự của Bộ điều khiển (`views/gk_controller_sync_views.xml`)
  * **Mô tả chi tiết**: Xây dựng List view chuyên biệt để theo dõi nhanh trạng thái đồng bộ nhân viên (`employee_sync_status` hiển thị badge `synced` hoặc `out_of_sync`) và thời điểm đồng bộ thành công cuối cùng (`last_sync_at`) của từng Controller.
* └── **Feature**: Thiết kế List view và Form view cho Dòng máy và Thuật toán (`views/gk_device_model_views.xml`, `views/gk_algorithm_views.xml`)
  * **Mô tả chi tiết**: Thiết kế giao diện cơ bản cho model `t4.gate_keeper.device_model` và `t4.gate_keeper.algorithm` để Admin khai báo các dòng máy chấm công và phiên bản thuật toán nhận diện tương ứng trong hệ thống.

---

## PHẦN 3 — MODULE 3: QUẢN LÝ NHÂN SỰ VÀ THÔNG TIN XÁC THỰC
*Mục đích: Quản lý hồ sơ nhân sự, nhóm và sinh trắc học (Model: Employee, Auth Info, Employee Biometric, Employee Group).*

### [MODEL] Cơ sở dữ liệu Nhân sự và Xác thực
* ├── **Feature**: Tạo model Nhân sự Gate Keeper `t4.gate_keeper.employee` (`models/gk_employee.py`)
  * **Mô tả chi tiết**: Khai báo model nhân sự độc lập với HR hành chính, gồm các trường: Tên nhân sự, Mã định danh phần cứng duy nhất (`emp_id`, unique, sinh tự động UUID v4), Trạng thái hiện diện computed (`inside`/`outside`/`unknown`), Khu vực hiện tại computed (`current_area_id`), liên kết Chi nhánh (`branch_id`), ảnh chân dung (`avatar`), và danh sách thẻ RFID/sinh trắc học liên kết.
* ├── **Feature**: Tạo model Thẻ từ RFID `t4.gate_keeper.auth_info` (`models/gk_auth_info.py`)
  * **Mô tả chi tiết**: Lưu trữ mã thẻ vật lý gán cho nhân viên: Mã thẻ (`card_code`, unique), trạng thái thẻ (`active` Boolean), liên kết Many2one với nhân viên sở hữu (`employee_id`), và ghi chú chi tiết.
* ├── **Feature**: Tạo model Sinh trắc học `t4.gate_keeper.employee.biometric` (`models/gk_employee_biometric.py`)
  * **Mô tả chi tiết**: Lưu dữ liệu vân tay hoặc khuôn mặt thô phục vụ đồng bộ xuống thiết bị vật lý: Loại sinh trắc học (vân tay/khuôn mặt), chỉ số ngón tay (`finger_index` 0-9), thuật toán tương thích (`algorithm_id` Many2one), và chuỗi dữ liệu mẫu (`template` nhị phân).
* └── **Feature**: Tạo model Nhóm nhân sự `t4.gate_keeper.employee_group` (`models/gk_employee_group.py`)
  * **Mô tả chi tiết**: Tạo bảng nhóm để gán phân quyền ra vào khu vực: Tên nhóm, Mã nhóm (`code`, unique), chi nhánh áp dụng, và liên kết Many2many với danh sách nhân viên (`employee_ids`).

### [LOGIC] Đồng bộ tuyệt đối từ phân hệ HR Odoo
* ├── **Feature**: Kế thừa model `hr.employee` để tự động đồng bộ nhân sự sang Gate Keeper (`models/hr_employee.py`)
  * **Mô tả chi tiết**: Viết hàm ghi đè `create()` và `write()` trên model gốc `hr.employee` của Odoo. Khi có nhân sự mới được tạo ở HR hoặc chỉnh sửa thông tin hành chính, hệ thống tự động kiểm tra, tạo hoặc cập nhật hồ sơ tương ứng bên `t4.gate_keeper.employee`.
* └── **Feature**: Cấu hình ẩn nút thêm mới "New" trên giao diện Gate Keeper Employee (`views/gk_employee_views.xml`)
  * **Mô tả chi tiết**: Cấu hình thuộc tính `create="0"` trong các thẻ `<list>`, `<kanban>`, và `<form>` của model `t4.gate_keeper.employee` để khóa cứng giao diện, ngăn người dùng tạo thủ công làm lệch dữ liệu với phân hệ HR.

### [VIEW] Giao diện quản lý Nhân sự và Nhóm
* ├── **Feature**: Thiết kế giao diện kế thừa hồ sơ HR Employee (`views/hr_employee_views.xml`)
  * **Mô tả chi tiết**: Kế thừa Form view của `hr.employee` để hiển thị thêm tab cấu hình Gate Keeper (Mã định danh `emp_id` sinh trắc học riêng, trạng thái đồng bộ) giúp Admin dễ dàng tra cứu.
* ├── **Feature**: Thiết kế List view và Form view cho Nhóm nhân sự (`views/gk_employee_group_views.xml`)
  * **Mô tả chi tiết**: Tạo giao diện cho model `t4.gate_keeper.employee_group` để cấu hình danh sách nhân viên thuộc nhóm và chi nhánh quản lý tương ứng.
* └── **Feature**: Thiết kế List view và Form view cho Thẻ RFID và Sinh trắc học (`views/gk_auth_info_views.xml`, `views/gk_employee_biometric_views.xml`)
  * **Mô tả chi tiết**: Thiết kế giao diện cơ bản cho model `t4.gate_keeper.auth_info` (quản lý thẻ từ RFID) và model `t4.gate_keeper.employee.biometric` (quản lý/tra cứu dữ liệu vân tay/khuôn mặt thô của từng nhân sự).

---

## PHẦN 4 — MODULE 4: TIẾP NHẬN DỮ LIỆU TỪ CONTROLLER (INTEGRATION)
*Mục đích: Tiếp nhận và xử lý các yêu cầu HTTP từ các bộ điều khiển vật lý.*

### [API] Khai báo các Endpoint kết nối
* ├── **Feature**: Đăng ký và hiện thực API ControllerRegister
  * **Mô tả chi tiết**:
    - *Mục đích*: Thiết bị gửi thông tin phần cứng khi khởi động hoặc cắm mạng lần đầu để Backend ghi nhận IP/MAC và kích hoạt trạng thái.
    - *HTTP Method & Route*: `POST` `/api/v1/controller-register` (hoặc thông qua `t4_coreapi` registry).
    - *Payload*: `controller_id`, `hardware_model`, `firmware_version`, `ip_address`, `mac_address`, `connection_type`.
    - *Logic xử lý*: Tra cứu bản ghi `t4.gate_keeper.controller` theo serial. Nếu tồn tại, cập nhật IP/MAC và đổi `status` sang `online`, đặt `last_heartbeat_at = Datetime.now()`. Cascade chuyển các thiết bị con từ `controller_offline` sang `online`.
* ├── **Feature**: Đăng ký và hiện thực API DeviceRegister
  * **Mô tả chi tiết**:
    - *Mục đích*: Đăng ký các thiết bị con kết nối trực tiếp với bộ điều khiển vật lý.
    - *HTTP Method & Route*: `POST` `/api/v1/device-register`
    - *Payload*: `device_sn`, `area`, `device-model`, `firmware_version`, `port/channel`.
    - *Logic xử lý*: Tra cứu thiết bị con trong `t4.gate_keeper.device` theo mã serial (`device_sn`), cập nhật trạng thái `online`, liên kết với khu vực tương ứng.
* ├── **Feature**: Đăng ký và hiện thực API ControllerGetConfig
  * **Mô tả chi tiết**:
    - *Mục đích*: Cho phép Controller tải cấu hình múi giờ chi nhánh sở hữu và danh sách thuật toán sinh trắc học được hỗ trợ của các thiết bị con trực thuộc.
    - *HTTP Method & Route*: `POST` `/api/v1/config`
    - *Payload*: `serial_number`.
    - *Logic xử lý*: Trích xuất múi giờ địa phương từ chi nhánh của Controller (`branch_id.timezone`) và danh sách thuật toán sinh trắc học được hỗ trợ của từng thiết bị con từ `device_model_id.algorithm_ids`.
* ├── **Feature**: Đăng ký và hiện thực API ControllerHeartbeat
  * **Mô tả chi tiết**:
    - *Mục đích*: Nhận nhịp tim định kỳ từ bộ điều khiển để kiểm tra tình trạng kết nối.
    - *HTTP Method & Route*: `POST` `/api/v1/heartbeat`
    - *Payload*: `controller_id`, mảng `devices_status` (gồm `device_sn` và `status` của từng thiết bị con).
    - *Logic xử lý*: Cập nhật `last_heartbeat_at = Datetime.now()` và đặt trạng thái Controller là `online`. Duyệt mảng `devices_status` để cập nhật trạng thái thiết bị con. Nếu thiết bị con offline và thuộc khu vực, tự động tạo Area Warning loại `device_issue`. Nếu trực tuyến lại, tự động đóng cảnh báo.
* ├── **Feature**: Đăng ký và hiện thực API ControllerEmployeeSync
  * **Mô tả chi tiết**:
    - *Mục đích*: Trả về danh sách nhân viên thay đổi hoặc cần xóa khỏi thiết bị tính từ lần đồng bộ trước.
    - *HTTP Method & Route*: `POST` `/api/v1/employee-sync`
    - *Payload*: `serial_number`, `last_sync_at`.
    - *Logic xử lý*: So sánh `write_date` của bản ghi nhân viên (`t4.gate_keeper.employee`) với thời điểm `last_sync_at` để lọc danh sách các nhân viên cần ghi đè/thêm mới (`action = "update"`) hoặc cần xóa (`action = "delete"`).
* ├── **Feature**: Đăng ký và hiện thực API EmployeeBiometricGet
  * **Mô tả chi tiết**:
    - *Mục đích*: Tải dữ liệu vân tay/khuôn mặt/thẻ chi tiết của một nhân viên cụ thể.
    - *HTTP Method & Route*: `POST` `/api/v1/biometric`
    - *Payload*: `controller_id`, `emp_id`.
    - *Logic xử lý*: Tìm bản ghi nhân viên dựa theo mã UUID duy nhất `emp_id`. Truy vấn dữ liệu liên kết từ bảng sinh trắc học `t4.gate_keeper.employee.biometric`. Lọc chỉ lấy các dữ liệu sinh trắc học có thuật toán tương thích. Mã hóa trường dữ liệu nhị phân `template` sang chuỗi `Base64`.
* ├── **Feature**: Đăng ký và hiện thực API ControllerSyncAck
  * **Mô tả chi tiết**:
    - *Mục đích*: Controller gửi xác nhận nạp dữ liệu hoàn tất, cập nhật lại thời điểm đồng bộ thành công gần nhất.
    - *HTTP Method & Route*: `POST` `/api/v1/sync`
    - *Payload*: `controller_id`, `sync_timestamp`.
    - *Logic xử lý*: Tìm Controller theo `serial_number` và cập nhật trường `last_sync_at = sync_timestamp`. Khi đó, trường tính toán trạng thái đồng bộ nhân viên (`employee_sync_status`) của Controller tự động chuyển về trạng thái đồng bộ hoàn tất (`synced`).
* ├── **Feature**: Đăng ký và hiện thực API AccessLogUpload
  * **Mô tả chi tiết**:
    - *Mục đích*: Tiếp nhận mảng log quẹt thẻ để lưu trữ và kiểm tra vi phạm bảo mật.
    - *HTTP Method & Route*: `POST` `/api/v1/log`
    - *Payload*: `controller_id`, mảng `logs` (gồm `device_serial`, `emp_id`, `access_time`, `direction`, `verification_type`).
    - *Logic xử lý*: Tra cứu thiết bị con theo `device_serial` để ra `device_id`, tra cứu nhân viên theo `emp_id` để ra `employee_id`. Tạo mới bản ghi trong `t4.gate_keeper.access_log` với trạng thái `sync_status = "success"`. Trong hàm `create()` của `t4.gate_keeper.access_log`, hệ thống tự động kiểm tra chính sách vi phạm giờ giấc ra vào, timezone địa phương và sinh Area Warning nếu vi phạm.
* ├── **Feature**: Đăng ký và hiện thực API ControllerCommandPoll
  * **Mô tả chi tiết**:
    - *Mục đích*: Bộ điều khiển gọi định kỳ (5-10s) quét tìm các lệnh mở cửa từ xa đang ở trạng thái `pending`.
    - *HTTP Method & Route*: `POST` `/api/v1/command`
    - *Payload*: `controller_id`.
    - *Logic xử lý*: Tìm kiếm các lệnh dành riêng cho Controller này đang ở trạng thái `pending`. Trả về danh sách lệnh và tự động chuyển trạng thái của lệnh sang `sending` để tránh trùng lặp.
* └── **Feature**: Đăng ký và hiện thực API ControllerCommandAck
  * **Mô tả chi tiết**:
    - *Mục đích*: Bộ điều khiển gửi phản hồi báo cáo kết quả thực thi lệnh mở cửa từ xa.
    - *HTTP Method & Route*: `POST` `/api/v1/confirmation`
    - *Payload*: `controller_id`, `command_id`, `execution_message`.
    - *Logic xử lý*: Tìm bản ghi lệnh theo `command_id`, cập nhật trạng thái lệnh sang `success` hoặc `failed` và lưu lại tin nhắn kết quả (`execution_message`) lên Odoo.

### [LOGIC] Nhật ký thiết bị thô (Device Log) và Xử lý Batch
* ├── **Feature**: Tạo model Nhật ký thiết bị thô `t4.gate_keeper.device_log` (`models/gk_device_log.py`)
  * **Mô tả chi tiết**: Tạo bảng lưu trữ thô: Lưu mã serial, chuỗi dữ liệu JSON thô gửi từ thiết bị, và trạng thái xử lý (`processed`/`failed`). Nhằm lưu trữ vết nguyên bản phục vụ phân tích lỗi khi tích hợp.
* └── **Feature**: Xây dựng logic xử lý batch offline
  * **Mô tả chi tiết**: Viết logic xử lý khi thiết bị gửi lên hàng loạt log lưu trữ offline: Backend parse danh sách, sắp xếp tăng dần theo thời gian trước khi gọi hàm xử lý lô (batch create) để tránh xung đột thứ tự dữ liệu.

### [VIEW] Giao diện Nhật ký thiết bị thô
* └── **Feature**: Thiết kế giao diện Nhật ký thiết bị thô (`views/gk_device_log_views.xml`)
  * **Mô tả chi tiết**: Thiết kế List view và Form view cho model `t4.gate_keeper.device_log` giúp kỹ thuật viên dễ dàng tra cứu, lọc và xem thông tin chi tiết các payload thô gửi từ Controller lên hệ thống (phân biệt trạng thái xử lý thành công/lỗi).

---

## PHẦN 5 — MODULE 5: GHI NHẬN NHẬT KÝ SỰ KIỆN RA VÀO (ACCESS LOGS)
*Mục đích: Chuẩn hóa dữ liệu sự kiện ra vào và theo dõi vị trí nhân viên (Model: Access Log).*

### [MODEL] Cơ sở dữ liệu Nhật ký ra vào
* ├── **Feature**: Tạo model Nhật ký ra vào `t4.gate_keeper.access_log` (`models/gk_access_log.py`)
  * **Mô tả chi tiết**: Khai báo các trường: Nhân viên (`employee_id`), Mã thẻ (`card_code`), Thiết bị con (`device_id`), Khu vực liên đới computed (`area_id`), Chi nhánh computed (`branch_id`), Thời gian quẹt thẻ (`access_time`), Chiều ra/vào (`direction` selection: `in`/`out`/`unknown`), Phương thức xác thực (`verification_type`), và trạng thái đồng bộ.
* ├── **Feature**: Ràng buộc bảo mật dữ liệu chặn sửa đổi nhật ký
  * **Mô tả chi tiết**: Viết hàm ghi đè `write()` và `unlink()` trên model `t4.gate_keeper.access_log`, đưa ra cảnh báo lỗi (ValidationError) chặn đứng mọi hành vi chỉnh sửa hoặc xóa các sự kiện ra vào sau khi đã được lưu trong database.
* └── **Feature**: Viết logic tự động cập nhật vị trí và trạng thái hiện diện của nhân viên
  * **Mô tả chi tiết**: Viết hàm xử lý trong `create()` của model Access Log: Dựa trên chiều ra vào (`direction` là `in` hoặc `out`) và khu vực của thiết bị (`area_id`), tự động cập nhật trường trạng thái hiện diện `presence_state` (trong/ngoài) và khu vực hiện tại `current_area_id` trên bảng nhân viên `t4.gate_keeper.employee`.

### [VIEW] Giao diện Nhật ký ra vào
* └── **Feature**: Thiết kế List view, Form view và Search view cho Nhật ký ra vào (`views/gk_access_log_views.xml`)
  * **Mô tả chi tiết**: Thiết kế giao diện để Admin và Bảo vệ dễ dàng tra cứu, lọc và xem thông tin chi tiết các sự kiện ra vào của nhân viên. List view hiển thị: Nhân viên, Chi nhánh, Khu vực, Thời gian, Chiều ra/vào và Phương thức xác thực. Hỗ trợ Search view lọc theo Chi nhánh, Khu vực, hướng đi (in/out) và khoảng thời gian.

---

## PHẦN 6 — MODULE 6: CẢNH BÁO VÀ CHÍNH SÁCH BẢO MẬT (WARNINGS & POLICIES)
*Mục đích: Phát hiện vi phạm an ninh và cảnh báo trực quan (Model: Area Warning, Alert Policy).*

### [MODEL] Cấu hình Cảnh báo và Chính sách bảo mật
* ├── **Feature**: Tạo model Loại cảnh báo `t4.gate_keeper.area_warning_type` (`models/gk_area_warning_type.py`)
  * **Mô tả chi tiết**: Tạo bảng loại cấu hình cảnh báo, nạp sẵn hai loại chính thông qua XML data: `invalid_access` (vi phạm giờ giấc, cuối tuần, cấm vào) và `device_issue` (lỗi thiết bị ngoại tuyến).
* ├── **Feature**: Tạo model Cảnh báo khu vực `t4.gate_keeper.area_warning` (`models/gk_area_warning.py`)
  * **Mô tả chi tiết**: Tạo bảng ghi nhận cảnh báo vi phạm thực tế: Khu vực xảy ra sự cố (`area_id`), thiết bị nguồn (`device_id`), nhân viên liên quan (`employee_id`), loại cảnh báo (`warning_type_id`), mô tả lỗi (`description`), trạng thái xử lý (`state` selection: `warning`/`resolved`), tài khoản giải quyết (`resolved_by_id`), thời điểm giải quyết và ghi chú xử lý.
* └── **Feature**: Tạo model Chính sách bảo mật `t4.gate_keeper.alert_policy` (`models/gk_alert_policy.py`)
  * **Mô tả chi tiết**: Bảng thiết lập quy tắc bảo mật: Chi nhánh áp dụng, Khu vực bảo vệ, các Nhóm nhân viên được phép ra vào, Khung giờ làm việc tiêu chuẩn (start_hour, end_hour) và cấu hình áp dụng cho ngày cuối tuần (weekend check).

### [LOGIC] Động cơ đánh giá quy tắc bảo mật (Security Engine)
* ├── **Feature**: Viết Hook kiểm tra vi phạm bảo mật khi tạo Access Log
  * **Mô tả chi tiết**: Viết hàm bổ trợ kiểm tra trong sự kiện tạo nhật ký. Chuyển đổi thời gian `access_time` sang múi giờ chi nhánh (`branch_id.timezone`). Kiểm tra xem thời gian có nằm ngoài khung giờ cho phép trong chính sách (`alert_policy`) hoặc rơi vào ngày cuối tuần không. Nếu vi phạm, tự động tạo mới một Area Warning trạng thái `warning`.
* └── **Feature**: Viết logic tự động tạo/đóng cảnh báo thiết bị ngoại tuyến
  * **Mô tả chi tiết**: 
    - Khi thiết bị con hoặc bộ điều khiển đổi trạng thái sang ngoại tuyến, tự động kiểm tra và tạo bản ghi cảnh báo `device_issue`.
    - Khi thiết bị hoạt động bình thường trở lại (trạng thái `online`), tự động gọi hàm `action_resolve()` để đóng (resolve) toàn bộ cảnh báo ngoại tuyến liên quan của thiết bị này.

### [VIEW] Giao diện giám sát an ninh
* ├── **Feature**: Thiết kế List view và Form view cho Cảnh báo khu vực (`views/gk_area_warning_views.xml`)
  * **Mô tả chi tiết**: Giao diện hiển thị danh sách các vi phạm. Thiết kế nút bấm "Xác nhận giải quyết" (Action Button calling `action_resolve()`) trên giao diện Form view cho phép người trực ban nhập ghi chú và đóng cảnh báo nhanh chóng.
* └── **Feature**: Thiết kế List view và Form view cho Chính sách bảo mật và Loại cảnh báo (`views/gk_alert_policy_views.xml`, `views/gk_area_warning_type_views.xml`)
  * **Mô tả chi tiết**:
    - Giao diện Chính sách bảo mật: Cho phép Admin cấu hình các thông số: Chi nhánh áp dụng, Khu vực bảo vệ, Khung giờ làm việc (start_hour, end_hour), ngày cuối tuần và các nhóm nhân sự được phép truy cập.
    - Giao diện Loại cảnh báo: Hiển thị danh sách mã và tên các loại cảnh báo (`invalid_access`, `device_issue`).

---

## PHẦN 7 — PHẦN KIỂM THỬ VÀ CÁC CHỨC NĂNG TRÌ HOÃN (OUT OF MVP)
*Mục đích: Đảm bảo chất lượng hệ thống và xác định rõ giới hạn MVP.*

### [TEST] Kiểm thử tự động (Unit Test)
* ├── **Feature**: Viết các test case kiểm thử logic xử lý múi giờ địa phương
  * **Mô tả chi tiết**: Viết các test case trong thư mục `tests/` giả lập các sự kiện quẹt thẻ gửi lên từ các chi nhánh có múi giờ khác nhau (ví dụ: Tokyo, TP.HCM), đảm bảo hệ thống đánh giá đúng khung giờ vi phạm theo giờ địa phương của chi nhánh đó.
* └── **Feature**: Viết unit test kiểm tra cơ chế đồng bộ nhân sự một chiều từ Odoo HR
  * **Mô tả chi tiết**: Viết test case tạo hồ sơ nhân sự trên `hr.employee`, xác minh hệ thống tự động đồng bộ sang `t4.gate_keeper.employee` và chặn đứng mọi hành vi tạo trực tiếp trên giao diện Gate Keeper Employee.

### [POSTPONED] Các tính năng nằm ngoài phạm vi MVP (Trì hoãn - Phase 2)
* ├── **Feature**: Chấm công hành chính (Attendance).
  * **Mô tả chi tiết**: Trì hoãn việc tích hợp bảng công, tính ca làm việc phức tạp của Odoo HR từ dữ liệu sự kiện quẹt thẻ.
* ├── **Feature**: Quản lý khách vãng lai (Visitor Management).
  * **Mô tả chi tiết**: Trì hoãn quy trình cấp thẻ tạm thời, đăng ký trước thông tin khách và theo dõi hành trình khách.
* ├── **Feature**: Màn hình giám sát trực ban thời gian thực (Real-time Dashboard).
  * **Mô tả chi tiết**: Trì hoãn việc phát triển màn hình web động (Javascript/Websocket) hiển thị luồng quẹt thẻ real-time.
* └── **Feature**: Báo cáo đồ thị thống kê nâng cao (Advanced Reports).
  * **Mô tả chi tiết**: Trì hoãn các biểu đồ báo cáo hiệu suất ra vào, tỷ lệ vi phạm theo phòng ban dạng đồ thị phức tạp.