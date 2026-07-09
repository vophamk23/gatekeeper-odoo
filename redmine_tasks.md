GATEKEEPER — CẤU TRÚC ISSUE TRÊN REDMINE

==========================================

Đọc từ trên xuống theo thứ tự — làm xong phần trước mới chuyển sang phần sau.

Mỗi \[PHẦN] là một Epic, mỗi \[NHÓM] là parent issue, mỗi Feature là subtask.

═══════════════════════════════════════════════════════

PHẦN 0 — SETUP DỰ ÁN

Làm đầu tiên, cả team phải hoàn thành phần này trước khi viết bất kỳ dòng code nào.

═══════════════════════════════════════════════════════

\[SETUP] Khởi tạo và cấu hình dự án Gatekeeper

\[SETUP] Thiết lập môi trường phát triển

│

├── Feature: Cài đặt Odoo 18 trên Docker local, chạy được trên máy từng thành viên

├── Feature: Cấu hình PostgreSQL và kiểm tra kết nối database thành công

├── Feature: Tạo repository GitHub, tạo 3 nhánh chính (main, develop, feature/\*)

├── Feature: Viết file README hướng dẫn từng bước cài môi trường cho thành viên mới

├── Feature: Cấu hình .gitignore loại bỏ file thừa của Odoo khỏi git

└── Feature: Kết nối máy chấm công thực tế với môi trường dev để test tích hợp

\[SETUP] Khởi tạo cấu trúc thư mục dự án Odoo

│

├── Feature: Tạo thư mục gốc chứa t4_coreapi + 8 module Gatekeeper đúng chuẩn cây thư mục Odoo

├── Feature: Tạo file \_\_manifest\_\_.py cho từng module với tên, version, dependency đầy đủ

├── Feature:Khai báo thứ tự phụ thuộc giữa các module trong \_\_manifest\_\_.py

└── Feature: Khởi động Odoo, cài tất cả 8 module, không có lỗi nào xuất hiện

\[SETUP] Cấu hình Redmine quản lý dự án

│

├── Feature: Tạo project Gatekeeper trên Redmine

├── Feature: Cấu hình trạng thái issue theo quy trình (New → In Progress → Review → Done / Bug)

├── Feature: Tạo toàn bộ issue tree theo tài liệu này lên Redmine

├── Feature: Phân công người phụ trách và deadline cho từng issue Sprint 1

└── Feature: Liên kết Redmine với GitHub để commit tự động cập nhật issue

\[SETUP] Thống nhất quy trình làm việc nhóm

│

├── Feature: Thống nhất cách đặt tên nhánh git (ví dụ: feature/gatekeeper-location-model)

├── Feature: Thống nhất cách viết commit message (ví dụ: \[LOC] Add Location model)

├── Feature: Thiết lập quy trình review code - mọi code phải được review trước khi merge vào develop

└── Feature: Họp kickoff toàn team, phân công nhiệm vụ và chốt Sprint plan

═══════════════════════════════════════════════════════

PHẦN 1 — TÀI LIỆU ĐẶC TẢ HỆ THỐNG

Làm song song với Sprint 1. BA chịu trách nhiệm chính, dev đọc và góp ý.

═══════════════════════════════════════════════════════

\[DOC] Tài liệu đặc tả hệ thống Gatekeeper

\[DOC] Tài liệu SRS - Đặc tả yêu cầu phần mềm

│

├── Feature: Viết Phần 1 - Giới thiệu dự án (mục đích, phạm vi, stakeholder, định nghĩa thuật ngữ)

├── Feature: Viết Phần 2 - Tổng quan hệ thống (kiến trúc 3 lớp, danh sách module, phân kỳ Phase 1/2)

├── Feature: Viết Phần 3 - Yêu cầu người dùng (Actor, User Stories, Acceptance Criteria)

├── Feature: Viết Phần 4 - Yêu cầu chức năng và phi chức năng

├── Feature: Viết Phần 5 - Đặc tả 13 Use Case chi tiết (luồng chính, ngoại lệ, tiền/hậu điều kiện)

└── Feature: Review và cập nhật SRS sau Sprint 1 dựa trên phản hồi thực tế từ team

\[DOC] Tài liệu ERD - Sơ đồ quan hệ dữ liệu

│

├── Feature: Vẽ ERD tổng thể toàn bộ 8 module trên draw.io hoặc dbdiagram.io

├── Feature: Mô tả chi tiết từng bảng, từng cột và kiểu dữ liệu tương ứng

├── Feature: Xác định rõ quan hệ khóa ngoại và các ràng buộc dữ liệu (unique, required)

└── Feature: Mapping từng bảng ERD sang tên model Odoo tương ứng để dev tham chiếu

\[DOC] Tài liệu SDD - Thiết kế hệ thống

│

├── Feature: Mô tả kiến trúc 3 lớp (Thiết bị → Integration → Odoo Core → Giao diện)

