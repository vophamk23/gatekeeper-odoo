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
* ├── **Feature**: API ControllerRegister - Tiếp nhận đăng ký phần cứng và kích hoạt trạng thái trực tuyến cho Bộ điều khiển
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Cho phép các bộ điều khiển vật lý tự động đăng ký với hệ thống Odoo khi khởi động hoặc kết nối mạng lần đầu.
    - *HTTP Method & Route*: `POST` `/api/v1/controller-register` (được phân phối và bảo mật qua module `t4_coreapi`).
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Mã số seri vật lý của bộ điều khiển (bắt buộc, ví dụ: "CTRL-100234").
      - `hardware_model`: Tên dòng máy bộ điều khiển (ví dụ: "ZKTeco C3-200").
      - `firmware_version`: Phiên bản phần mềm nhúng đang chạy (ví dụ: "v2.1.4").
      - `ip_address`: Địa chỉ IP nội bộ của bộ điều khiển.
      - `mac_address`: Địa chỉ MAC vật lý của bộ điều khiển.
      - `connection_type`: Giao thức kết nối (`wifi`, `ethernet`, `cellular`).
    - *Logic xử lý Odoo Backend*:
      - Tra cứu bản ghi trong model `t4.gate_keeper.controller` dựa trên số seri `serial_number = controller_id`.
      - Nếu chưa có bản ghi, trả về lỗi cảnh báo bảo mật hoặc tự động tạo mới (tùy cấu hình whitelist).
      - Nếu có, cập nhật các trường cấu hình mạng: `ip_address`, `mac_address`, `firmware_version`, `connection_type`.
      - Chuyển trạng thái kết nối `status` của bộ điều khiển thành `online` và cập nhật `last_heartbeat_at = Datetime.now()`.
      - **Cascade trạng thái**: Tự động tìm tất cả các thiết bị con (`t4.gate_keeper.device`) đang thuộc bộ điều khiển này và có trạng thái `controller_offline` để chuyển sang `online`.
* ├── **Feature**: API DeviceRegister - Tiếp nhận và tự động đăng ký các thiết bị con vật lý kết nối với Bộ điều khiển
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Bộ điều khiển khai báo danh sách các thiết bị con kết nối trực tiếp vào các cổng của nó để Odoo quản lý.
    - *HTTP Method & Route*: `POST` `/api/v1/device-register`
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Số seri của bộ điều khiển quản lý.
      - `device_sn`: Số seri duy nhất của thiết bị con (ví dụ: đầu đọc thẻ RFID, máy quét vân tay).
      - `port_or_channel`: Cổng kết nối vật lý trên bộ điều khiển (ví dụ: cổng Wiegand 1, Wiegand 2).
      - `device_model`: Dòng máy thiết bị con.
    - *Logic xử lý Odoo Backend*:
      - Xác thực sự tồn tại của bộ điều khiển cha `controller_id`.
      - Tra cứu thiết bị con trong model `t4.gate_keeper.device` theo trường duy nhất `serial_number = device_sn`.
      - Nếu chưa tồn tại, tự động tạo mới thiết bị con, liên kết Many2one với bộ điều khiển cha (`controller_id`) và dòng máy tương thích.
      - Nếu đã tồn tại, cập nhật cổng kết nối `port_or_channel` và chuyển trạng thái hoạt động thành `online`.
* ├── **Feature**: API ControllerGetConfig - Tải thông tin múi giờ chi nhánh và các thuật toán sinh trắc học được hỗ trợ
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Bộ điều khiển tải các cấu hình hệ thống từ Odoo để tự căn chỉnh thời gian cục bộ và biết các thuật toán sinh trắc học khả dụng.
    - *HTTP Method & Route*: `POST` `/api/v1/config`
    - *Tham số đầu vào (Payload JSON)*:
      - `serial_number`: Số seri vật lý của bộ điều khiển.
    - *Logic xử lý Odoo Backend*:
      - Tìm kiếm bộ điều khiển khớp với `serial_number`.
      - Trích xuất trường múi giờ địa phương từ chi nhánh quản lý: `branch_id.timezone` (ví dụ: "Asia/Ho_Chi_Minh").
      - Quét tất cả các thiết bị con thuộc bộ điều khiển để lấy danh sách các thuật toán sinh trắc học được hỗ trợ thông qua liên kết `device_model_id.algorithm_ids`.
      - Trả về phản hồi chứa thông tin múi giờ, định dạng ngày giờ, và danh sách thuật toán (ví dụ: Face v12.0, Finger v10.0).
