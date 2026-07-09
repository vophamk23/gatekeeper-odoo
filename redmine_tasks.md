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
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.branch` trong Odoo kèm theo mô tả ngắn gọn `_description = "Gate Keeper Branch"`.
    - Khai báo trường tên chi nhánh `name` (Char, bắt buộc, ví dụ: "Chi nhánh Hà Nội") làm nhãn hiển thị chính.
    - Khai báo trường mã định danh `code` (Char, bắt buộc, ví dụ: "HN_BRANCH") viết liền không dấu, phục vụ đối chiếu cấu hình.
    - Khai báo trường địa chỉ vật lý `address` (Char) của văn phòng chi nhánh.
    - Khai báo trường trạng thái kích hoạt `active` (Boolean, mặc định là True) giúp ẩn/hiện chi nhánh tạm ngừng hoạt động.
    - Khai báo trường múi giờ địa lý `timezone` (Selection, bắt buộc): Lấy danh sách múi giờ chuẩn toàn cầu từ thư viện `pytz.common_timezones` (ví dụ: `Asia/Ho_Chi_Minh`, `Asia/Tokyo`) nhằm phục vụ việc quy đổi thời gian khi đánh giá quy tắc ra vào của thiết bị.
* ├── **Feature #11365**: Thêm ràng buộc duy nhất cho mã chi nhánh và Chặn xóa chi nhánh khi còn khu vực bên trong.
  * **Mô tả chi tiết**:
    - Thiết lập ràng buộc SQL duy nhất (`_sql_constraints`) cho trường `code` đảm bảo mã chi nhánh không bị trùng lặp trong cơ sở dữ liệu.
    - Viết đè hàm xóa bản ghi `unlink()` trên model `t4.gate_keeper.branch`.
    - Thực hiện kiểm tra xem chi nhánh hiện tại có đang liên kết với khu vực (`t4.gate_keeper.area`) con nào không.
    - Nếu phát hiện còn khu vực con hoạt động, ném ra cảnh báo lỗi `ValidationError` kèm thông điệp dịch thuật tiếng Việt thông qua hàm `_()` để chặn đứng hành vi xóa chi nhánh của người dùng.
* └── **Feature #11366**: Nhập dữ liệu mẫu 2-3 chi nhánh để test giao diện.
  * **Mô tả chi tiết**:
    - Khởi tạo tệp tin dữ liệu XML `data/gk_branch_data.xml` và khai báo vào danh sách `data` trong tệp `__manifest__.py`.
    - Thiết lập thuộc tính `noupdate="1"` để ngăn chặn dữ liệu mẫu bị ghi đè khi nâng cấp module (upgrade).
    - Tạo sẵn các bản ghi mẫu:
      - Chi nhánh Hà Nội: Mã `HN_BRANCH`, múi giờ `Asia/Ho_Chi_Minh`.
      - Chi nhánh Đà Nẵng: Mã `DN_BRANCH`, múi giờ `Asia/Ho_Chi_Minh`.
      - Chi nhánh TP.HCM: Mã `HCM_BRANCH`, múi giờ `Asia/Ho_Chi_Minh`.

### [MODEL] Xây dựng model Area (Khu vực)
* ├── **Feature #11367**: Tạo class `GateKeeperArea` (`t4.gate_keeper.area` trong `models/gk_area.py`) liên kết Many2one với `branch_id` và các trường tính toán trạng thái động.
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.area` trong Odoo kèm mô tả `_description = "Gate Keeper Area"`.
    - Khai báo trường tên khu vực `name` (Char, bắt buộc, ví dụ: "Phòng Server", "Kho thành phẩm").
    - Thiết lập liên kết Many2one bắt buộc đến chi nhánh quản lý `branch_id` (`t4.gate_keeper.branch`, required=True).
    - Tạo trường One2many `warning_ids` liên kết đến các cảnh báo an ninh khu vực (`t4.gate_keeper.area_warning`).
    - Khai báo trường trạng thái an ninh computed lưu trữ `status` (Selection: `normal`/`warning`, store=True). Trạng thái chuyển thành `warning` nếu tồn tại ít nhất một cảnh báo liên kết chưa giải quyết (`state == 'warning'`), ngược lại là `normal`.
    - Khai báo trường tính toán số lượng cảnh báo `warning_count` (Integer) hiển thị tổng số cảnh báo an ninh đang hoạt động của khu vực.
* ├── **Feature #11368**: Liên kết khu vực với chi nhánh và thêm ràng buộc tên khu vực không trùng trong cùng một chi nhánh.
  * **Mô tả chi tiết**:
    - Viết hàm kiểm tra ràng buộc Python sử dụng decorator `@api.constrains('name', 'branch_id')`.
    - Đảm bảo trong phạm vi cùng một chi nhánh (`branch_id`), tên của các khu vực con không được phép trùng lặp nhau (ví dụ: Trong "Chi nhánh Hà Nội" không thể tạo hai khu vực cùng tên "Phòng R&D", nhưng "Chi nhánh TP.HCM" vẫn được phép có một "Phòng R&D" riêng).
    - Ném ra lỗi `ValidationError` dịch thuật tiếng Việt nếu phát hiện vi phạm quy tắc trùng tên khu vực này.
* └── **Feature #11369**: Nhập dữ liệu mẫu 4-5 khu vực để test.
  * **Mô tả chi tiết**:
    - Thiết lập các bản ghi khu vực mẫu thông qua tệp dữ liệu XML demo của module.
    - Liên kết chính xác các khu vực mẫu này đến các chi nhánh đã tạo trước đó bằng thuộc tính `ref="..."`.
    - Nạp sẵn các bản ghi mẫu đặc trưng:
      - Thuộc chi nhánh Hà Nội: "Sảnh chính Hà Nội", "Phòng Server HN", "Phòng R&D HN".
      - Thuộc chi nhánh TP.HCM: "Sảnh chính HCM", "Kho thành phẩm HCM".

### [VIEW] Xây dựng giao diện quản lý chi nhánh
* ├── **Feature #11370**: Trang list view danh sách chi nhánh dạng bảng hiển thị tên, mã chi nhánh, địa chỉ và trạng thái hoạt động (`views/gk_branch_views.xml`).
  * **Mô tả chi tiết**:
    - Định nghĩa List View (Tree View) cho model chi nhánh hiển thị cấu trúc bảng rõ ràng.
    - Các cột hiển thị trên danh sách gồm: Mã chi nhánh (`code`), Tên chi nhánh (`name`), Múi giờ (`timezone`), Địa chỉ (`address`), Trạng thái hoạt động (`active`).
    - Hỗ trợ tính năng bật/tắt trạng thái hoạt động trực tiếp từ giao diện tree view.
* ├── **Feature #11371**: Trang form view chi tiết chi nhánh hiển thị thông tin đầy đủ kèm danh sách khu vực con bên dưới.
  * **Mô tả chi tiết**:
    - Thiết kế giao diện Form View cho chi nhánh sử dụng thẻ `<group>` phân chia bố cục cân đối.
    - *Khung thông tin cơ bản*: Tên chi nhánh, Mã chi nhánh, Trạng thái hoạt động.
    - *Khung cấu hình mạng & địa lý*: Địa chỉ văn phòng, Múi giờ chi nhánh.
    - *Tab khu vực trực thuộc*: Tích hợp thẻ `<notebook>` chứa tab danh sách khu vực con (One2many `area_ids` hiển thị dạng tree view lồng), hỗ trợ tạo nhanh khu vực con trực tiếp ngay trên form chi nhánh.
* └── **Feature #11372**: Ô tìm kiếm và lọc chi nhánh theo tên, mã hoặc trạng thái.
  * **Mô tả chi tiết**:
    - Xây dựng cấu trúc thẻ `<search>` cho chi nhánh.
    - Cho phép tìm kiếm nhanh theo Tên hoặc Mã chi nhánh thông qua thanh tìm kiếm.
    - Thêm bộ lọc nhanh (Filters) lọc danh sách chi nhánh "Đang hoạt động" (`active = True`) và "Đã ngừng hoạt động" (`active = False`).
    - Thêm tính năng gom nhóm (Group by) theo Múi giờ (`timezone`).

### [VIEW] Xây dựng giao diện quản lý khu vực
* ├── **Feature #11373**: Trang list view danh sách khu vực lọc theo từng chi nhánh (`views/gk_area_views.xml`).
  * **Mô tả chi tiết**:
    - Định nghĩa List View cho model khu vực hiển thị các cột: Tên khu vực (`name`), Chi nhánh quản lý (`branch_id`), Trạng thái an ninh (`status`), Số lượng cảnh báo hiện tại (`warning_count`).
    - Hỗ trợ thanh công cụ tìm kiếm nhanh theo tên khu vực và bộ lọc danh sách theo từng Chi nhánh.
* ├── **Feature #11374**: Trang form view chi tiết khu vực hiển thị danh sách thiết bị con và danh sách cảnh báo khu vực liên quan.
  * **Mô tả chi tiết**:
    - Thiết kế Form View cho khu vực hiển thị thông tin chi nhánh quản lý và trạng thái an ninh.
    - Tích hợp bố cục Tab tiện lợi (`notebook`):
      - *Tab Thiết bị lắp đặt*: Hiển thị danh sách One2many các thiết bị con (`t4.gate_keeper.device`) đang được cấu hình hoạt động tại khu vực này.
      - *Tab Nhật ký cảnh báo*: Hiển thị danh sách các bản ghi cảnh báo khu vực (`t4.gate_keeper.area_warning`) liên quan đến khu vực này để trực ban theo dõi lịch sử vi phạm an ninh.