├── Feature: Mô tả luồng dữ liệu từ lúc thiết bị gửi tín hiệu đến lúc hiển thị trên dashboard

└── Feature: Mô tả cơ chế phân quyền RBAC - ai được làm gì trong hệ thống

\[DOC] Tài liệu hướng dẫn sử dụng

│

├── Feature: Viết hướng dẫn cho Admin - cách cấu hình địa điểm, thiết bị, policy

├── Feature: Viết hướng dẫn cho Bảo vệ trực ban - cách dùng dashboard và xử lý cảnh báo

├── Feature: Viết hướng dẫn cho Kỹ thuật viên - cách theo dõi và cập nhật thiết bị

└── Feature: Viết hướng dẫn cho Giám đốc - cách xem báo cáo và thống kê

\[DOC] Tài liệu test case

│

├── Feature: Viết bảng test case cho từng Use Case theo đúng Acceptance Criteria trong SRS

├── Feature: Phân loại test case theo mức độ (smoke test, functional test, edge case)

└── Feature: Tạo Postman collection để dev tự test API endpoint của integration layer

═══════════════════════════════════════════════════════════════════

PHẦN NỀN TẢNG — MODULE API GATEWAY: T4 CORE API

Làm song song với Sprint 1. Dev backend phụ trách chính.

Phải hoàn thành trước khi bắt đầu Module 4.

Không cần block Module 1, 2, 3 — các module đó không phụ thuộc.

═══════════════════════════════════════════════════════════════════

\[MODULE 0] API Gateway — t4_coreapi (Pre-built · Setup Only)

Mô tả: Module dùng chung cho toàn hệ thống T4. Đóng vai trò cổng

bảo vệ OAuth2-style — xác thực thiết bị/ứng dụng bên ngoài trước

khi cho phép gọi vào Odoo. Gatekeeper_integration phụ thuộc trực

tiếp vào module này.

──────────────────────────────────────────────────────────────────

\[SETUP] Cài đặt và xác nhận t4_coreapi hoạt động

──────────────────────────────────────────────────────────────────

│

├── Feature: Đưa t4_coreapi vào thư mục addons, cài module lên

│ Odoo, xác nhận không có lỗi khi khởi động

│

├── Feature: Kiểm tra toàn bộ chức năng đã hoạt động đúng

│ (auth endpoint, token issuance, rate limit, IP whitelist)

│ bằng Postman collection — ghi nhận pass/fail từng case

│

├── Feature: Nếu còn chức năng chưa hoàn thiện thì liệt kê và

│ phân công dev hoàn thiện trước Sprint 2

│

└── Feature: Viết tài liệu nội bộ hướng dẫn team Gatekeeper cách

đăng ký Application và Endpoint mới trên t4_coreapi

──────────────────────────────────────────────────────────────────

\[CONFIG] Tạo cấu hình Gatekeeper trên giao diện Odoo

──────────────────────────────────────────────────────────────────

│

├── Feature: Tạo core.api.domain "Gatekeeper" — thiết lập hostname

│ và base URL cho toàn bộ API của hệ thống

│

├── Feature: Tạo core.api.version "v1" trên domain Gatekeeper

│ với path prefix /api/v1

│

├── Feature: Tạo core.api.application "Gatekeeper Device Gateway"

│ — đây là danh tính của máy chấm công khi gọi API

│ Lấy client_id và client_secret sau khi tạo

│

├── Feature: Cấu hình token TTL phù hợp cho thiết bị

│ (access token: 24h, refresh token: 168h)

│

└── Feature: Cấu hình IP whitelist — chỉ cho phép IP của

các máy chấm công thực tế gọi vào

──────────────────────────────────────────────────────────────────

\[TEST] Kiểm thử gateway trước khi bàn giao cho Module 4

──────────────────────────────────────────────────────────────────

│

├── Feature: Test case 1 — Thiết bị gọi auth với client_id/secret

│ hợp lệ → nhận được access_token và refresh_token (200)

│

├── Feature: Test case 2 — Gọi auth với secret sai

│ → nhận HTTP 401 Unauthorized

│

├── Feature: Test case 3 — Gọi API endpoint với token hợp lệ

│ → nhận HTTP 200

│

├── Feature: Test case 4 — Gọi API với token hết hạn

│ → nhận HTTP 401, dùng refresh_token lấy token mới

│

├── Feature: Test case 5 — Gọi từ IP không nằm trong whitelist

│ → nhận HTTP 403 Forbidden

│

└── Feature: Test case 6 — Gọi vượt rate limit (>60 req/phút)

→ nhận HTTP 429 Too Many Requests

═══════════════════════════════════════════════════════

PHẦN 2 — MODULE 1: QUẢN LÝ ĐỊA ĐIỂM VÀ CỔNG

Làm đầu tiên trong các module. Đây là nền tảng - không có địa điểm và cổng thì