* ├── **Feature**: API ControllerHeartbeat - Tiếp nhận tín hiệu nhịp tim định kỳ và tự động phát hiện/xử lý cảnh báo ngoại tuyến
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Duy trì kết nối sống (Keep-alive) giữa thiết bị phần cứng và hệ thống, đồng thời phát hiện sớm sự cố mất kết nối mạng.
    - *HTTP Method & Route*: `POST` `/api/v1/heartbeat`
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Số seri của bộ điều khiển gửi tín hiệu.
      - `devices_status`: Mảng danh sách trạng thái của các thiết bị con trực thuộc (gồm `device_sn` và trạng thái `status` tương ứng).
    - *Logic xử lý Odoo Backend*:
      - Cập nhật thời điểm nhận tín hiệu cuối `last_heartbeat_at = Datetime.now()` và đặt trạng thái Controller thành `online`.
      - Duyệt qua mảng `devices_status` để cập nhật trạng thái hoạt động cho từng thiết bị con tương ứng trong database.
      - **Logic sinh Cảnh báo tự động**: 
        - Nếu trạng thái thiết bị con chuyển sang ngoại tuyến (`offline` hoặc `controller_offline`) và thiết bị đó đã được gán vào một khu vực (`area_id`), hệ thống sẽ kiểm tra xem đã có cảnh báo đang hoạt động nào chưa. Nếu chưa, tự động tạo mới bản ghi `t4.gate_keeper.area_warning` với loại cảnh báo là `device_issue` (lỗi thiết bị).
        - Nếu thiết bị con trực tuyến trở lại (`online`), hệ thống tự động gọi hàm `action_resolve()` để đóng (đổi trạng thái sang `resolved`) toàn bộ các cảnh báo ngoại tuyến liên quan của thiết bị này.
* ├── **Feature**: API ControllerEmployeeSync - Đồng bộ và lọc danh sách nhân viên cần thêm mới, cập nhật hoặc xóa khỏi thiết bị
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Cung cấp cho bộ điều khiển danh sách các nhân viên có thay đổi dữ liệu thẻ/sinh trắc học kể từ lần đồng bộ thành công gần nhất.
    - *HTTP Method & Route*: `POST` `/api/v1/employee-sync`
    - *Tham số đầu vào (Payload JSON)*:
      - `serial_number`: Số seri vật lý của bộ điều khiển gọi đồng bộ.
      - `last_sync_at`: Thời điểm đồng bộ thành công trước đó do thiết bị gửi lên.
    - *Logic xử lý Odoo Backend*:
      - Tìm kiếm Controller tương ứng. Nếu tham số `last_sync_at` rỗng hoặc không hợp lệ, hệ thống sẽ lấy giá trị mặc định lưu trên database (`last_sync_at` của Controller).
      - So sánh thời điểm chỉnh sửa `write_date` của tất cả bản ghi nhân sự `t4.gate_keeper.employee` với mốc thời gian đồng bộ trước.
      - Lọc ra:
        - Danh sách nhân viên cần cập nhật hoặc thêm mới (`action = "update"`): Những người được chỉnh sửa hoặc tạo mới sau thời điểm `last_sync_at`.
        - Danh sách nhân viên cần xóa bỏ khỏi bộ nhớ thiết bị (`action = "delete"`): Những người bị đổi chi nhánh, bị khóa thẻ hoặc đã nghỉ việc.
      - Trả về mảng JSON chứa danh sách `emp_id` và hành động tương ứng.
* ├── **Feature**: API EmployeeBiometricGet - Xuất thông tin thẻ từ và dữ liệu sinh trắc học mã hóa dạng Base64
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Truy xuất dữ liệu sinh trắc học chi tiết (vân tay/khuôn mặt) hoặc mã thẻ từ của nhân viên cụ thể để lưu xuống bộ nhớ cục bộ của Controller.
    - *HTTP Method & Route*: `POST` `/api/v1/biometric`
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Số seri của bộ điều khiển yêu cầu tải dữ liệu.
      - `emp_id`: Mã định danh phần cứng của nhân viên cần tải (ví dụ: UUID v4).
    - *Logic xử lý Odoo Backend*:
      - Tra cứu nhân viên theo mã `emp_id` trong bảng `t4.gate_keeper.employee`.
      - Truy vấn danh sách thẻ từ liên kết (`t4.gate_keeper.auth_info`).
      - Truy vấn dữ liệu sinh trắc học liên kết từ bảng `t4.gate_keeper.employee.biometric`.
      - Lọc chỉ lấy các bản ghi sinh trắc học có thuật toán tương thích với các thiết bị con của Controller hiện tại.
      - Thực hiện mã hóa Base64 cho trường dữ liệu nhị phân `template` chứa mã băm vân tay/khuôn mặt để đảm bảo truyền tải an toàn qua JSON.