* └── **Feature #11375**: Hiển thị trực quan trạng thái cảnh báo khu vực (normal/warning) ngay trên trang danh sách list view.
  * **Mô tả chi tiết**:
    - Cấu hình các thuộc tính trang trí động trên thẻ `<tree>` của list view khu vực (ví dụ: `decoration-danger="status == 'warning'"`, `decoration-success="status == 'normal'"`).
    - Hiển thị trực quan màu ĐỎ hoặc VÀNG trên dòng danh sách khi khu vực đó đang có sự cố an ninh chưa giải quyết, giúp người trực ban dễ dàng nhận diện vùng nguy hiểm tức thì.

### [ACCESS] Phân quyền module chi nhánh và khu vực
* ├── **Feature #11376**: Cấu hình quyền Admin - toàn quyền chi nhánh và khu vực (`security/ir.model.access.csv`).
  * **Mô tả chi tiết**:
    - Đăng ký phân quyền trong tệp cấu hình an ninh CSV của Odoo.
    - Phân bổ đầy đủ các quyền CRUD: Đọc (Read = 1), Ghi (Write = 1), Tạo (Create = 1), Xóa (Delete = 1) cho nhóm quyền quản trị viên Gate Keeper Admin (`t4_gate_keeper.group_gatekeeper_admin`) đối với cả 2 model `t4.gate_keeper.branch` và `t4.gate_keeper.area`.
* ├── **Feature #11377**: Cấu hình quyền Bảo vệ và Kỹ thuật viên - chỉ được xem chi nhánh và khu vực.
  * **Mô tả chi tiết**:
    - Cấu hình quyền chỉ xem (Read-only) trong file CSV phân quyền: cấp quyền Đọc (Read = 1), chặn Ghi (Write = 0), chặn Tạo (Create = 0), chặn Xóa (Delete = 0) cho hai nhóm vai trò Bảo vệ (`t4_gate_keeper.group_gatekeeper_guard`) và Kỹ thuật viên (`t4_gate_keeper.group_gatekeeper_technician`) trên cả hai model Chi nhánh và Khu vực.
* └── **Feature #11378**: Kiểm tra phân quyền đúng theo từng vai trò.
  * **Mô tả chi tiết**:
    - Tạo các tài khoản kiểm thử tương ứng với từng nhóm vai trò trên môi trường local.
    - Xác minh tài khoản Bảo vệ khi xem danh sách Chi nhánh/Khu vực sẽ không nhìn thấy nút "Tạo mới" (Create) và nút "Sửa" (Edit), đồng thời hệ thống ném ra lỗi AccessError từ chối hành vi chỉnh sửa.
    - Xác minh tài khoản Admin có thể thực hiện đầy đủ các chức năng quản trị bình thường.

## PHẦN 2 — MODULE 2: QUẢN LÝ BỘ ĐIỀU KHIỂN VÀ THIẾT BỊ
*Mục đích: Quản lý hạ tầng thiết bị phần cứng (Model: Controller, Device, Device Model, Algorithm).*

### [MODEL] Cơ sở dữ liệu Bộ điều khiển và Thiết bị
* ├── **Feature**: Tạo model Bộ điều khiển `t4.gate_keeper.controller` (`models/gk_controller.py`)
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.controller` trong Odoo kèm theo mô tả ngắn gọn `_description = "Gate Keeper Controller"`.
    - Khai báo trường tên bộ điều khiển `name` (Char, bắt buộc, ví dụ: "Bộ điều khiển Cổng Chính").
    - Khai báo trường số seri phần cứng `serial_number` (Char, bắt buộc, unique) để nhận diện duy nhất thiết bị vật lý khi giao tiếp qua API.
    - Khai báo các trường cấu hình mạng: Địa chỉ IP `ip_address` (Char) và Địa chỉ MAC vật lý `mac_address` (Char).
    - Khai báo trường phiên bản phần mềm nhúng `firmware_version` (Char) và giao thức kết nối `connection_type` (Selection: `wifi`, `ethernet`, `cellular`, `tcp_ip`).
    - Khai báo trường trạng thái kết nối `status` (Selection: `online`/`offline`, mặc định `offline`).
    - Khai báo các trường ghi nhận thời gian: Thời điểm heartbeat cuối `last_heartbeat_at` (Datetime), thời điểm đồng bộ thành công gần nhất `last_sync_at` (Datetime).
    - Khai báo các liên kết nghiệp vụ: Chi nhánh `branch_id` (Many2one tới `t4.gate_keeper.branch`, bắt buộc) và Công ty sở hữu `company_id` (Many2one tới `res.company`, bắt buộc, mặc định lấy công ty hiện tại của user).
    - Khai báo trường đồng bộ múi giờ tự động `timezone` (Selection, store=True): Lấy giá trị liên kết từ chi nhánh cha thông qua `related="branch_id.timezone"`.
* ├── **Feature**: Tạo model Thiết bị con `t4.gate_keeper.device` (`models/gk_device.py`)
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.device` trong Odoo kèm theo mô tả ngắn gọn `_description = "Gate Keeper Device"`.
    - Khai báo các trường cơ bản: Tên thiết bị `name` (Char, bắt buộc), Số seri thiết bị con `serial_number` (Char, bắt buộc, unique).
    - Khai báo trường cổng kết nối vật lý trên bộ điều khiển `port_or_channel` (Char, ví dụ: "relay_1", "wiegand_2").
    - Khai báo trường trạng thái hoạt động của thiết bị `status` (Selection: `online`/`offline`/`controller_offline`, mặc định `offline`).
    - Khai báo các liên kết Many2one bắt buộc: Bộ điều khiển cha quản lý trực tiếp `controller_id` (Many2one tới `t4.gate_keeper.controller`, required=True, onDelete="cascade"), Khu vực lắp đặt `area_id` (Many2one tới `t4.gate_keeper.area`), và Dòng máy thiết bị `device_model_id` (Many2one tới `t4.gate_keeper.device_model`).
    - Thiết lập trường tự động kế thừa múi giờ từ chi nhánh `timezone` (Selection, store=True) thông qua `related="controller_id.branch_id.timezone"`.
    - Thiết lập trường phân quyền theo công ty `company_id` (Many2one tới `res.company`, store=True) kế thừa trực tiếp từ bộ điều khiển cha qua `related="controller_id.company_id"`.
* └── **Feature**: Tạo các model phụ trợ Model thiết bị và Thuật toán sinh trắc học
  * **Mô tả chi tiết**:
    - **Tạo model Dòng máy (`t4.gate_keeper.device_model` trong `models/gk_device_model.py`)**:
      - Khai báo các trường: Tên dòng máy `name` (Char, bắt buộc, ví dụ: "ZKTeco C3-200"), Nhà sản xuất `manufacturer` (Char).
      - Thiết lập liên kết Many2many `algorithm_ids` đến model Thuật toán để khai báo các công nghệ sinh trắc học mà dòng máy này hỗ trợ.
    - **Tạo model Thuật toán (`t4.gate_keeper.algorithm` trong `models/gk_algorithm.py`)**:
      - Khai báo các trường: Tên thuật toán `name` (Char, bắt buộc, ví dụ: "ZKTeco Face 12.0"), Loại dữ liệu sinh trắc học `bio_type` (Selection: `fingerprint`/`face`/`rfid`/`card`), và Phiên bản thuật toán `version` (Char).

### [LOGIC] Logic trạng thái và Tác vụ tự động (Scheduler)
* ├── **Feature**: Viết cơ chế cascade trạng thái kết nối
  * **Mô tả chi tiết**:
    - Viết hàm ghi đè `write()` trên model `t4.gate_keeper.controller` để bắt sự kiện thay đổi trạng thái kết nối `status`.
    - **Khi Controller chuyển sang trực tuyến (`status == 'online'`)**: Tự động tìm tất cả các thiết bị con trực thuộc (`device_ids`) đang ở trạng thái ngoại tuyến do mất kết nối bộ điều khiển (`status == 'controller_offline'`) để chuyển đồng loạt sang `online`.
    - **Khi Controller chuyển sang ngoại tuyến (`status != 'online'`)**: Tự động tìm tất cả các thiết bị con trực thuộc đang không ở trạng thái ngoại tuyến bộ điều khiển (`status != 'controller_offline'`) để chuyển sang trạng thái mất kết nối cha `controller_offline`.
* └── **Feature**: Cấu hình Scheduled Action tự động quét trạng thái thiết bị ngoại tuyến
  * **Mô tả chi tiết**:
    - Khởi tạo tệp tin XML `data/scheduler_cron.xml` cấu hình tác vụ chạy tự động định kỳ mỗi 5 phút (`ir.cron`).
    - Viết logic kiểm tra trạng thái ngoại tuyến của Controller trong tệp `models/gk_scheduler.py` (hoặc method trên model controller).
    - Quét tìm toàn bộ các bộ điều khiển đang ở trạng thái trực tuyến (`status == 'online'`) nhưng thời điểm nhận tín hiệu nhịp tim cuối cùng (`last_heartbeat_at`) cách thời điểm hiện tại quá 15 phút.
    - Chuyển trạng thái của các bộ điều khiển quá hạn này sang ngoại tuyến `offline`. Khi đó, hàm write() của bộ điều khiển sẽ tự động cascade để tắt trạng thái của các thiết bị con trực thuộc.