các module sau không có gì để gắn vào.

═══════════════════════════════════════════════════════

\[MODULE] Quản lý địa điểm và cổng gatekeeper_location

\[MODEL] Xây dựng model Location (Địa điểm)

│

├── Feature: Tạo bảng lưu thông tin địa điểm (class Location) gồm tên, mã định danh, địa chỉ và trạng thái hoạt động

├── Feature: Đảm bảo mã địa điểm không được trùng nhau trong toàn hệ thống

├── Feature: Chặn xóa địa điểm nếu địa điểm đó còn cổng đang hoạt động bên trong

└── Feature: Nhập dữ liệu mẫu 2-3 địa điểm để test giao diện

\[MODEL] Xây dựng model Gate (Cổng ra vào)

│

├── Feature: Tạo bảng lưu thông tin cổng (class Gate) gồm tên, mã, loại cổng (chỉ vào / chỉ ra / hai chiều) và trạng thái

├── Feature: Liên kết mỗi cổng với một địa điểm cụ thể

├── Feature: Đảm bảo mã cổng không trùng trong cùng một địa điểm

└── Feature: Nhập dữ liệu mẫu 4-5 cổng thuộc các địa điểm khác nhau để test

\[VIEW] Xây dựng giao diện quản lý địa điểm

│

├── Feature: Trang list view danh sách địa điểm hiển thị tên, mã và trạng thái dạng bảng

├── Feature: Trang form view chi tiết địa điểm hiển thị thông tin đầy đủ kèm danh sách cổng bên dưới

└── Feature: Ô tìm kiếm và lọc địa điểm theo tên, mã hoặc trạng thái

\[VIEW] Xây dựng giao diện quản lý cổng

│

├── Feature: Trang list view danh sách cổng lọc theo từng địa điểm

├── Feature: Trang form view chi tiết cổng với dropdown chọn loại cổng

└── Feature: Nút bật/tắt trạng thái cổng ngay trên trang danh sách list view, không cần vào form

\[ACCESS] Phân quyền module địa điểm và cổng

│

├── Feature: Admin được toàn quyền tạo, sửa, vô hiệu hóa địa điểm và cổng

├── Feature: Bảo vệ và kỹ thuật viên chỉ được xem, không được sửa

└── Feature: Kiểm tra đăng nhập từng vai trò, đảm bảo đúng quyền truy cập

═══════════════════════════════════════════════════════

PHẦN 3 — MODULE 2: QUẢN LÝ THIẾT BỊ

Làm sau Module 1. Thiết bị phải được gắn vào cổng nên cổng phải có trước.

═══════════════════════════════════════════════════════

\[MODULE] Quản lý thiết bị gatekeeper_device

\[MODEL] Xây dựng model Device (Thiết bị)

│

├── Feature: Tạo bảng lưu thông tin thiết bị (class Device) gồm tên, mã serial, loại thiết bị, nhà sản xuất và trạng thái

├── Feature: Liên kết mỗi thiết bị với một cổng cụ thể

├── Feature: Định nghĩa 4 trạng thái thiết bị (đang hoạt động, bảo trì, mất kết nối, sự cố)

├── Feature: Lưu thêm trường thời gian (last_seen_at) gửi tín hiệu gần nhất để phục vụ theo dõi sức khỏe

└── Feature: Nhập dữ liệu mẫu 3-4 thiết bị gắn vào các cổng đã tạo ở Module 1

\[LOGIC] Xây dựng logic theo dõi sức khỏe thiết bị

│

├── Feature: Viết tác vụ tự động Scheduled Action (ir.cron) chạy mỗi 5 phút, kiểm tra thiết bị nào chưa gửi tín hiệu quá 15 phút

├── Feature: Tự động chuyển thiết bị đó sang trạng thái mất kết nối và tạo cảnh báo khi vượt ngưỡng

├── Feature: Tự động phục hồi trạng thái khi thiết bị gửi tín hiệu trở lại

└── Feature: Gửi email thông báo đến kỹ thuật viên ngay khi thiết bị bị đánh dấu mất kết nối

\[VIEW] Xây dựng giao diện quản lý thiết bị

│

├── Feature: Trang list view danh sách thiết bị với cột trạng thái hiển thị màu sắc (xanh/đỏ/vàng)

└── Feature: Trang form view chi tiết thiết bị kèm lịch sử thay đổi trạng thái theo thời gian

\[ACCESS] Cấu hình phân quyền module Device

│

├── Feature: Chỉ admin mới được đăng ký thiết bị mới và chuyển sang trạng thái đã duyệt

└── Feature: Kỹ thuật viên chỉ được xem và cập nhật ghi chú bảo trì, không được xóa thiết bị

═══════════════════════════════════════════════════════

PHẦN 4 — MODULE 3: QUẢN LÝ ĐỐI TƯỢNG RA VÀO

Làm song song với Module 2. Không phụ thuộc vào thiết bị nhưng phải có trước