* ├── **Feature**: API ControllerSyncAck - Tiếp nhận xác nhận nạp dữ liệu thành công và cập nhật thời điểm đồng bộ của Controller
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Thiết bị báo cáo lại cho Odoo sau khi đã ghi thành công tất cả dữ liệu nhân sự mới vào bộ nhớ flash của phần cứng.
    - *HTTP Method & Route*: `POST` `/api/v1/sync`
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Số seri vật lý của bộ điều khiển gửi xác nhận.
      - `sync_timestamp`: Thời điểm đồng bộ hoàn tất trên thiết bị.
    - *Logic xử lý Odoo Backend*:
      - Tìm kiếm Controller tương ứng theo số seri.
      - Cập nhật trường `last_sync_at = sync_timestamp` trên bảng `t4.gate_keeper.controller`.
      - Cơ chế kiểm tra phụ thuộc (depends engine) sẽ tự động cập nhật trường tính toán trạng thái đồng bộ `employee_sync_status` chuyển thành `synced` (Đã đồng bộ).
* ├── **Feature**: API AccessLogUpload - Tiếp nhận và phân tích mảng nhật ký quẹt thẻ thực tế của nhân viên gửi lên từ thiết bị
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Tiếp nhận dữ liệu quẹt thẻ thực tế của nhân viên gửi từ các thiết bị con để lưu trữ nhật ký ra vào và đánh giá quy tắc an ninh.
    - *HTTP Method & Route*: `POST` `/api/v1/log`
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Số seri bộ điều khiển gửi dữ liệu.
      - `logs`: Mảng danh sách các sự kiện quẹt thẻ, mỗi sự kiện gồm: `device_serial` (mã đầu đọc), `emp_id` (mã nhân viên), `card_code` (mã thẻ quẹt), `access_time` (thời gian sự kiện trên thiết bị), `direction` (`in`/`out`/`unknown`), `verification_type` (phương thức xác thực: thẻ, vân tay, mặt).
    - *Logic xử lý Odoo Backend*:
      - Với mỗi bản ghi trong mảng `logs`:
        - Tra cứu thiết bị con trong `t4.gate_keeper.device` theo `device_serial` để xác định trường `device_id`.
        - Tra cứu nhân viên trong `t4.gate_keeper.employee` theo `emp_id` để xác định trường `employee_id`.
        - Tạo mới một bản ghi trong `t4.gate_keeper.access_log` lưu trữ đầy đủ các thông tin trên cùng với trạng thái `sync_status = "success"`.
        - Hàm `create()` trên model Access Log sẽ tự động đánh giá chính sách an ninh và cập nhật trạng thái vị trí nhân sự.
* ├── **Feature**: API ControllerCommandPoll - Tiếp nhận yêu cầu quét tìm các lệnh điều khiển từ xa đang chờ thực thi (Pending Commands)
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Hỗ trợ cơ chế Pull-based giúp các bộ điều khiển nằm sau tường lửa (NAT) vẫn có thể nhận được lệnh mở cửa từ xa gửi từ Odoo Server bằng cách gọi API định kỳ.
    - *HTTP Method & Route*: `POST` `/api/v1/command`
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Số seri của bộ điều khiển quét lệnh.
    - *Logic xử lý Odoo Backend*:
      - Tìm kiếm các bản ghi trong model lệnh điều khiển đang ở trạng thái `pending` và thuộc bộ điều khiển này.
      - Trả về danh sách lệnh dưới dạng mảng JSON bao gồm: `command_id`, loại lệnh (`open_door`, `close_door`, `lock_down`), thông số thiết bị con đích và thời gian hết hạn (expiration).
      - Chuyển trạng thái lệnh sang `sending` để đảm bảo thiết bị không tải trùng một lệnh nhiều lần.
* └── **Feature**: API ControllerCommandAck - Tiếp nhận báo cáo kết quả thực thi lệnh điều khiển từ xa (Mở/Khóa cửa) từ thiết bị
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Bộ điều khiển gửi xác nhận kết quả sau khi đã kích hoạt rơ-le mở cửa vật lý thành công hoặc thất bại.
    - *HTTP Method & Route*: `POST` `/api/v1/confirmation`
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Số seri của bộ điều khiển.
      - `command_id`: Mã định danh lệnh đã nhận từ Odoo.
      - `status`: Trạng thái thực thi (`success` / `failed`).
      - `execution_message`: Tin nhắn báo cáo chi tiết hoặc mã lỗi phần cứng (nếu có).
    - *Logic xử lý Odoo Backend*:
      - Tìm bản ghi lệnh khớp với `command_id`.
      - Cập nhật trạng thái lệnh sang `success` hoặc `failed` và ghi nhận nội dung `execution_message` phục vụ kiểm tra lỗi.

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