### [VIEW] Giao diện quản lý Thiết bị phần cứng
* ├── **Feature**: Thiết kế List view và Form view cho Bộ điều khiển (`views/gk_controller_views.xml`)
  * **Mô tả chi tiết**:
    - **List view**: Hiển thị bảng danh sách bộ điều khiển gồm các cột: Tên, Số seri, Trạng thái kết nối (sử dụng màu sắc trực quan), Chi nhánh quản lý, Công ty sở hữu, Thời điểm nhận nhịp tim cuối.
    - **Form view**:
      - Phân chia thành các Group thông tin rõ ràng: *Thông tin chung* (Tên, Số seri, Chi nhánh, Công ty), *Thông số kết nối* (IP, MAC, Giao thức, Phiên bản phần mềm), *Trạng thái hoạt động* (Trạng thái kết nối, Thời điểm nhận nhịp tim, Thời điểm đồng bộ thành công).
      - Tích hợp One2many hiển thị danh sách các thiết bị con trực thuộc (`device_ids`) dạng bảng lồng bên dưới form.
    - **Search view**: Cho phép tìm kiếm theo Tên, Số seri. Filters lọc nhanh theo trạng thái trực tuyến/ngoại tuyến. Group by theo Chi nhánh và Công ty.
* ├── **Feature**: Thiết kế List view và Form view cho Thiết bị (`views/gk_device_views.xml`)
  * **Mô tả chi tiết**:
    - **List view**: Hiển thị danh sách thiết bị con bao gồm các cột: Tên thiết bị, Số seri, Bộ điều khiển quản lý, Khu vực lắp đặt, Trạng thái hoạt động. Sử dụng màu sắc badges để phân biệt trạng thái: Xanh lá cho `online`, Đỏ cho `offline`, Cam cho `controller_offline`.
    - **Form view**: Phân nhóm cấu hình: *Thông tin chung* (Tên, Số seri, Công ty), *Vị trí lắp đặt* (Bộ điều khiển quản lý, Cổng/Kênh vật lý, Khu vực lắp đặt), *Cấu hình phần cứng* (Dòng máy thiết bị, Trạng thái hoạt động).
    - **Search view**: Cho phép tìm kiếm nhanh theo Tên, Số seri thiết bị con. Filters lọc theo trạng thái kết nối. Group by theo Bộ điều khiển và Khu vực lắp đặt.
* ├── **Feature**: Thiết kế giao diện giám sát trạng thái đồng bộ nhân sự của Bộ điều khiển (`views/gk_controller_sync_views.xml`)
  * **Mô tả chi tiết**:
    - Xây dựng giao diện List view chuyên biệt để theo dõi hiệu quả việc đồng bộ dữ liệu.
    - Các cột hiển thị: Tên bộ điều khiển, Số seri, Chi nhánh, Trạng thái đồng bộ nhân viên `employee_sync_status` (sử dụng nhãn trang trí trực quan: Xanh cho `synced` - Đã đồng bộ, Đỏ cho `out_of_sync` - Lệch dữ liệu), Thời điểm đồng bộ thành công cuối cùng `last_sync_at`.
* └── **Feature**: Thiết kế List view và Form view cho Dòng máy và Thuật toán (`views/gk_device_model_views.xml`, `views/gk_algorithm_views.xml`)
  * **Mô tả chi tiết**:
    - **Giao diện Dòng máy (`gk_device_model_views.xml`)**:
      - List view hiển thị: Tên dòng máy, Nhà sản xuất.
      - Form view hiển thị thông tin chung và danh sách Many2many các thuật toán sinh trắc học được hỗ trợ dạng thẻ tag trực quan.
    - **Giao diện Thuật toán (`gk_algorithm_views.xml`)**:
      - List view hiển thị: Tên thuật toán, Loại sinh trắc học, Phiên bản.
      - Form view cho phép cấu hình chi tiết thông số thuật toán.

## PHẦN 3 — MODULE 3: QUẢN LÝ NHÂN SỰ VÀ THÔNG TIN XÁC THỰC
*Mục đích: Quản lý hồ sơ nhân sự, nhóm và sinh trắc học (Model: Employee, Auth Info, Employee Biometric, Employee Group).*

### [MODEL] Cơ sở dữ liệu Nhân sự và Xác thực
* ├── **Feature**: Tạo model Nhân sự Gate Keeper `t4.gate_keeper.employee` (`models/gk_employee.py`)
  * **Mô tả chi tiết**:
    - **Tách biệt kiến trúc nhân sự**: Xây dựng model nhân sự độc lập hoàn toàn với hồ sơ nhân sự hành chính của Odoo (`hr.employee`). Việc này nhằm bảo vệ sự ổn định của thiết bị phần cứng khi mã nhân viên hành chính Odoo thay đổi.
    - **Trường Mã định danh duy nhất (`emp_id`)**: Khai báo trường `emp_id` (Char, bắt buộc, unique, mặc định tự động sinh chuỗi UUID v4 bằng hàm Python `uuid.uuid4`). Đây là mã băm vĩnh viễn gắn liền với vân tay/khuôn mặt lưu trên phần cứng thiết bị.
    - **Các trường thông tin cơ bản**:
      - `name` (Char, bắt buộc): Tên nhân viên hiển thị khi quét thẻ/nhận diện thành công.
      - `avatar` (Image): Ảnh chân dung nhân viên phục vụ đồng bộ nhận dạng khuôn mặt.
      - `active` (Boolean, default=True): Trạng thái hoạt động của nhân viên để tắt/bật đồng bộ nhanh.
      - `branch_id` (Many2one tới `t4.gate_keeper.branch`, bắt buộc): Chi nhánh làm việc của nhân sự.
    - **Các trường tính toán trạng thái hiện diện (Computed Fields)**:
      - `presence_state` (Selection: `inside`/`outside`/`unknown`, mặc định `unknown`): Trạng thái vị trí thực tế của nhân viên.
      - `current_area_id` (Many2one tới `t4.gate_keeper.area`): Khu vực hiện tại nhân viên đang đứng trong chi nhánh.
      - `biometric_ids` (One2many tới `t4.gate_keeper.employee.biometric`): Liên kết danh sách vân tay/khuôn mặt.
      - `auth_info_ids` (One2many tới `t4.gate_keeper.auth_info`): Liên kết danh sách thẻ từ RFID.
* ├── **Feature**: Tạo model Thẻ từ RFID `t4.gate_keeper.auth_info` (`models/gk_auth_info.py`)
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.auth_info` lưu trữ thông tin thẻ từ RFID vật lý cấp phát cho nhân viên.
    - Khai báo trường mã thẻ `card_code` (Char, bắt buộc, unique) ghi nhận chuỗi mã hex/dec của thẻ vật lý (ví dụ: "RFID-100234").
    - Khai báo trường trạng thái `active` (Boolean, mặc định True) cho phép khóa thẻ nhanh mà không cần xóa bản ghi.
    - Khai báo liên kết Many2one `employee_id` (`t4.gate_keeper.employee`, bắt buộc, onDelete="cascade") xác định chủ sở hữu thẻ.
    - Khai báo trường ghi chú `notes` (Text) ghi chép lý do cấp thẻ hoặc lịch sử thu hồi.
* ├── **Feature**: Tạo model Sinh trắc học `t4.gate_keeper.employee.biometric` (`models/gk_employee_biometric.py`)
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.employee.biometric` làm kho lưu trữ dữ liệu sinh trắc học vân tay hoặc khuôn mặt thô.
    - Khai báo trường loại sinh trắc học `bio_type` (Selection: `fingerprint`/`face`, bắt buộc).
    - Khai báo trường chỉ số ngón tay `finger_index` (Integer, chỉ áp dụng khi `bio_type == 'fingerprint'`, giá trị từ 0-9 tương ứng các ngón tay).
    - Khai báo liên kết Many2one `algorithm_id` (`t4.gate_keeper.algorithm`, bắt buộc) xác định thuật toán mã hóa tương thích với thiết bị phần cứng.
    - Khai báo trường dữ liệu mẫu `template` (Binary, bắt buộc) lưu trữ chuỗi dữ liệu mã băm vân tay/khuôn mặt được mã hóa thô (Binary byte).
    - Khai báo liên kết Many2one `employee_id` (`t4.gate_keeper.employee`, bắt buộc, onDelete="cascade").