Module 5 vì sự kiện cần biết đây là ai.

═══════════════════════════════════════════════════════

\[MODULE] Quản lý đối tượng ra vào gatekeeper_person

\[MODEL] Xây dựng model Person (Hồ sơ đối tượng)

│

├── Feature: Tạo bảng lưu thông tin người (class Person) gồm họ tên, mã định danh, loại (sinh viên/nhân viên/khách), đơn vị, ảnh

├── Feature: Đảm bảo mã định danh không trùng trong toàn hệ thống

├── Feature: Chặn xóa hồ sơ nếu người đó còn lịch sử sự kiện, chỉ cho phép vô hiệu hóa

└── Feature: Nhập dữ liệu mẫu 10 người thuộc các loại khác nhau để test

\[MODEL] Xây dựng model Person Card (Thẻ nhận dạng)│

├── Feature: Tạo bảng lưu thẻ nhận dạng (class PersonCard) gồm loại thẻ, giá trị mã, ngày hiệu lực, ngày hết hạn và trạng thái

├── Feature: Liên kết mỗi thẻ với một hồ sơ Person cụ thể - một người có thể có nhiều thẻ

├── Feature: Đảm bảo giá trị mã thẻ không trùng trong toàn hệ thống

└── Feature: Tự động chuyển thẻ sang trạng thái hết hạn khi qua ngày hết hạn

\[MODEL] Xây dựng model Person Group (Nhóm đối tượng)│

├── Feature: Tạo bảng nhóm đối tượng (class PersonGroup) với tên nhóm và mô tả, danh sách thành viên

├── Feature: Cho phép một người thuộc nhiều nhóm cùng lúc

└── Feature: Nhập dữ liệu demo các nhóm mẫu (sinh viên, nhân viên, khách)

\[LOGIC] Xây dựng logic trạng thái hiện diện

│

├── Feature: Sau mỗi sự kiện ra vào, tự động cập nhật trạng thái người đó đang trong hay ngoài khuôn viên

└── Feature: Cập nhật trạng thái hiện diện tự động sau mỗi sự kiện mới (vào thì đang trong, ra thì đang ngoài)

\[VIEW] Xây dựng giao diện quản lý đối tượng

│

├── Feature: Trang list view danh sách người với lọc theo loại đối tượng và đơn vị

├── Feature: Trang form view chi tiết hồ sơ kèm tab Thẻ nhận dạng để thêm/khóa thẻ

└── Feature: Trang quản lý nhóm đối tượng - tạo nhóm và thêm/xóa thành viên

═══════════════════════════════════════════════════════

PHẦN 5 — MODULE 4: TIẾP NHẬN DỮ LIỆU TỪ THIẾT BỊ NGOÀI

Depends: t4_coreapi, gatekeeper_location, gatekeeper_device, gatekeeper_person

Mô tả: Module này KHÔNG tự xây dựng lại cơ chế xác thực.

Toàn bộ phần bảo mật (auth, token, rate limit, IP whitelist) đã

được t4_coreapi xử lý. Module 4 chỉ tập trung vào nghiệp vụ:

nhận dữ liệu thô từ thiết bị → chuẩn hoá → chuyển sang Module 5.═══════════════════════════════════════════════════════

\[MODULE] Tiếp nhận dữ liệu từ thiết bị ngoài gatekeeper_integration

Ghi chú : Không tự viết auth — toàn bộ bảo mật do t4_coreapi xử lý.

──────────────────────────────────────────────────────────────────

\[GATEWAY] Đăng ký endpoint trên t4_coreapi

──────────────────────────────────────────────────────────────────

│

├── Feature: Đăng ký endpoint nhận sự kiện quẹt thẻ

│ POST /api/v1/gatekeeper/event

│

├── Feature: Đăng ký endpoint nhận heartbeat thiết bị

│ POST /api/v1/gatekeeper/heartbeat

│

└── Feature: Đăng ký endpoint thiết bị hỏi cấu hình

&#x20; GET /api/v1/gatekeeper/status

──────────────────────────────────────────────────────────────────

\[LOGIC] Xử lý sự kiện quẹt thẻ

──────────────────────────────────────────────────────────────────

│

├── Feature: Viết Server Action nhận và đọc dữ liệu sự kiện

│ Đọc từ context: device_serial, card_code, timestamp

│

├── Feature: Validate dữ liệu đầu vào — báo lỗi nếu thiếu field

│

├── Feature: Tra cứu thiết bị theo mã serial — báo lỗi nếu không tìm thấy hoặc inactive

│

└── Feature: Chuyển dữ liệu sang bộ chuẩn hoá rồi gửi sang Module 5

──────────────────────────────────────────────────────────────────

\[LOGIC] Xử lý heartbeat thiết bị

──────────────────────────────────────────────────────────────────

│

└── Feature: Cập nhật trường last_seen_at trên Device khi nhận heartbeat

