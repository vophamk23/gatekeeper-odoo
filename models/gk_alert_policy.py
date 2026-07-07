# -*- coding: utf-8 -*-
# Mục đích: Định nghĩa các chính sách cảnh báo bảo mật (giờ cấm, khu vực trái phép, anti-passback, v.v.)
#          để vận hành engine tự động phát hiện vi phạm.

from odoo import fields, models

from ..utils.utils import check_outside_working_hours


class GateKeeperAlertPolicy(models.Model):
    _name = "t4.gate_keeper.alert_policy"
    _description = "Gate Keeper Alert Policy"
    _order = "priority, name"

    name = fields.Char(string="Policy Name", required=True)
    code = fields.Char(string="Code", required=True)
    active = fields.Boolean(string="Active", default=True)
    description = fields.Text(string="Description")

    # Branch and area scope
    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        string="Branch",
        help="Branch where this policy applies. Leave empty to apply to all branches.",
    )

    area_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.area",
        string="Applicable Areas",
        help="Areas affected by this policy. Leave empty to apply to all areas.",
    )

    # For 'unauthorized_area' condition_type: groups ALLOWED to enter the area_ids
    allowed_group_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.employee_group",
        relation="t4_gk_alert_policy_allowed_group_rel",
        column1="policy_id",
        column2="group_id",
        string="Allowed Groups",
        help="Groups allowed to access the restricted areas. Only used when condition_type is 'unauthorized_area'.",
    )

    # For general scope filtering: policy applies only to these groups
    employee_group_ids = fields.Many2many(
        comodel_name="t4.gate_keeper.employee_group",
        relation="t4_gk_alert_policy_group_rel",
        column1="policy_id",
        column2="group_id",
        string="Employee Groups",
        help="Groups this policy monitors. Leave empty to monitor all employees.",
    )

    warning_type_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area_warning_type",
        string="Warning Type",
        required=True,
        ondelete="restrict",
    )

    priority = fields.Integer(
        string="Priority",
        default=10,
        help="Lower number means higher priority.",
    )

    # Time restriction fields (used with 'unauthorized_time' condition_type)
    start_hour = fields.Float(
        string="Start Hour",
        default=17.0,
        help="Start of restricted hour window (24h float, e.g. 17.0 = 5PM).",
    )
    end_hour = fields.Float(
        string="End Hour",
        default=8.0,
        help="End of restricted hour window (24h float). Supports overnight windows (e.g. 17 to 7).",
    )
    apply_weekend = fields.Boolean(
        string="Apply on Weekend",
        default=True,
        help="If checked, weekend access is also considered a violation.",
    )

    def _get_matching_policies(self, access_log):
        """Find active policies matching the given access log's branch and scope.

        - For 'unauthorized_area' and 'unknown_card' conditions:
          area/group filters are NOT applied here; they are handled in _evaluate().
        - For all others: filters on branch, area, and employee group are applied.
        """
        policies = self.search([("active", "=", True)])
        result = self.env[self._name]
        for policy in policies:
            condition = policy.warning_type_id.condition_type

            if (
                policy.branch_id
                and access_log.branch_id
                and policy.branch_id != access_log.branch_id
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

    def _evaluate(self, access_log):
        """Evaluate this policy against an access log record.

        Returns: (triggered: bool, reason: str)

        Supported condition_types:
          - unknown_card
          - unauthorized_time
          - invalid_sequence
          - unauthorized_area
          - overtime (handled by cron, not here)
          - device_offline (handled directly by device write(), not here)
        """
        self.ensure_one()
        condition = self.warning_type_id.condition_type
        emp = access_log.employee_id

        # A: Unknown Card - employee_id is empty
        if condition == "unknown_card" and not emp:
            return (
                True,
                "Unknown card detected at device %s"
                % (access_log.device_id.name or "?"),
            )

        # B: Unauthorized Time
        if condition == "unauthorized_time" and emp:
            # TODO: Dùng check_outside_working_hours (đã import ở đầu file) kết hợp với
            # self.start_hour / self.end_hour / self.apply_weekend và timezone của branch
            # để xác định vi phạm giờ cấm theo đúng chính sách này (không phải giờ làm việc chung).
            return (False, "")

        # D: Anti-passback (Invalid Sequence)
        if condition == "invalid_sequence" and emp:
            # TODO: Kiểm tra anti-passback dựa vào presence_state và chiều ra/vào (direction) của nhân viên
            return (False, "")

        # C: Unauthorized Area
        if condition == "unauthorized_area" and emp:
            # TODO: Kiểm tra quyền truy cập khu vực dựa vào area_ids và allowed_group_ids
            return (False, "")

        return (False, "")
