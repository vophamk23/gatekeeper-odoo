# -*- coding: utf-8 -*-
# Mục đích: Định nghĩa các chính sách cảnh báo bảo mật (giờ cấm, khu vực trái phép, anti-passback, v.v.)
#          để vận hành engine tự động phát hiện vi phạm.

from odoo import fields, models

try:
    import pytz
except ImportError:
    pytz = None


class GateKeeperAlertPolicy(models.Model):
    _name = "t4.gate_keeper.alert_policy"
    _description = "Gate Keeper Alert Policy"
    _order = "name"

    name = fields.Char(string="Policy Name", required=True)
    code = fields.Char(string="Code", required=True)
    active = fields.Boolean(string="Active", default=True)
    description = fields.Text(string="Description")

    # Phạm vi chi nhánh áp dụng (trống = tất cả chi nhánh)
    branch_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.branch",
        string="Applicable Branches",
        help="Chi nhánh áp dụng (trống = áp dụng tất cả).",
    )

    area_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.area",
        string="Applicable Areas",
        help="Khu vực áp dụng. Trống = tất cả. Với unauthorized_area: đây là danh sách khu vực cấm.",
    )

    # Chỉ dùng cho condition_type='unauthorized_area': nhóm ĐƯỢC PHÉP vào area_ids
    allowed_group_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.employee_group",
        relation="t4_gk_alert_policy_allowed_group_rel",
        column1="policy_id",
        column2="group_id",
        string="Allowed Groups",
        help="Nhóm được phép vào khu vực cấm. Chỉ dùng cho condition_type='unauthorized_area'.",
    )

    # Phạm vi nhóm nhân viên được giám sát (trống = tất cả)
    employee_group_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.employee_group",
        relation="t4_gk_alert_policy_group_rel",
        column1="policy_id",
        column2="group_id",
        string="Employee Groups",
        help="Nhóm nhân viên được giám sát bởi chính sách này. Trống = tất cả.",
    )

    warning_type_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area_warning_type",
        string="Warning Type",
        required=True,
        ondelete="restrict",
    )

    condition_type = fields.Selection(
        related="warning_type_id.condition_type",
        string="Condition Type",
        readonly=True,
    )

    priority = fields.Selection(
        selection=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Mức độ ưu tiên",
        default="low",
        help="Mức độ cảnh báo khởi tạo. Có thể được leo thang theo thời gian nếu không xử lý.",
    )

    # Khung giờ cấm (dùng cho condition_type='unauthorized_time')
    start_hour = fields.Float(
        string="Start Hour",
        default=17.0,
        help="Giờ bắt đầu cấm (24h float, ví dụ 17.0 = 17:00). Hỗ trợ khung qua đêm.",
    )
    end_hour = fields.Float(
        string="End Hour",
        default=8.0,
        help="Giờ kết thúc cấm (24h float). Nếu end < start thì là khung qua đêm (VD: 17→7).",
    )
    apply_weekend = fields.Boolean(
        string="Apply on Weekend",
        default=True,
        help="Nếu bật, quẹt thẻ vào cuối tuần cũng bị coi là vi phạm.",
    )

    # Được gọi bởi: _evaluate_policy_rules() tại L249 trong file models/gk_access_log.py
    def _get_matching_policies(self, access_log):
        """Tìm các policy đang bật khớp với branch/area/nhóm của access_log.

        - unauthorized_area và unknown_card: bỏ qua lọc area/group ở đây,
          để _evaluate() xử lý (vì area_ids/allowed_group_ids mang nghĩa điều kiện vi phạm).
        - Các loại khác: lọc theo branch, area, employee_group.
        """
        policies = self.search([("active", "=", True)])
        result = self.env[self._name]
        for policy in policies:
            condition = policy.warning_type_id.condition_type

            # Kiểm tra chi nhánh: nếu policy chỉ áp dụng một số chi nhánh cụ thể
            if (
                policy.branch_ids
                and access_log.branch_id
                and access_log.branch_id not in policy.branch_ids
            ):
                continue

            if condition not in ("unauthorized_area", "unknown_card"):
                if (
                    policy.area_ids
                    and access_log.area_id
                    and access_log.area_id not in policy.area_ids
                ):
                    continue
                if policy.employee_group_ids and access_log.employee_id:
                    emp_groups = access_log.employee_id.group_ids
                    if not (emp_groups & policy.employee_group_ids):
                        continue

            result |= policy
        return result

    # Được gọi bởi: _evaluate_policy_rules() tại L251 trong file models/gk_access_log.py
    def _evaluate(self, access_log):
        """Đánh giá chính sách này với một bản ghi access_log.

        Trả về: (triggered: bool, reason: str)

        Các loại condition_type được hỗ trợ:
          - unknown_card       : thẻ không tìm thấy hồ sơ
          - unauthorized_time  : quẹt trong khung giờ cấm
          - invalid_sequence   : vi phạm anti-passback
          - unauthorized_area  : nhóm không được phép vào khu vực
          - overtime           : do cron xử lý, không qua đây
          - device_offline     : do gk_device.write() xử lý trực tiếp
        """
        self.ensure_one()
        condition = self.warning_type_id.condition_type
        emp = access_log.employee_id

        # A: Thẻ lạ — employee_id rỗng chính là điều kiện kích hoạt
        if condition == "unknown_card" and not emp:
            return (
                True,
                "Phát hiện THẺ LẠ tại thiết bị %s"
                % (access_log.device_id.name or "?"),
            )

        # B: Ngoài giờ quy định — kiểm tra khung giờ cấm theo timezone của branch
        # ---> Gọi hàm: _check_unauthorized_time() tại L169 trong file này (gk_alert_policy.py)
        if condition == "unauthorized_time" and emp:
            return self._check_unauthorized_time(access_log)

        # D: Anti-passback — kiểm tra trình tự ra/vào
        # ---> Gọi hàm: _check_invalid_sequence() tại L230 trong file này (gk_alert_policy.py)
        if condition == "invalid_sequence" and emp:
            return self._check_invalid_sequence(access_log)

        # C: Khu vực cấm — kiểm tra nhóm được phép
        # ---> Gọi hàm: _check_unauthorized_area() tại L263 trong file này (gk_alert_policy.py)
        if condition == "unauthorized_area" and emp:
            return self._check_unauthorized_area(access_log)

        return (False, "")

    def _check_unauthorized_time(self, access_log):
        """Kiểm tra thời điểm quẹt thẻ có nằm trong khung giờ cấm không.

        Hỗ trợ khung giờ qua đêm (ví dụ: 17:00 → 07:00 sáng hôm sau).
        Timezone lấy từ branch của log, fallback về Asia/Ho_Chi_Minh.
        """
        self.ensure_one()
        if not pytz:
            return (False, "")

        access_time_utc = access_log.access_time
        if not access_time_utc:
            return (False, "")

        # Lấy timezone của branch, fallback về Asia/Ho_Chi_Minh
        tz_name = (
            access_log.branch_id.timezone
            if access_log.branch_id and access_log.branch_id.timezone
            else "Asia/Ho_Chi_Minh"
        )
        try:
            tz = pytz.timezone(tz_name)
        except Exception:
            tz = pytz.timezone("Asia/Ho_Chi_Minh")

        # Quy đổi access_time (UTC) sang giờ địa phương
        local_dt = pytz.utc.localize(access_time_utc.replace(tzinfo=None)).astimezone(tz)
        event_hour = local_dt.hour + local_dt.minute / 60.0

        # Kiểm tra cuối tuần (thứ 7 = weekday 5, chủ nhật = 6)
        if self.apply_weekend and local_dt.weekday() >= 5:
            reason = (
                "%s quẹt thẻ vào %s (cuối tuần) — vi phạm chính sách \"%s\""
                % (
                    access_log.employee_id.name,
                    local_dt.strftime("%H:%M %d/%m/%Y"),
                    self.name,
                )
            )
            return (True, reason)

        # Kiểm tra khung giờ cấm (hỗ trợ qua đêm)
        start = self.start_hour
        end = self.end_hour
        if start < end:
            # Khung trong ngày: ví dụ 12:00 → 13:00
            in_curfew = start <= event_hour <= end
        else:
            # Khung qua đêm: ví dụ 17:00 → 07:00
            in_curfew = event_hour >= start or event_hour <= end

        if in_curfew:
            reason = (
                "%s quẹt thẻ lúc %s — nằm trong khung giờ cấm của chính sách \"%s\""
                % (
                    access_log.employee_id.name,
                    local_dt.strftime("%H:%M"),
                    self.name,
                )
            )
            return (True, reason)

        return (False, "")

    def _check_invalid_sequence(self, access_log):
        """Kiểm tra vi phạm anti-passback dựa trên presence_state của nhân viên.

        Vi phạm khi:
        - Quẹt RA (direction=out) nhưng nhân viên đang ở NGOÀI hoặc UNKNOWN.
        - Quẹt VÀO (direction=in) khi đã ở TRONG một khu vực KHÁC mà chưa ra.
        """
        self.ensure_one()
        emp = access_log.employee_id
        direction = access_log.direction

        if direction == "out" and emp.presence_state in ("outside", "unknown"):
            reason = (
                "%s quẹt RA nhưng trạng thái đang là \"%s\" — vi phạm anti-passback"
                % (emp.name, emp.presence_state)
            )
            return (True, reason)

        if direction == "in" and emp.presence_state == "inside":
            # Nếu đang ở trong CÙNG khu vực thì không tính anti-passback
            if not emp.current_area_id or emp.current_area_id != access_log.area_id:
                reason = (
                    "%s đang ở \"%s\" nhưng quẹt vào \"%s\" mà chưa quẹt ra — vi phạm anti-passback"
                    % (
                        emp.name,
                        emp.current_area_id.name or "?",
                        access_log.area_id.name if access_log.area_id else "?",
                    )
                )
                return (True, reason)

        return (False, "")

    def _check_unauthorized_area(self, access_log):
        """Kiểm tra nhân viên có quyền vào khu vực hay không.

        area_ids       = danh sách khu vực bị giám sát (khu vực cấm).
        allowed_group_ids = nhóm ĐƯỢC PHÉP vào (trống = không ai được phép).

        Vi phạm khi: khu vực log nằm trong area_ids VÀ nhóm của nhân viên không giao với allowed_group_ids.
        """
        self.ensure_one()
        emp = access_log.employee_id

        # Chỉ kiểm tra khi khu vực log thuộc danh sách khu vực bị giám sát
        if not self.area_ids or not access_log.area_id:
            return (False, "")

        if access_log.area_id not in self.area_ids:
            return (False, "")

        # Không có nhóm được phép → không ai được vào
        if not self.allowed_group_ids:
            reason = (
                "%s vào khu vực cấm \"%s\" — chính sách \"%s\" không cho phép nhóm nào"
                % (emp.name, access_log.area_id.name, self.name)
            )
            return (True, reason)

        # Kiểm tra nhóm nhân viên có giao với allowed_group_ids không
        emp_groups = emp.group_ids
        if not (emp_groups & self.allowed_group_ids):
            reason = (
                "%s vào khu vực cấm \"%s\" — nhóm của nhân viên không được phép theo chính sách \"%s\""
                % (emp.name, access_log.area_id.name, self.name)
            )
            return (True, reason)

        return (False, "")