──────────────────────────────────────────────────────────────────

\[LOGIC] Chuẩn hoá dữ liệu đa thiết bị

──────────────────────────────────────────────────────────────────

│

├── Feature: Xây dựng DataNormalizer — chuyển payload thô về định dạng chuẩn

│ Output: device_id, card_code, timestamp (UTC), direction

│

├── Feature: Cấu hình adapter cho từng hãng thiết bị (ZKTeco, Hikvision, Dahua...)

│

└── Feature: Ghi log payload không nhận dạng được để bổ sung adapter sau

──────────────────────────────────────────────────────────────────

\[LOGIC] Chống trùng lặp và xử lý sự kiện offline

──────────────────────────────────────────────────────────────────

│

├── Feature: Tạo bảng staging lưu tạm dữ liệu thô trước khi xử lý

│ Model: gatekeeper.raw.event

│

├── Feature: Phát hiện sự kiện trùng — bỏ qua, không tạo bản ghi mới

│ Khoá trùng: device_serial + card_code + timestamp

│

├── Feature: Hỗ trợ gửi batch offline — nhiều sự kiện trong 1 request

│ POST /api/v1/gatekeeper/event với body là mảng events

│

└── Feature: Sắp xếp batch offline theo thời gian tăng dần trước khi xử lý

──────────────────────────────────────────────────────────────────

\[VIEW] Giao diện giám sát (dành cho kỹ thuật viên)

──────────────────────────────────────────────────────────────────

│

├── Feature: Trang list view dữ liệu thô — phân biệt đã xử lý / lỗi / đang chờ

│

└── Feature: Trang thống kê — số sự kiện theo ngày, tỷ lệ lỗi, top thiết bị

──────────────────────────────────────────────────────────────────

\[ACCESS] Phân quyền

──────────────────────────────────────────────────────────────────

│

├── Feature: Admin — toàn quyền cấu hình endpoint và thông tin kết nối thiết bị

│

└── Feature: Kỹ thuật viên — chỉ xem raw event log để hỗ trợ debug

═══════════════════════════════════════════════════════

PHẦN 6 — MODULE 5: GHI NHẬN SỰ KIỆN RA VÀO

Đây là trái tim của hệ thống. Làm sau Module 4 vì cần integration layer

đã hoạt động để nhận dữ liệu thực tế từ thiết bị.

═══════════════════════════════════════════════════════

\[MODULE] Ghi nhận sự kiện ra vào gatekeeper_event

&#x20;

\[MODEL] Xây dựng model Event (Sự kiện)

│

├── Feature: Tạo bảng sự kiện (class Event) lưu đầy đủ thông tin - người, thiết bị, cổng, địa điểm, thời gian, chiều vào/ra, trạng thái

├── Feature: Chặn hoàn toàn việc sửa hoặc xóa sự kiện sau khi đã tạo, kể cả admin cũng không được

├── Feature: Thêm trường đánh dấu sự kiện offline để phân biệt với sự kiện real-time

└── Feature: Nhập dữ liệu mẫu 20-30 sự kiện để test giao diện và báo cáo

\[LOGIC] Xây dựng logic xử lý sự kiện đến

│

├── Feature: Tra cứu mã thẻ để xác định đúng người (nếu không tìm thấy thì đánh dấu không xác định)

├── Feature: Xác định chiều vào hay ra dựa trên cấu hình loại cổng đã thiết lập ở Module 1

├── Feature: Cập nhật trạng thái hiện diện của đối tượng ngay sau khi tạo sự kiện

└── Feature: Gọi sang module cảnh báo để kiểm tra có vi phạm quy tắc nào không

\[VIEW] Xây dựng giao diện tra cứu lịch sử sự kiện

│

├── Feature: Trang list view danh sách sự kiện với bộ lọc theo địa điểm, cổng, người, thời gian và chiều

├── Feature: Trang form view chi tiết từng sự kiện hiển thị đầy đủ thông tin

├── Feature: Nút xuất danh sách đã lọc ra file Excel

└── Feature: Nút xuất danh sách đã lọc ra file PDF

═══════════════════════════════════════════════════════

PHẦN 7 — MODULE 6: CẢNH BÁO VÀ QUY TẮC TỰ ĐỘNG

Làm sau Module 5. Cần có sự kiện thực tế để kiểm tra quy tắc có hoạt động đúng không.

═══════════════════════════════════════════════════════

\[MODULE] Cảnh báo và quy tắc tự động gatekeeper_alert

\[MODEL] Xây dựng model Alert Policy (Quy tắc cảnh báo)

│

├── Feature: Tạo bảng quy tắc (class AlertPolicy) lưu tên, loại điều kiện, nhóm đối tượng áp dụng, địa điểm và mức độ ưu tiên

├── Feature: Cài sẵn 4 loại điều kiện (ở trong quá giờ quy định, vào ngoài khung giờ, thiết bị mất kết nối, mã thẻ không tìm thấy)