* └── **Feature**: Tạo model Nhóm nhân sự `t4.gate_keeper.employee_group` (`models/gk_employee_group.py`)
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.employee_group` phục vụ nhóm nhân sự để cấu hình phân quyền truy cập theo phòng ban hoặc vai trò.
    - Khai báo các trường: Tên nhóm `name` (Char, bắt buộc), Mã nhóm `code` (Char, bắt buộc, unique, ví dụ: "RD_DEPT").
    - Khai báo liên kết Many2one `branch_id` (`t4.gate_keeper.branch`) xác định phạm vi chi nhánh áp dụng nhóm.
    - Thiết lập liên kết Many2many `employee_ids` đến model `t4.gate_keeper.employee` để lập danh sách thành viên thuộc nhóm.

### [LOGIC] Đồng bộ tuyệt đối từ phân hệ HR Odoo
* ├── **Feature**: Kế thừa model `hr.employee` để tự động đồng bộ nhân sự sang Gate Keeper (`models/hr_employee.py`)
  * **Mô tả chi tiết**:
    - Viết class kế thừa (inherit) model gốc `hr.employee` của Odoo.
    - **Ghi đè hàm tạo `create()`**: Sau khi bản ghi nhân sự HR Odoo được lưu thành công, hệ thống tự động kiểm tra và tạo mới một bản ghi tương ứng bên model `t4.gate_keeper.employee` với trường `name`, `active`, và `branch_id` (nếu có mapping). Đồng thời tự động sinh mã UUID v4 lưu vào trường `emp_id`.
    - **Ghi đè hàm ghi `write()`**: Khi người dùng thay đổi các thông tin cơ bản (Tên nhân sự, trạng thái hoạt động active) trên HR Employee, hệ thống tự động viết đè thông tin tương ứng sang bản ghi liên kết bên Gate Keeper Employee, đảm bảo dữ liệu đồng bộ một chiều ổn định.
* └── **Feature**: Cấu hình ẩn nút thêm mới "New" trên giao diện Gate Keeper Employee (`views/gk_employee_views.xml`)
  * **Mô tả chi tiết**:
    - Thiết lập thuộc tính khóa chức năng `create="0"` trên thẻ `<tree>` (hoặc `<list>`), `<kanban>`, và `<form>` của view model `t4.gate_keeper.employee`.
    - Điều này giúp ẩn đi nút "Tạo mới" (New) trên toàn bộ giao diện quản lý nhân sự Gate Keeper, bắt buộc người dùng chỉ có thể quản lý và thêm mới nhân sự thông qua phân hệ HR mặc định của Odoo, tránh tình trạng lệch dữ liệu (data inconsistency).

### [VIEW] Giao diện quản lý Nhân sự và Nhóm
* ├── **Feature**: Thiết kế giao diện kế thừa hồ sơ HR Employee (`views/hr_employee_views.xml`)
  * **Mô tả chi tiết**:
    - Viết XML kế thừa (xml inherit) Form view chuẩn của model `hr.employee` trong Odoo.
    - Bổ sung một tab con mới `<page string="Gate Keeper Configuration">` vào bên trong thẻ `<notebook>`.
    - Hiển thị các trường cấu hình liên quan: Mã định danh sinh trắc học `emp_id` (chỉ hiển thị dạng readonly), trạng thái hiện diện `presence_state`, khu vực đang đứng `current_area_id`.
    - Tích hợp liên kết danh sách thẻ từ RFID và sinh trắc học trực thuộc của nhân sự đó dưới dạng bảng One2many lồng.
* ├── **Feature**: Thiết kế List view và Form view cho Nhóm nhân sự (`views/gk_employee_group_views.xml`)
  * **Mô tả chi tiết**:
    - **List view**: Hiển thị bảng danh sách các nhóm nhân sự gồm các cột: Mã nhóm (`code`), Tên nhóm (`name`), Chi nhánh áp dụng (`branch_id`).
    - **Form view**: Phân bổ gồm các thông tin cơ bản của nhóm (Tên, Mã, Chi nhánh) và một notebook tab hiển thị danh sách Many2many các nhân viên thuộc nhóm (`employee_ids`) dạng bảng trực quan.
    - **Search view**: Hỗ trợ tìm kiếm theo tên/mã nhóm và gom nhóm nhanh theo Chi nhánh.
* └── **Feature**: Thiết kế List view và Form view cho Thẻ RFID và Sinh trắc học (`views/gk_auth_info_views.xml`, `views/gk_employee_biometric_views.xml`)
  * **Mô tả chi tiết**:
    - **Giao diện Thẻ từ (`gk_auth_info_views.xml`)**:
      - List view hiển thị: Mã thẻ (`card_code`), Nhân viên sở hữu (`employee_id`), Trạng thái hoạt động, Ghi chú.
      - Form view hỗ trợ khai báo mã thẻ, gán nhân viên và quản lý trạng thái kích hoạt của thẻ.
    - **Giao diện Sinh trắc học (`gk_employee_biometric_views.xml`)**:
      - List view hiển thị: Nhân viên liên kết, Loại sinh trắc học, Chỉ số ngón tay, Thuật toán mã hóa.
      - Form view hiển thị thông tin sinh trắc học, trường lưu mẫu băm nhị phân `template` được cấu hình readonly và hiển thị dưới dạng nhãn mã hóa an toàn.

## PHẦN 4 — MODULE 4: TIẾP NHẬN DỮ LIỆU TỪ CONTROLLER (INTEGRATION)
*Mục đích: Tiếp nhận và xử lý các yêu cầu HTTP từ các bộ điều khiển vật lý.*

### [API] Khai báo các Endpoint kết nối
* ├── **Feature**: API ControllerRegister - Tiếp nhận đăng ký phần cứng và kích hoạt trạng thái trực tuyến cho Bộ điều khiển
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Cho phép các bộ điều khiển vật lý tự động đăng ký với hệ thống Odoo khi khởi động hoặc kết nối mạng lần đầu.
    - *HTTP Method & Route*: `POST` `/api/v1/controller-register` (được phân phối và bảo mật qua module `t4_coreapi`).
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Mã số seri vật lý của bộ điều khiển (bắt buộc, ví dụ: "CON-HW-998877").
      - `hardware_model`: Tên dòng máy bộ điều khiển (ví dụ: "T4-GATE-PRO").
      - `firmware_version`: Phiên bản phần mềm nhúng đang chạy (ví dụ: "v2.1.0").
      - `ip_address`: Địa chỉ IP nội bộ của bộ điều khiển.
      - `mac_address`: Địa chỉ MAC vật lý của bộ điều khiển.
      - `connection_type`: Giao thức kết nối (`wifi`, `ethernet`, `cellular`, `tcp_ip`).
    - *Logic xử lý Odoo Backend*:
      - Tra cứu bản ghi trong model `t4.gate_keeper.controller` dựa trên số seri `serial_number = controller_id`.
      - Nếu chưa có bản ghi, trả về lỗi cảnh báo bảo mật hoặc tự động tạo mới (tùy cấu hình whitelist).
      - Nếu có, cập nhật các trường cấu hình mạng: `ip_address`, `mac_address`, `firmware_version`, `connection_type`.
      - Chuyển trạng thái kết nối `status` của bộ điều khiển thành `online` và cập nhật `last_heartbeat_at = Datetime.now()`.
      - **Cascade trạng thái**: Tự động tìm tất cả các thiết bị con (`t4.gate_keeper.device`) đang thuộc bộ điều khiển này và có trạng thái `controller_offline` để chuyển sang `online`.
    - *Ví dụ code API mẫu (GK Controller)*:
      ```python
      @endpoint(name="ControllerRegister")
      def controller_register(self):
          # Đọc dữ liệu từ HTTP POST request body dạng JSON gửi từ thiết bị
          body = get_body()
          controller_id = body.get("controller_id")
          
          # Chuẩn bị dữ liệu cập nhật trạng thái mạng và kết nối
          vals = {
              "ip_address": body.get("ip_address"),
              "mac_address": body.get("mac_address"),
              "firmware_version": body.get("firmware_version"),
              "connection_type": body.get("connection_type"),
              "status": "online",  # Kích hoạt trạng thái trực tuyến
              "last_heartbeat_at": fields.Datetime.now(),  # Cập nhật thời điểm nhận gói tin cuối
          }
          
          # Tìm bộ điều khiển theo số seri phần cứng duy nhất
          controller = self.search([("serial_number", "=", controller_id)], limit=1)
          if not controller:
              return {"success": False, "message": "Controller not found"}
              
          # Ghi các thông số mới vào database
          controller.write(vals)
          
          # Trả về kết quả xác nhận đăng ký thành công
          return {
              "message": "Success",
              "controller_id": controller.id,
              "name": controller.name,
              "status": "200 OK"
          }
      ```
* ├── **Feature**: API DeviceRegister - Tiếp nhận và tự động đăng ký các thiết bị con vật lý kết nối với Bộ điều khiển
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Bộ điều khiển khai báo danh sách các thiết bị con kết nối trực tiếp vào các cổng của nó để Odoo quản lý.
    - *HTTP Method & Route*: `POST` `/api/v1/device-register`
    - *Tham số đầu vào (Payload JSON)*:
      - `device_sn`: Số seri duy nhất của thiết bị con (ví dụ: "DN91058915").
      - `area`: Khu vực lắp đặt (ví dụ: "Cổng trước/sau").
      - `device-model`: Dòng máy thiết bị con (ví dụ: "ZKTeco").
      - `port/channel`: Cổng kết nối vật lý trên bộ điều khiển (ví dụ: "relay_01").
      - `firmware_version`: Phiên bản phần mềm nhúng.
      - `system_version`: Phiên bản hệ thống.
    - *Logic xử lý Odoo Backend*:
      - Tra cứu thiết bị con trong model `t4.gate_keeper.device` theo trường duy nhất `serial_number = device_sn`.
      - Nếu chưa tồn tại, tự động tạo mới thiết bị con và liên kết Many2one với bộ điều khiển cha.
      - Nếu đã tồn tại, cập nhật cổng kết nối `port_or_channel` và chuyển trạng thái hoạt động thành `online`.
    - *Ví dụ code API mẫu (GK Device)*:
      ```python
      @endpoint(name="DeviceRegister")
      def device_register(self):
          # Đọc payload từ HTTP POST request body dạng JSON
          body = get_body()
          device_sn = body.get("device_sn")
          port = body.get("port/channel")
          dev_model_name = body.get("device-model")
          
          # Tra cứu thiết bị con theo số seri duy nhất trong bảng t4.gate_keeper.device
          device = self.search([("serial_number", "=", device_sn)], limit=1)
          if not device:
              return {"success": False, "message": "Device not pre-configured"}
              
          # Tra cứu dòng máy tương ứng trong database (ví dụ ZKTeco, Hikvision)
          dev_model = self.env["t4.gate_keeper.device_model"].search([("name", "=", dev_model_name)], limit=1)
          
          # Cập nhật thông tin cổng vật lý và chuyển trạng thái thiết bị sang online
          vals = {
              "status": "online",
              "port_or_channel": port,
          }
          if dev_model:
              vals["device_model_id"] = dev_model.id
              
          # Ghi đè cấu hình mới xuống database
          device.write(vals)
          
          # Trả về kết quả xác nhận đăng ký thành công thiết bị con
          return {
              "message": "Success",
              "status": "200 OK",
              "device_id": device.id,
              "controller_name": device.controller_id.name or "",
              "device_name": device.name or ""
          }
      ```
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
    - *Ví dụ code API mẫu (GK Controller)*:
      ```python
      @endpoint(name="ControllerGetConfig")
      def get_config(self):
          # Đọc thông số đầu vào
          body = get_body()
          serial_number = body.get("serial_number")
          
          # Tìm bộ điều khiển đang yêu cầu cấu hình
          controller = self.search([("serial_number", "=", serial_number)], limit=1)
          if not controller:
              return {"success": False, "message": "Controller not found"}
          
          # Duyệt qua các thiết bị con trực thuộc để xây dựng mảng thông số kỹ thuật
          devices_data = []
          for dev in controller.device_ids:
              algos = []
              # Lấy các thuật toán sinh trắc học mà dòng máy này hỗ trợ
              for algo in dev.device_model_id.algorithm_ids:
                  algos.append({
                      "name": algo.name,
                      "type": algo.bio_type,
                      "version": algo.version or "1.0"
                  })
              devices_data.append({
                  "device_id": dev.id,
                  "name": dev.name,
                  "serial_number": dev.serial_number,
                  "port_or_channel": dev.port_or_channel,
                  "supported_algorithms": algos
              })
              
          # Xuất dữ liệu cấu hình chi nhánh gồm Múi giờ timezone và thiết bị con
          return {
              "message": "Success",
              "status": "200 OK",
              "timezone": controller.branch_id.timezone or "UTC",
              "devices": devices_data
          }
      ```
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
        - Nếu trạng thái thiết bị con chuyển sang ngoại tuyến (`offline` hoặc `controller_offline`) và thiết bị đó đã được gán vào một khu vực (`area_id`), hệ thống sẽ kiểm tra xem đã có cảnh báo đang hoạt động nào chưa. Nếu chưa, tự động tạo mới bản ghi `t4.gate_keeper.area_warning` with warning type `device_issue`.
        - Nếu thiết bị con trực tuyến trở lại (`online`), hệ thống tự động gọi hàm `action_resolve()` để đóng (đổi trạng thái sang `resolved`) toàn bộ các cảnh báo ngoại tuyến liên quan của thiết bị này.
    - *Ví dụ code API mẫu (GK Controller)*:
      ```python
      @endpoint(name="ControllerHeartbeat")
      def controller_heartbeat(self):
          # Lấy thông tin thiết bị gửi nhịp tim
          body = get_body()
          controller_id = body.get("controller_id")
          devices_status = body.get("devices_status", [])
          
          controller = self.search([("serial_number", "=", controller_id)], limit=1)
          if not controller:
              return {"success": False, "message": "Controller not found"}
              
          # Đánh dấu Controller đang online và cập nhật thời điểm giao tiếp cuối cùng
          controller.write({
              "status": "online",
              "last_heartbeat_at": fields.Datetime.now()
          })
          
          # Cập nhật trạng thái từng thiết bị con
          for dev_info in devices_status:
              dev_sn = dev_info.get("device_sn")
              status = dev_info.get("status")
              device = self.env["t4.gate_keeper.device"].search([("serial_number", "=", dev_sn)], limit=1)
              if device:
                  # Hàm write() trên Device sẽ tự kích hoạt tạo/đóng Area Warning
                  device.write({"status": status})
                  
          return {
              "message": "Success",
              "status": "200 OK"
          }
      ```
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
    - *Ví dụ code API mẫu (GK Controller)*:
      ```python
      @endpoint(name="ControllerEmployeeSync")
      def employee_sync(self):
          # Lấy tham số đồng bộ
          body = get_body()
          serial = body.get("serial_number")
          last_sync_str = body.get("last_sync_at")
          
          controller = self.search([("serial_number", "=", serial)], limit=1)
          if not controller:
              return {"success": False, "message": "Controller not found"}
              
          # Dự phòng: nếu tham số trống, dùng ngày đồng bộ cuối lưu trong Odoo
          last_sync = fields.Datetime.from_string(last_sync_str) if last_sync_str else controller.last_sync_at
          
          # Tìm nhân sự có thay đổi thông tin (write_date > last_sync) thuộc chi nhánh của Controller
          updated_employees = self.env["t4.gate_keeper.employee"].search([
              ("write_date", ">", last_sync),
              ("branch_id", "=", controller.branch_id.id)
          ])
          
          # Xác định hành động nạp mới/cập nhật hay xóa
          sync_data = []
          for emp in updated_employees:
              sync_data.append({
                  "emp_id": emp.emp_id,
                  "action": "update" if emp.active else "delete"
              })
              
          # Xuất mảng danh sách các thay đổi
          return {
              "message": "Success",
              "status": "200 OK",
              "sync_timestamp": fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              "changes": sync_data
          }
      ```
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
    - *Ví dụ code API mẫu (GK Employee)*:
      ```python
      @endpoint(name="EmployeeBiometricGet")
      def get_biometric(self):
          body = get_body()
          emp_id = body.get("emp_id")
          controller_id = body.get("controller_id")
          
          # Xác thực sự tồn tại của thiết bị và nhân viên
          controller = self.env["t4.gate_keeper.controller"].search([("serial_number", "=", controller_id)], limit=1)
          employee = self.search([("emp_id", "=", emp_id)], limit=1)
          
          if not controller or not employee:
              return {"success": False, "message": "Controller or Employee not found"}
              
          # Lấy danh sách ID các thuật toán sinh trắc học được hỗ trợ bởi các thiết bị con của Controller này
          supported_algos = controller.device_ids.mapped("device_model_id.algorithm_ids.id")
          
          # Tìm các bản ghi vân tay/khuôn mặt tương thích thuật toán của thiết bị
          biometrics = self.env["t4.gate_keeper.employee.biometric"].search([
              ("employee_id", "=", employee.id),
              ("algorithm_id", "in", supported_algos)
          ])
          
          # Chuyển đổi nhị phân sang Base64 chuỗi để gửi qua JSON
          templates = []
          for bio in biometrics:
              templates.append({
                  "biometric_type": bio.bio_type,
                  "finger_index": bio.finger_index,
                  "algorithm_name": bio.algorithm_id.name,
                  "algorithm_version": bio.algorithm_id.version or "1.0",
                  "template": base64.b64encode(bio.template).decode("utf-8") if bio.template else ""
              })
              
          # Trả về gói thông tin sinh trắc học đầy đủ của nhân sự
          return {
              "message": "Success",
              "status": "200 OK",
              "emp_id": employee.emp_id,
              "name": employee.name,
              "biometrics": templates
          }
      ```
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
    - *Ví dụ code API mẫu (GK Controller)*:
      ```python
      @endpoint(name="ControllerSyncAck")
      def sync_ack(self):
          body = get_body()
          controller_id = body.get("controller_id")
          sync_time = body.get("sync_timestamp")
          
          # Tìm bộ điều khiển gửi báo cáo
          controller = self.search([("serial_number", "=", controller_id)], limit=1)
          if not controller:
              return {"success": False, "message": "Controller not found"}
              
          # Lưu mốc thời gian đồng bộ thành công gần nhất
          controller.write({
              "last_sync_at": fields.Datetime.from_string(sync_time) if sync_time else fields.Datetime.now()
          })
          
          return {
              "message": "Success",
              "status": "200 OK"
          }
      ```
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
    - *Ví dụ code API mẫu (GK Access Log)*:
      ```python
      @endpoint(name="AccessLogUpload")
      def upload_logs(self):
          body = get_body()
          logs = body.get("logs", [])
          created_count = 0
          
          # Duyệt mảng log quẹt thẻ thô
          for log in logs:
              # Ánh xạ số seri đầu đọc sang bản ghi thiết bị trong Odoo
              device = self.env["t4.gate_keeper.device"].search([("serial_number", "=", log.get("device_serial"))], limit=1)
              # Ánh xạ UUID nhân viên
              employee = self.env["t4.gate_keeper.employee"].search([("emp_id", "=", log.get("emp_id"))], limit=1)
              
              if device and employee:
                  # Tạo bản ghi log quẹt thẻ; logic kiểm tra giờ giấc/timezone nằm trong hook create()
                  self.create({
                      "device_id": device.id,
                      "employee_id": employee.id,
                      "card_code": log.get("card_code"),
                      "access_time": fields.Datetime.from_string(log.get("access_time")),
                      "direction": log.get("direction"),
                      "verification_type": log.get("verification_type"),
                      "sync_status": "success"
                  })
                  created_count += 1
                  
          # Trả về tổng số lượng log đã tiếp nhận và xử lý thành công
          return {
              "message": "Success",
              "status": "200 OK",
              "processed_count": created_count
          }
      ```
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
    - *Ví dụ code API mẫu (GK Controller)*:
      ```python
      @endpoint(name="ControllerCommandPoll")
      def command_poll(self):
          body = get_body()
          controller_id = body.get("controller_id")
          
          # Tìm bộ điều khiển
          controller = self.search([("serial_number", "=", controller_id)], limit=1)
          if not controller:
              return {"success": False, "message": "Controller not found"}
              
          # Lọc danh sách lệnh điều khiển từ xa đang ở trạng thái 'pending'
          commands = self.env["t4.gate_keeper.command"].search([
              ("controller_id", "=", controller.id),
              ("state", "=", "pending")
          ])
          
          res = []
          for cmd in commands:
              # Đổi trạng thái lệnh sang 'sending' để tránh tải trùng lặp
              cmd.write({"state": "sending"})
              res.append({
                  "command_id": cmd.id,
                  "action": cmd.action_type,
                  "device_serial": cmd.device_id.serial_number,
                  "parameters": cmd.parameters
              })
              
          # Xuất mảng danh sách lệnh chờ thực thi xuống thiết bị
          return {
              "message": "Success",
              "status": "200 OK",
              "commands": res
          }
      ```
* └── **Feature**: API ControllerCommandAck - Tiếp nhận báo cáo kết quả thực thi lệnh điều khiển từ xa (Mở/Khóa cửa) từ thiết bị
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Bộ điều khiển gửi xác nhận kết quả sau khi đã kích hoạt rơ-le mở cửa vật lý thành công hoặc thất bại.
    - *HTTP Method & Route*: `POST` `/api/v1/confirmation`
    - *Tham số đầu vào (Payload JSON)*:
      - `controller_id`: Số seri của bộ điều khiển.
      - `command_id`: Mã định danh lệnh đã nhận từ Odoo.
      - `execution_message`: Tin nhắn báo cáo chi tiết hoặc mã lỗi phần cứng (nếu có).
    - *Logic xử lý Odoo Backend*:
      - Tìm bản ghi lệnh khớp với `command_id`.
      - Cập nhật trạng thái lệnh sang `success` hoặc `failed` và ghi nhận nội dung `execution_message` phục vụ kiểm tra lỗi.
    - *Ví dụ code API mẫu (GK Controller)*:
      ```python
      @endpoint(name="ControllerCommandAck")
      def command_ack(self):
          body = get_body()
          command_id = body.get("command_id")
          msg = body.get("execution_message")
          
          # Tra cứu lệnh điều khiển từ ID
          command = self.env["t4.gate_keeper.command"].browse(command_id)
          if not command.exists():
              return {"success": False, "message": "Command not found"}
              
          # Ghi nhận trạng thái hoàn tất thành công và lưu thông báo kết quả của rơ-le phần cứng
          command.write({
              "state": "success",
              "execution_message": msg
          })
          
          return {
              "message": "Success",
              "status": "200 OK"
          }
      ```

### [LOGIC] Nhật ký thiết bị thô (Device Log) và Xử lý Batch
* ├── **Feature**: Tạo model Nhật ký thiết bị thô `t4.gate_keeper.device_log` (`models/gk_device_log.py`)
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Tạo bảng lưu trữ vết dữ liệu thô (raw payload) được gửi từ Controller/Device lên hệ thống Backend trước khi qua bộ xử lý nghiệp vụ của Odoo. Đây là lớp bảo vệ dữ liệu nguyên bản, phục vụ đắc lực cho công tác gỡ lỗi (debugging), kiểm toán dữ liệu và giám sát chất lượng truyền tin của phần cứng.
    - *Cấu trúc trường dữ liệu*:
      - `controller_id` (Many2one, liên kết `t4.gate_keeper.controller`): Xác định bộ điều khiển nguồn gửi gói tin log thô.
      - `raw_data` (Text, bắt buộc): Chuỗi JSON thô nguyên bản nhận được từ HTTP request body của thiết bị.
      - `status` (Selection: `draft`/`processed`/`failed`, default `draft`): Trạng thái xử lý của gói log thô.
      - `error_message` (Text): Ghi lại thông tin lỗi chi tiết (exception traceback) nếu quá trình parse hoặc xử lý dữ liệu thô thất bại.
      - `log_type` (Selection: `heartbeat`/`access_log`/`command_ack`/`register`): Xác định loại nghiệp vụ của gói tin thô.
      - `received_at` (Datetime, default `Datetime.now()`): Thời điểm hệ thống tiếp nhận gói tin thô.
    - *Quy tắc bảo mật & dữ liệu*: Bản ghi này chỉ cho phép tạo mới từ hệ thống/API, chặn hoàn toàn quyền sửa đổi thủ công trên giao diện của mọi nhóm người dùng để bảo toàn tính toàn vẹn và trung thực của vết log.
* ├── **Feature**: Xây dựng logic xử lý batch offline
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Giải quyết triệt để bài toán bộ điều khiển bị mất mạng tạm thời (offline) phải lưu trữ cục bộ (buffering) hàng ngàn sự kiện quẹt thẻ. Khi kết nối mạng phục hồi, thiết bị sẽ gửi đồng loạt một payload chứa mảng lớn các sự kiện (batch upload).
    - *Chi tiết logic xử lý*:
      - Hệ thống tiếp nhận HTTP POST request chứa danh sách mảng các sự kiện (`logs` array).
      - Tự động tạo bản ghi `t4.gate_keeper.device_log` ở trạng thái `draft` và lưu trữ toàn bộ chuỗi JSON thô nhận được.
      - Tiến hành phân tích (parse) chuỗi JSON:
        - **Sắp xếp thời gian**: Sắp xếp mảng các sự kiện quẹt thẻ tăng dần theo mốc thời gian sự kiện thực tế (`access_time`) trước khi đưa vào xử lý. Việc này đảm bảo các bản ghi cũ được tạo trước bản ghi mới, giúp các hàm tính toán vị trí hiện tại (`presence_state`, `current_area_id`) của nhân sự trên Odoo luôn cập nhật đúng trạng thái mới nhất.
        - **Tối ưu hóa hiệu năng (Batch Insert)**: Gom nhóm các bản ghi hợp lệ theo thiết bị và nhân viên, sau đó thực hiện một câu lệnh tạo lô (`create()` nhận mảng list dicts) thay vì tạo từng dòng một trong vòng lặp nhằm tối ưu hóa hiệu năng truy vấn database PostgreSQL.
        - **Quản lý Transaction**: Toàn bộ quá trình xử lý lô được bọc trong một database transaction. Nếu thành công, trạng thái bản ghi `t4.gate_keeper.device_log` chuyển sang `processed`. Nếu xảy ra bất kỳ lỗi runtime nào, hệ thống thực hiện rollback transaction, ghi nhận traceback lỗi chi tiết vào trường `error_message` và chuyển trạng thái bản ghi thô thành `failed`.
* └── **Feature**: Thiết kế giao diện Nhật ký thiết bị thô (`views/gk_device_log_views.xml`)
  * **Mô tả chi tiết**:
    - *Mục tiêu*: Cung cấp giao diện quản trị cho các kỹ thuật viên vận hành hệ thống (Technicians / System Administrators) dễ dàng tra cứu, kiểm tra luồng dữ liệu thô và khắc phục sự cố phần cứng.
    - *Chi tiết giao diện*:
      - **List view**:
        - Hiển thị danh sách các bản ghi nhật ký thô.
        - Các cột hiển thị: Thời gian nhận (`received_at`), Bộ điều khiển (`controller_id`), Loại sự kiện (`log_type`), Trạng thái (`status`), Thông báo lỗi ngắn (`error_message` - rút gọn).
        - Sử dụng thẻ màu (Bootstrap decoration badges) để phân biệt trạng thái trực quan: Màu xanh lá cho `processed`, màu đỏ cho `failed`, và màu xám cho `draft`.
      - **Form view**:
        - Trình bày thông tin theo các Groupbox hợp lý:
          - *Thông tin chung*: Bộ điều khiển, Loại sự kiện, Thời gian nhận.
          - *Trạng thái xử lý*: Trạng thái, Thông báo lỗi chi tiết (nếu có).
          - *Dữ liệu thô*: Hiển thị trường `raw_data` dưới dạng khối mã nguồn lớn (text field read-only) giúp kỹ thuật viên dễ dàng đọc cấu trúc JSON và sao chép chuỗi JSON phục vụ debug lỗi.
      - **Search view & Filters**:
        - Thanh tìm kiếm nhanh theo mã seri Bộ điều khiển.
        - Các bộ lọc nhanh (Filters) theo trạng thái: "Lỗi xử lý (Failed)", "Chưa xử lý (Draft)", "Đã xử lý (Processed)".
        - Gom nhóm (Group by) theo: Bộ điều khiển, Loại sự kiện và Trạng thái xử lý.

## PHẦN 5 — MODULE 5: GHI NHẬN NHẬT KÝ SỰ KIỆN RA VÀO (ACCESS LOGS)
*Mục đích: Chuẩn hóa dữ liệu sự kiện ra vào và theo dõi vị trí nhân viên (Model: Access Log).*

### [MODEL] Cơ sở dữ liệu Nhật ký ra vào
* ├── **Feature**: Tạo model Nhật ký ra vào `t4.gate_keeper.access_log` (`models/gk_access_log.py`)
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.access_log` lưu vết các sự kiện quẹt thẻ thực tế của nhân viên.
    - Khai báo các trường liên kết bắt buộc: Nhân viên `employee_id` (Many2one tới `t4.gate_keeper.employee`, required=True) và Thiết bị con `device_id` (Many2one tới `t4.gate_keeper.device`, required=True).
    - Khai báo các trường thông tin quẹt thẻ: Mã thẻ `card_code` (Char), thời gian sự kiện quẹt thẻ `access_time` (Datetime, required=True), chiều di chuyển `direction` (Selection: `in`/`out`/`unknown`, required=True, default `unknown`), và phương thức xác thực `verification_type` (Selection: `card`/`fingerprint`/`face`/`other`).
    - Khai báo trường trạng thái đồng bộ log `sync_status` (Selection: `success`/`pending`/`failed`, default `success`).
    - Khai báo trường tự động tính toán và lưu trữ Khu vực `area_id` (Many2one tới `t4.gate_keeper.area`, store=True) thông qua `related="device_id.area_id"`.
    - Khai báo trường tự động tính toán và lưu trữ Chi nhánh `branch_id` (Many2one tới `t4.gate_keeper.branch`, store=True) thông qua `related="device_id.controller_id.branch_id"`.
