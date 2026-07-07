# -*- coding: utf-8 -*-
# Mục đích: Theo dõi trạng thái hiện diện thực tế (trong/ngoài) của nhân viên theo từng khu vực.
#          Phục vụ engine anti-passback và cài theo dõi overtime.

from odoo import fields, models


class GateKeeperPresenceState(models.Model):
    _name = "t4.gate_keeper.presence_state"
    _description = "Gate Keeper Presence State"
    _order = "last_seen_at desc"

    employee_id = fields.Many2one(
        comodel_name="t4.gate_keeper.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
    )

    branch_id = fields.Many2one(
        comodel_name="t4.gate_keeper.branch",
        string="Branch",
        related="employee_id.branch_id",
        store=True,
        readonly=True,
    )

    area_id = fields.Many2one(
        comodel_name="t4.gate_keeper.area",
        string="Current Area",
    )

    state = fields.Selection(
        selection=[
            ("inside", "Inside"),
            ("outside", "Outside"),
        ],
        string="State",
        default="outside",
        required=True,
    )

    last_seen_at = fields.Datetime(
        string="Last Seen At", default=fields.Datetime.now, required=True
    )
    notes = fields.Text(string="Notes")

    def mark_inside(self, area_id=False, notes=False):
        """Cập nhật trạng thái hiện diện sang 'inside', lưu khu vực hiện tại,
        và đồng bộ ngược lại cache presence_state/current_area_id trên gk_employee."""
        self.ensure_one()
        target_area_id = area_id or self.area_id.id
        self.write(
            {
                "state": "inside",
                "area_id": target_area_id,
                "last_seen_at": fields.Datetime.now(),
                "notes": notes or self.notes,
            }
        )
        self.employee_id.write(
            {
                "presence_state": "inside",
                "current_area_id": target_area_id,
            }
        )
        return self

    def mark_outside(self, area_id=False, notes=False):
        """Cập nhật trạng thái hiện diện sang 'outside', xóa khu vực hiện tại nếu cần,
        và đồng bộ ngược lại cache presence_state/current_area_id trên gk_employee."""
        self.ensure_one()
        self.write(
            {
                "state": "outside",
                "area_id": area_id or False,
                "last_seen_at": fields.Datetime.now(),
                "notes": notes or self.notes,
            }
        )
        self.employee_id.write(
            {
                "presence_state": "outside",
                "current_area_id": False,
            }
        )
        return self

    def evaluate_passback(self, access_log):
        """TODO: Kiểm tra lần ra/vào trước của nhân viên và phát hiện vi phạm anti-passback."""
        self.ensure_one()
        return False

    def _get_previous_access(self, access_log):
        """TODO: Lấy sự kiện ra/vào gần nhất của nhân viên để kiểm tra tuần tự hợp lệ."""
        return self.env["t4.gate_keeper.access_log"].search([], limit=1)