├── Feature: Quy tắc mới tạo mặc định ở trạng thái tắt, admin phải bật thủ công mới có hiệu lực

└── Feature: Nhập dữ liệu demo các policy mẫu

\[MODEL] Xây dựng model Alert (Cảnh báo)

│

├── Feature: Tạo bảng cảnh báo (class Alert) lưu: quy tắc kích hoạt, người liên quan, thời gian, mức độ và trạng thái xử lý

├── Feature: Lưu lịch sử xử lý (ai xác nhận, lúc mấy giờ và ghi chú gì)

└── Feature: Chặn tự động đóng cảnh báo - bảo vệ phải bấm xác nhận thủ công mới đóng được

\[LOGIC] Engine đánh giá quy tắc sau mỗi sự kiện

│

├── Feature: Sau mỗi sự kiện mới, kiểm tra tất cả quy tắc đang bật xem có điều kiện nào thỏa mãn không

├── Feature: Nếu một sự kiện thỏa nhiều quy tắc thì tạo nhiều cảnh báo riêng biệt

└── Feature: Nếu cảnh báo chưa được xử lý sau ngưỡng thời gian thì tự động leo thang - gửi thêm thông báo lên bảo vệ trưởng

\[LOGIC] Xây dựng logic phân phối thông báo

│

├── Feature: Hiển thị cảnh báo mức cao và khẩn cấp hiển thị ngay trên dashboard bảo vệ kèm âm thanh

├── Feature: Cảnh báo liên quan đến thiết bị gửi email cho kỹ thuật viên

└── Feature: Toàn bộ cảnh báo được ghi vào hộp thông báo Odoo để xem lại sau

\[VIEW] Xây dựng giao diện quản lý cảnh báo

│

├── Feature: Trang list view danh sách cảnh báo phân màu theo mức độ (đỏ khẩn cấp, cam cao, vàng trung bình, xám thấp)

├── Feature: Trang form view chi tiết cảnh báo với ô ghi chú và nút xác nhận đã xử lý

├── Feature: Trang cấu hình quy tắc cảnh báo cho admin (tạo, sửa, bật/tắt từng quy tắc)

└── Feature: Trang list view lịch sử cảnh báo đã đóng để bảo vệ trưởng tra cứu khi cần điều tra

═══════════════════════════════════════════════════════

PHẦN 8 — MODULE 7: MÀN HÌNH TRỰC BAN

Làm sau Module 5 và 6 vì cần có dữ liệu sự kiện và cảnh báo thực tế

để dashboard hiển thị đúng.

═══════════════════════════════════════════════════════

\[MODULE] Màn hình trực ban gatekeeper_dashboard

\[COMPONENT] Xây dựng khung dashboard chính

│

├── Feature: Xây dựng khung giao diện dashboard chạy trên Odoo, tối ưu hiển thị màn hình lớn

├── Feature: Cài chế độ tự động làm mới dữ liệu mỗi 30 giây, không cần bảo vệ thao tác

└── Feature: Thiết kế font chữ lớn, màu sắc tương phản rõ ràng phù hợp với chốt bảo vệ

\[COMPONENT] Xây dựng phần tổng quan hiện diện

│

├── Feature: Hiển thị tổng số người đang trong khuôn viên phân theo từng địa điểm

├── Feature: Hiển thị số liệu tổng hợp theo loại đối tượng (sinh viên, nhân viên, khách)

└── Feature: Ô tìm kiếm nhanh tên hoặc mã trong danh sách người đang trong khuôn viên

\[COMPONENT] Xây dựng phần bảng cảnh báo

│

├── Feature: Hiển thị danh sách cảnh báo chưa xử lý hiển thị phân màu theo mức độ, mới nhất lên đầu

├── Feature: Phát âm thanh cảnh báo khi có cảnh báo mức cao hoặc khẩn cấp mới xuất hiện

├── Feature: Nhấn vào cảnh báo xem chi tiết và bấm xác nhận xử lý ngay trên dashboard

└── Feature: Số lượng cảnh báo chưa xử lý hiển thị thường trực góc màn hình

\[COMPONENT] Xây dựng phần trạng thái thiết bị

│

├── Feature: Hiển thị đèn xanh/đỏ cho từng thiết bị (xanh là hoạt động tốt, đỏ là có vấn đề)

└── Feature: Hiển thị banner cảnh báo xuất hiện ngay khi bất kỳ thiết bị nào chuyển sang mất kết nối

═══════════════════════════════════════════════════════

PHẦN 9 — MODULE 8: BÁO CÁO VÀ THỐNG KÊ

Làm cuối cùng. Cần có đủ dữ liệu sự kiện thực tế để báo cáo có ý nghĩa.

═══════════════════════════════════════════════════════

\[MODULE] Báo cáo và thống kê gatekeeper_report