* ├── **Feature**: Ràng buộc bảo mật dữ liệu chặn sửa đổi nhật ký
  * **Mô tả chi tiết**:
    - Viết hàm ghi đè phương thức sửa bản ghi `write()` trên model `t4.gate_keeper.access_log`. Nếu phát hiện bất kỳ hành động cập nhật nào, lập tức ném ra lỗi `ValidationError` kèm theo nội dung dịch thuật tiếng Việt để khóa cứng dữ liệu log.
    - Viết hàm ghi đè phương thức xóa bản ghi `unlink()` trên model `t4.gate_keeper.access_log`. Mọi hành động xóa log quẹt thẻ đều bị ngăn chặn và ném ra cảnh báo lỗi `ValidationError` tương tự để tránh việc gian lận hoặc phá hoại dữ liệu.
* └── **Feature**: Viết logic tự động cập nhật vị trí và trạng thái hiện diện của nhân viên
  * **Mô tả chi tiết**:
    - Viết hàm xử lý trong sự kiện tạo bản ghi `@api.model_create_multi` hoặc `create()` của model Access Log.
    - Sau khi bản ghi nhật ký quẹt thẻ được tạo thành công, tiến hành tra cứu bản ghi nhân viên tương ứng (`employee_id`).
    - **Nếu chiều di chuyển là vào (`direction == 'in'`)**: Cập nhật trạng thái hiện diện của nhân viên thành đang ở văn phòng (`presence_state = 'inside'`) và gán vị trí khu vực hiện tại `current_area_id` bằng khu vực của thiết bị quẹt thẻ (`area_id`).
    - **Nếu chiều di chuyển là ra (`direction == 'out'`)**: Cập nhật trạng thái hiện diện của nhân viên thành đang ở ngoài (`presence_state = 'outside'`) và xóa sạch thông tin khu vực hiện tại (`current_area_id = False`).