\[REPORT] Xây dựng báo cáo lịch sử sự kiện

│

├── Feature: Giao diện lọc sự kiện theo địa điểm, cổng, người, khoảng thời gian và trạng thái

├── Feature: Xuất kết quả lọc ra file Excel để lưu trữ hoặc gửi báo cáo

└── Feature: Xuất kết quả lọc ra file PDF có tiêu đề và định dạng chuyên nghiệp

\[REPORT] Xây dựng báo cáo thống kê lưu lượng

│

├── Feature: Biểu đồ lưu lượng ra vào theo từng giờ trong ngày

├── Feature: Biểu đồ lưu lượng theo từng ngày trong tuần

├── Feature: Biểu đồ lưu lượng theo từng cổng và địa điểm

└── Feature: Chọn hai khoảng thời gian để so sánh lưu lượng - tuần này với tuần trước chẳng hạn

\[REPORT] Xây dựng báo cáo theo cá nhân và thiết bị

│

├── Feature: Tra cứu toàn bộ lịch sử ra vào của một người cụ thể trong khoảng thời gian chọn

└── Feature: Tra cứu lịch sử sự cố và thay đổi trạng thái của từng thiết bị

\[LOGIC] Xây dựng tính năng gửi báo cáo tự động qua email

│

├── Feature: Giao diện admin cấu hình lịch gửi (ngày/tuần/tháng), danh sách email, định dạng file

├── Feature: Tác vụ tự động tạo báo cáo và gửi email đúng lịch, không cần ai đăng nhập

├── Feature: Nếu gửi email thất bại thì thử lại tối đa 3 lần cách nhau 30 phút

└── Feature: Nếu không có dữ liệu trong kỳ thì vẫn gửi email với nội dung thông báo rõ ràng

═══════════════════════════════════════════════════════

PHẦN 10 — KIỂM THỬ VÀ XỬ LÝ BUG

Chạy xuyên suốt từ Sprint 1 đến khi nghiệm thu.

Tester và BA phụ trách chính, dev hỗ trợ fix.

═══════════════════════════════════════════════════════

\[TEST] Kiểm thử và xử lý bug hệ thống Gatekeeper

\[TEST] Kiểm thử Module 1+2 Location và Device (Địa điểm và Thiết bị)

│

├── Feature: Viết test case tạo địa điểm hợp lệ - kiểm tra lưu thành công

├── Feature: Viết test case tạo địa điểm trùng mã - kiểm tra hệ thống báo lỗi

├── Feature: Viết test case vô hiệu hóa địa điểm - kiểm tra lịch sử không bị xóa

├── Feature: Viết test case đăng ký thiết bị mới - kiểm tra trạng thái chờ duyệt

├── Feature: Viết test case thiết bị mất kết nối 15 phút - kiểm tra cron tự chuyển trạng thái

└── Feature: Viết test case thiết bị phục hồi - kiểm tra trạng thái tự khôi phục

\[TEST] Kiểm thử Module 3+4 Person và Integration (Đối tượng và Thẻ)

│

├── Feature: Viết test case tạo hồ sơ đối tượng hợp lệ - kiểm tra lưu thành công

├── Feature: Viết test case tạo hồ sơ trùng mã - kiểm tra hệ thống báo lỗi

└── Feature: Viết test case gắn thẻ nhận dạng RFID cho người - kiểm tra khi quẹt thẻ hệ thống tra ra đúng người

├── Feature: Viết test case API nhận sự kiện từ thiết bị hợp lệ - kiểm tra HTTP 200

├── Feature: Viết test case gửi sự kiện trùng lặp - kiểm tra chống duplicate

└── Feature: Viết test case gửi batch sự kiện offline - kiểm tra thứ tự thời gian đúng

\[TEST] Kiểm thử Module 5 Event (Sự kiện)

│

├── Feature: Viết test case sự kiện hợp lệ được tạo - kiểm tra đủ thông tin

├── Feature: Viết test case cố sửa sự kiện - kiểm tra hệ thống chặn thành công

├── Feature: Viết test case cố xóa sự kiện - kiểm tra hệ thống chặn thành công

├── Feature: Viết test case trạng thái hiện diện Người vào cổng - kiểm tra trạng thái hiện diện chuyển sang đang trong khuôn viên

└── Feature: Feature: Viết test case trạng thái hiện diện Người ra cổng - kiểm tra trạng thái hiện diện chuyển sang đang ngoài khuôn viên

\[TEST] Kiểm thử Module 6 Alert (Cảnh báo)

│

├── Feature: Viết test case policy Người ở trong khuôn viên quá giờ - kiểm tra cảnh báo được tạo đúng mức độ

├── Feature: Viết test case policy Người vào ngoài khung giờ quy định - kiểm tra cảnh báo phát sinh đúng

├── Feature: Viết test case một sự kiện thỏa nhiều policy - kiểm tra tạo ra nhiều cảnh báo độc lập

├── Feature: Viết test case tắt policy đang bật - kiểm tra hệ thống không tạo cảnh báo mới nữa

└── Feature: Viết test case xác nhận xử lý cảnh báo - kiểm tra lưu đúng tên người xử lý và thời gian

\[TEST] Kiểm thử Module 7 Dashboard

│

├── Feature: Kiểm tra dashboard hiển thị đúng số người đang trong khuôn viên

├── Feature: Kiểm tra dashboard tự động làm mới không bị lỗi sau 1 giờ liên tục

├── Feature: Kiểm tra cảnh báo hiển thị đúng màu theo mức độ ưu tiên

└── Feature: Thiết bị mất kết nối - kiểm tra đèn đỏ xuất hiện đúng thiết bị trên dashboard

\[TEST] Kiểm thử Module 8 Report

│

├── Feature: Lọc sự kiện theo nhiều tiêu chí - kiểm tra kết quả đúng và đủ

├── Feature: Kiểm tra xuất báo cáo Excel đúng dữ liệu đã lọc

├── Feature: Kiểm tra xuất báo cáo PDF đúng định dạng

└── Feature: Kiểm tra email báo cáo tự động gửi đúng lịch và đúng người nhận

\[TEST] Kiểm thử phân quyền RBAC (toàn hệ thống)

│
├── Feature: Admin — xác nhận toàn quyền trên mọi module, riêng Event
│ vẫn không sửa/xóa được dù có quyền cao nhất

├── Feature: Bảo vệ trực ban — chỉ truy cập dashboard và xử lý cảnh báo,
│ bị chặn khi sửa cấu hình hoặc xem báo cáo thống kê qua URL trực tiếp

├── Feature: Bảo vệ trưởng — xem được lịch sử sự kiện/cảnh báo, bị chặn
│ khi thử sửa policy hoặc cấu hình thiết bị

├── Feature: Kỹ thuật viên — chỉ cập nhật được trạng thái/ghi chú thiết bị,
│ bị chặn hoàn toàn khi truy cập dữ liệu Person/Event

├── Feature: Giám đốc — chỉ xem báo cáo thống kê (read-only), bị chặn ở
│ mọi thao tác tạo/sửa/xóa và không truy cập được dashboard vận hành

└── Feature: Kiểm tra đổi vai trò một user có hiệu lực ngay, và user chưa
gán vai trò nào không truy cập được module Gatekeeper nào

\[TEST] Kiểm thử hiệu năng và bảo mật

├── Feature: Kiểm tra 10 thiết bị gửi sự kiện đồng thời - hệ thống không bị nghẽn

├── Feature: Kiểm tra độ trễ từ thiết bị gửi đến dashboard hiển thị không vượt 5 giây

├── Feature: Kiểm tra truy vấn báo cáo 12 tháng dữ liệu trả kết quả dưới 3 giây

├── Feature: Kiểm tra bảo vệ truy cập chức năng admin bằng URL trực tiếp - bị chặn

├── Feature: Kiểm tra kỹ thuật viên không thấy dữ liệu sự kiện ra vào đối tượng

└── Feature: Kiểm tra phiên đăng nhập tự hết hạn sau thời gian không hoạt động

\[TEST] Kiểm thử nghiệm thu với người dùng thực (UAT)

│

├── Feature: Lập kịch bản UAT cho từng vai trò (admin, bảo vệ, kỹ thuật viên, giám đốc)

├── Feature: Mời người dùng thực tế ngồi dùng thử và ghi lại toàn bộ phản hồi

├── Feature: Tổng hợp vấn đề phát sinh, phân loại và giao dev fix

└── Feature: Xác nhận nghiệm thu từng Use Case dựa trên Acceptance Criteria trong SRS

\[BUG] Quản lý và xử lý bug

├── Feature: Thiết lập quy trình báo cáo bug (mẫu mô tả, bước tái hiện, screenshot)

├── Feature: Phân loại bug theo mức độ (Critical, High, Medium, Low)

├── Feature: Ưu tiên xử lý bug Critical và High trước khi chuyển sang Sprint tiếp theo

├── Feature: Viết lại test case cho từng bug đã fix để tránh tái phát

└── Feature: Tổng hợp báo cáo bug cuối Sprint - số lượng phát sinh, đã fix, còn tồn đọng

═══════════════════════════════════════════════════════

THỨ TỰ THỰC HIỆN THEO SPRINT

═══════════════════════════════════════════════════════

Sprint 1 → Setup + t4_coreapi (song song) + Tài liệu + Module 1 + Module 2

Sprint 2 → Module 3 + Module 4 + Module 5 + Test Module 1, 2, 3

Sprint 3 → Module 6 + Module 7 + Module 8 + Test Module 4, 5, 6

Sprint 4 → Test Module 7, 8 + Hiệu năng + UAT + Fix bug + Nghiệm thu