### [VIEW] Giao diện Nhật ký ra vào
* └── **Feature**: Thiết kế List view, Form view và Search view cho Nhật ký ra vào (`views/gk_access_log_views.xml`)
  * **Mô tả chi tiết**:
    - **List view**: Thiết kế bảng danh sách hiển thị các cột quan trọng: Nhân viên, Thời gian quẹt thẻ, Chiều ra/vào (sử dụng icon hoặc badge màu sắc), Phương thức xác thực, Thiết bị nhận dạng, Khu vực và Chi nhánh.
    - **Form view**: Thiết lập toàn bộ các trường hiển thị ở chế độ chỉ đọc (`readonly="1"`). Phân nhóm rõ ràng thành: *Thông tin nhân sự* (Nhân viên, Mã thẻ), *Sự kiện quẹt thẻ* (Thời gian quẹt, Chiều ra/vào, Trạng thái xác thực), và *Thông tin địa lý* (Thiết bị con, Khu vực liên đới, Chi nhánh liên đới).
    - **Search view**:
      - Cho phép tìm kiếm nhanh theo tên nhân viên và mã thẻ.
      - Thiết lập các bộ lọc nhanh (Filters): "Chiều vào (In)", "Chiều ra (Out)", "Xác thực khuôn mặt (Face)", "Xác thực vân tay (Fingerprint)".
      - Thiết lập tính năng gom nhóm (Group by) theo: Nhân viên, Chi nhánh, Khu vực, Ngày quẹt thẻ (theo ngày/tháng/năm).

---

## PHẦN 6 — MODULE 6: CẢNH BÁO VÀ CHÍNH SÁCH BẢO MẬT (WARNINGS & POLICIES)
*Mục đích: Phát hiện vi phạm an ninh và cảnh báo trực quan (Model: Area Warning, Alert Policy).*

### [MODEL] Cấu hình Cảnh báo và Chính sách bảo mật
* ├── **Feature**: Tạo model Loại cảnh báo `t4.gate_keeper.area_warning_type` (`models/gk_area_warning_type.py`)
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.area_warning_type` kèm mô tả `_description = "Area Warning Type"`.
    - Khai báo các trường dữ liệu: Tên loại cảnh báo `name` (Char, bắt buộc, ví dụ: "Truy cập trái phép"), Mã loại cảnh báo `code` (Char, bắt buộc, unique, ví dụ: `invalid_access`).
    - Khởi tạo tệp tin dữ liệu XML `data/gk_area_warning_type_data.xml` nạp sẵn 2 loại cảnh báo chuẩn:
      - Loại 1: Mã `invalid_access` (Vi phạm quy tắc truy cập như ngoài giờ làm việc, ngày nghỉ hoặc cấm vào).
      - Loại 2: Mã `device_issue` (Lỗi phần cứng như thiết bị hoặc bộ điều khiển bị ngoại tuyến).
* ├── **Feature**: Tạo model Cảnh báo khu vực `t4.gate_keeper.area_warning` (`models/gk_area_warning.py`)
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.area_warning` kèm mô tả `_description = "Area Warning"`.
    - Khai báo các trường liên kết bắt buộc: Khu vực xảy ra cảnh báo `area_id` (Many2one tới `t4.gate_keeper.area`, required=True), Loại cấu hình cảnh báo `warning_type_id` (Many2one tới `t4.gate_keeper.area_warning_type`, required=True).
    - Khai báo các trường liên kết tùy chọn: Thiết bị con nguồn sự cố `device_id` (Many2one), Nhân viên vi phạm `employee_id` (Many2one), Nhật ký quẹt thẻ liên quan `access_log_id` (Many2one).
    - Khai báo các trường chi tiết lỗi: Chi tiết cảnh báo `description` (Text), Trạng thái xử lý `state` (Selection: `warning`/`resolved`, mặc định `warning`).
    - Khai báo các trường xử lý sự cố: Trực ban giải quyết `resolved_by_id` (Many2one tới `res.users`), thời điểm giải quyết `resolved_at` (Datetime), ghi chú giải quyết `resolution_notes` (Text).
    - Viết hàm xử lý nghiệp vụ `action_resolve()`: Cho phép chuyển trạng thái bản ghi sang `resolved`, tự động điền `resolved_by_id = self.env.user` và `resolved_at = Datetime.now()`.
* └── **Feature**: Tạo model Chính sách bảo mật `t4.gate_keeper.alert_policy` (`models/gk_alert_policy.py`)
  * **Mô tả chi tiết**:
    - Đăng ký model `t4.gate_keeper.alert_policy` cấu hình quy tắc an ninh cho các khu vực.
    - Khai báo các trường: Tên chính sách `name` (Char, bắt buộc), Chi nhánh áp dụng `branch_id` (Many2one tới `t4.gate_keeper.branch`, bắt buộc).
    - Khai báo các trường liên kết Many2many: Các khu vực bảo vệ `area_ids` (`t4.gate_keeper.area`), Các nhóm nhân sự được phép ra vào `employee_group_ids` (`t4.gate_keeper.employee_group`).
    - Khai báo các trường cấu hình thời gian: Giờ bắt đầu cho phép `start_hour` (Float, ví dụ: 8.00 cho 08:00), Giờ kết thúc cho phép `end_hour` (Float, ví dụ: 17.00 cho 17:00), Cấu hình ngày nghỉ `allow_weekend` (Boolean, mặc định False).

### [LOGIC] Động cơ đánh giá quy tắc bảo mật (Security Engine)
* ├── **Feature**: Viết Hook kiểm tra vi phạm bảo mật khi tạo Access Log
  * **Mô tả chi tiết**:
    - Viết logic kiểm tra quy tắc an ninh trong hook `create()` của model Access Log.
    - Lấy thông tin múi giờ của chi nhánh (`branch_id.timezone`). Quy đổi thời gian quẹt thẻ `access_time` sang múi giờ địa phương của chi nhánh đó bằng thư viện `pytz`.
    - Tìm kiếm các chính sách bảo mật (`t4.gate_keeper.alert_policy`) đang áp dụng cho khu vực hiện tại (`area_id`).
    - Đánh giá các quy tắc vi phạm:
      - **Vi phạm ngày nghỉ**: Nếu rơi vào Thứ Bảy hoặc Chủ Nhật mà chính sách cấu hình `allow_weekend == False`.
      - **Vi phạm giờ giấc**: Nếu giờ địa phương nằm ngoài khung giờ cho phép (`start_hour` đến `end_hour`).
      - **Vi phạm quyền truy cập**: Nếu nhân sự quẹt thẻ không nằm trong các nhóm được quyền ra vào (`employee_group_ids`) của khu vực đó.
    - Nếu phát hiện vi phạm, hệ thống tự động tạo mới một bản ghi cảnh báo khu vực `t4.gate_keeper.area_warning` với loại cảnh báo là `invalid_access`, ghi nhận chi tiết mô tả lỗi vào trường `description` và đặt trạng thái là `warning`.
* └── **Feature**: Viết logic tự động tạo/đóng cảnh báo thiết bị ngoại tuyến
  * **Mô tả chi tiết**:
    - **Khi thiết bị ngoại tuyến**: Viết logic bắt sự kiện thay đổi trạng thái của Thiết bị (`t4.gate_keeper.device`). Nếu thiết bị chuyển sang trạng thái ngoại tuyến (`offline` hoặc `controller_offline`) và thiết bị đó đã được lắp đặt tại một khu vực (`area_id`), hệ thống kiểm tra và tự động tạo mới một cảnh báo loại lỗi thiết bị `device_issue` ở trạng thái hoạt động `warning`.
    - **Khi thiết bị trực tuyến trở lại**: Khi trạng thái thiết bị chuyển về trực tuyến `online`, hệ thống tự động tìm và gọi hàm `action_resolve()` để đóng (đổi trạng thái sang `resolved`) toàn bộ cảnh báo lỗi thiết bị `device_issue` đang hoạt động liên quan đến thiết bị này.

### [VIEW] Giao diện giám sát an ninh
* ├── **Feature**: Thiết kế List view và Form view cho Cảnh báo khu vực (`views/gk_area_warning_views.xml`)
  * **Mô tả chi tiết**:
    - **List view**: Hiển thị bảng danh sách các vi phạm an ninh: Khu vực xảy ra, Loại lỗi, Mô tả chi tiết vi phạm, Nhân viên liên quan, Trạng thái (đỏ badge `warning`, xanh badge `resolved`), Người giải quyết và Thời gian giải quyết.
    - **Form view**:
      - Nhóm thông tin chung: Khu vực, Thiết bị con, Nhân viên vi phạm, Nhật ký ra vào liên quan.
      - Nhóm giải quyết sự cố: Trạng thái, Người giải quyết, Thời điểm giải quyết, Ghi chú xử lý (cho phép trực ban nhập ghi chú).
      - **Action Button "Resolve Warning"**: Tích hợp nút bấm gọi hàm `action_resolve()` trên thanh menu tiêu đề (header) của Form view, nút này chỉ hiển thị khi bản ghi ở trạng thái `warning` để trực ban xác nhận xử lý nhanh.
    - **Search view**: Tìm kiếm nhanh theo khu vực. Filters lọc cảnh báo "Đang hoạt động (Warning)" và "Đã giải quyết (Resolved)". Group by theo Khu vực và Loại cảnh báo.
* └── **Feature**: Thiết kế List view và Form view cho Chính sách bảo mật và Loại cảnh báo (`views/gk_alert_policy_views.xml`, `views/gk_area_warning_type_views.xml`)
  * **Mô tả chi tiết**:
    - **Giao diện Chính sách bảo mật (`gk_alert_policy_views.xml`)**:
      - List view hiển thị: Tên chính sách, Chi nhánh áp dụng, Khung giờ cho phép (`start_hour` - `end_hour`), Trạng thái ngày cuối tuần.
      - Form view cho phép cấu hình chi tiết thông số: chọn chi nhánh, các khu vực áp dụng, các nhóm nhân sự được ra vào, và cấu hình các khung giờ giới hạn.
    - **Giao diện Loại cảnh báo (`gk_area_warning_type_views.xml`)**:
      - Thiết kế List view và Form view cơ bản hiển thị mã và tên các loại cảnh báo (`invalid_access`, `device_issue`).

## PHẦN 7 — MODULE 7: MÀN HÌNH TRỰC BAN GIÁM SÁT THỜI GIAN THỰC (REAL-TIME DUTY MONITORING)
*Mục đích: Cung cấp giao diện trực quan cho nhân viên bảo vệ/trực ban theo dõi luồng quẹt thẻ và cảnh báo khẩn cấp thời gian thực.*

### [DASHBOARD] Giao diện Giám sát trực ban
* ├── **Feature**: Thiết kế giao diện Dashboard Trực ban (views/gk_duty_dashboard_views.xml, templates/gk_duty_dashboard_templates.xml)
  * **Mô tả chi tiết**:
    - Thiết kế màn hình trực ban sử dụng Client Action hoặc template OWL/QWeb XML tích hợp hiển thị trạng thái hoạt động nhanh của toàn bộ Chi nhánh, số lượng nhân sự đang có mặt tại từng khu vực.
    - Tích hợp các widget đếm số lượng cảnh báo an ninh chưa giải quyết (`state == 'warning'`) và hiển thị trực quan danh sách các thiết bị con ngoại tuyến.
* ├── **Feature**: Cập nhật danh sách quẹt thẻ thời gian thực (Real-time Event Feed)
  * **Mô tả chi tiết**:
    - Xây dựng cơ chế thông báo bằng Odoo Bus (`bus.bus` hoặc long-polling/websocket) để cập nhật trực tiếp luồng quẹt thẻ của nhân viên lên màn hình trực ban mà không cần tải lại trang.
    - Tự động hiển thị ảnh chân dung (avatar) của nhân sự, tên nhân sự, vị trí quẹt thẻ và hướng đi (`in`/`out`) khi có log quẹt thẻ mới gửi lên hệ thống.
* └── **Feature**: Cơ chế phát âm thanh và pop-up cảnh báo khẩn cấp
  * **Mô tả chi tiết**:
    - Tự động hiển thị hộp thoại pop-up nổi lên giao diện (Sticky Alert popup) ngay lập tức khi phát hiện có cảnh báo vi phạm bảo mật loại `invalid_access` được kích hoạt.
    - Phát âm thanh bip ngắn để thu hút sự chú ý của trực ban. Cho phép nhấn xem nhanh chi tiết cảnh báo hoặc chuyển hướng đến Form giải quyết cảnh báo.

---

## PHẦN 8 — MODULE 8: HỆ THỐNG BÁO CÁO THỐNG KÊ (REPORTING SYSTEM)
*Mục đích: Cung cấp các công cụ kết xuất dữ liệu, biểu đồ phân tích hiệu suất ra vào và vi phạm bảo mật phục vụ công tác quản lý.*

### [REPORT] Kết xuất dữ liệu và biểu đồ phân tích
* ├── **Feature**: Thiết kế Báo cáo biểu đồ thống kê ra vào (Graph & Pivot Views) (`views/gk_access_log_views.xml`)
  * **Mô tả chi tiết**:
    - Tích hợp thêm cấu trúc thẻ `<graph>` và `<pivot>` cho model Nhật ký ra vào `t4.gate_keeper.access_log`.
    - Hỗ trợ biểu đồ hình cột/hình tròn phân tích tần suất ra vào theo múi giờ làm việc, theo từng Chi nhánh hoặc theo nhóm nhân sự.
    - Hỗ trợ Pivot view thống kê chi tiết số lượt quẹt thẻ theo từng phương thức (vân tay, thẻ từ, khuôn mặt).
* ├── **Feature**: Thiết kế Báo cáo phân tích cảnh báo vi phạm an ninh
  * **Mô tả chi tiết**:
    - Cấu hình Graph view và Pivot view cho model Cảnh báo khu vực `t4.gate_keeper.area_warning`.
    - Phân tích thống kê số lượng vi phạm phát hiện theo từng Khu vực (nhằm xác định điểm yếu an ninh) và đo lường thời gian trung bình trực ban xử lý đóng cảnh báo.
* └── **Feature**: Tích hợp tính năng kết xuất dữ liệu quẹt thẻ ra file Excel (Excel Export)
  * **Mô tả chi tiết**:
    - Xây dựng nút bấm hoặc tác vụ xuất báo cáo dữ liệu (Excel report) định dạng bảng tính `.xlsx`.
    - Ghi nhận chi tiết thông tin: mã nhân viên, họ tên, chi nhánh, khu vực, thời điểm quẹt, và hướng đi phục vụ làm dữ liệu đối soát chấm công hoặc kiểm toán an ninh.

---

## PHẦN 9 — PHẦN KIỂM THỬ VÀ KIỂM SOÁT CHẤT LƯỢNG (TESTING & QUALITY ASSURANCE)
*Mục đích: Đảm bảo độ tin cậy và chất lượng hệ thống thông qua kiểm thử tự động.*

### [TEST] Kiểm thử tự động (Unit Test)
* ├── **Feature**: Viết các test case kiểm thử logic xử lý múi giờ địa phương (`tests/test_gk_timezone.py`)
  * **Mô tả chi tiết**:
    - Viết các test case trong thư mục `tests/` giả lập các sự kiện quẹt thẻ gửi lên từ các chi nhánh có múi giờ khác nhau (ví dụ: Tokyo, TP.HCM).
    - Đảm bảo hệ thống quy đổi và đánh giá đúng khung giờ vi phạm theo giờ địa phương của chi nhánh đó mà không bị ảnh hưởng bởi múi giờ của máy chủ Odoo.
* └── **Feature**: Viết unit test kiểm tra cơ chế đồng bộ nhân sự một chiều từ Odoo HR (`tests/test_gk_employee_sync.py`)
  * **Mô tả chi tiết**:
    - Viết test case tạo hồ sơ nhân sự trên `hr.employee`, xác minh hệ thống tự động đồng bộ sang `t4.gate_keeper.employee`.
    - Chặn đứng mọi hành vi tạo trực tiếp trên giao diện Gate Keeper Employee và ném ra lỗi.

---

## PHẦN 10 — CÁC CHỨC NĂNG TRÌ HOÃN (OUT OF MVP - Phase 2)
*Mục đích: Xác định rõ giới hạn MVP của dự án.*

### [POSTPONED] Các tính năng nằm ngoài phạm vi MVP (Trì hoãn)
* ├── **Feature**: Chấm công hành chính (Attendance).
  * **Mô tả chi tiết**: Trì hoãn việc tích hợp bảng công, tính ca làm việc phức tạp của Odoo HR từ dữ liệu sự kiện quẹt thẻ.
* └── **Feature**: Quản lý khách vãng lai (Visitor Management).
  * **Mô tả chi tiết**: Trì hoãn quy trình cấp thẻ tạm thời, đăng ký trước thông tin khách và theo dõi hành trình khách.

