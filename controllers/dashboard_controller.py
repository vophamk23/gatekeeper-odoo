# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from datetime import datetime, time

class T4GatekeeperDashboardController(http.Controller):

    @http.route('/t4_gate_keeper/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        env = request.env
        
        # Lấy mốc thời gian bắt đầu ngày hôm nay (giờ UTC) để thống kê
        today_start = datetime.combine(fields.Date.today(), time.min)
        
        # Thống kê số lượng hiện diện (Inside / Outside / Unknown)
        inside_count = env['t4.gate_keeper.employee'].search_count([('presence_state', '=', 'inside')])
        outside_count = env['t4.gate_keeper.employee'].search_count([('presence_state', '=', 'outside')])
        unknown_count = env['t4.gate_keeper.employee'].search_count([('presence_state', '=', 'unknown')])

        # Phân rã số lượng trong khuôn viên theo từng khu vực/địa điểm
        area_counts = []
        areas = env['t4.gate_keeper.area'].search([])
        for area in areas:
            count = env['t4.gate_keeper.employee'].search_count([
                ('presence_state', '=', 'inside'),
                ('current_area_id', '=', area.id)
            ])
            area_counts.append({
                'id': area.id,
                'name': area.name,
                'count': count
            })
            
        # Tổng số lượt sự kiện ra vào trong ngày hôm nay
        events_today = env['t4.gate_keeper.access_log'].search_count([('access_time', '>=', today_start)])
        
        # Thống kê cảnh báo chưa xử lý
        alerts_active = env['t4.gate_keeper.area_warning'].search_count([('state', '=', 'warning')])
        
        # Thống kê trạng thái thiết bị
        devices = env['t4.gate_keeper.device'].search([])
        device_stats = {
            'online': 0,
            'offline': 0,
            'controller_offline': 0
        }
        device_list = []
        for dev in devices:
            state = dev.status or 'offline'
            if state in device_stats:
                device_stats[state] += 1
            device_list.append({
                'id': dev.id,
                'name': dev.name,
                'serial': dev.serial_number or '',
                'state': state,
                'controller': dev.controller_id.name if dev.controller_id else 'Không có Controller',
                'area': dev.area_id.name if dev.area_id else 'Không có Khu vực',
            })
            
        # Danh sách cảnh báo chưa xử lý (tối đa 15 bản ghi gần nhất)
        active_alerts = []
        alert_records = env['t4.gate_keeper.area_warning'].search([
            ('state', '=', 'warning')
        ], order='create_date desc', limit=15)
        for alert in alert_records:
            active_alerts.append({
                'id': alert.id,
                'policy_name': alert.warning_type_id.name or 'Cảnh báo an ninh',
                'person': alert.employee_id.name if alert.employee_id else 'Thẻ lạ / Không rõ',
                'device': alert.device_id.name if alert.device_id else '',
                'alert_time': fields.Datetime.to_string(alert.create_date),
                'priority': alert.priority or 'low',
                'state': alert.state,
                'note': alert.description or '',
            })
            
        # Danh sách 10 sự kiện quẹt thẻ gần đây nhất
        recent_events = []
        event_records = env['t4.gate_keeper.access_log'].search([], order='access_time desc', limit=10)
        for ev in event_records:
            recent_events.append({
                'id': ev.id,
                'time': fields.Datetime.to_string(ev.access_time),
                'person': ev.employee_id.name if ev.employee_id else (f"Thẻ lạ: {ev.card_code}" if ev.card_code else "Không rõ danh tính"),
                'direction': ev.direction,
                'gate': ev.device_id.name if ev.device_id else '',
                'location': ev.area_id.name if ev.area_id else '',
            })
            
        # Danh sách những người đang ở trong khuôn viên
        people_inside = []
        inside_employees = env['t4.gate_keeper.employee'].search([('presence_state', '=', 'inside')])
        for p in inside_employees:
            group_names = ", ".join(p.group_ids.mapped('name')) if p.group_ids else ""
            people_inside.append({
                'id': p.id,
                'name': p.name,
                'identifier': p.emp_id,
                'department': group_names,
                'branch_id': p.branch_id.id if p.branch_id else False,
                'branch_name': p.branch_id.name if p.branch_id else 'Không rõ Chi nhánh',
                'group_ids': p.group_ids.ids,
                'location_name': p.current_area_id.name if p.current_area_id else 'Chưa xác định',
                'location_id': p.current_area_id.id if p.current_area_id else False,
            })

        # Lấy danh sách Chi nhánh để hiển thị bộ lọc
        branches = env['t4.gate_keeper.branch'].search([])
        branch_list = [{'id': b.id, 'name': b.name} for b in branches]

        # Lấy danh sách Nhóm đối tượng để hiển thị bộ lọc
        groups = env['t4.gate_keeper.employee_group'].search([])
        group_list = [{
            'id': g.id,
            'name': g.name,
            'branch_id': g.branch_id.id if g.branch_id else False
        } for g in groups]

        return {
            'stats': {
                'inside': inside_count,
                'outside': outside_count,
                'unknown': unknown_count,
                'location_counts': area_counts,
                'events_today': events_today,
                'alerts_active': alerts_active,
                'device_active': device_stats['online'],
                'device_total': len(devices),
            },
            'devices': device_list,
            'alerts': active_alerts,
            'events': recent_events,
            'people_inside': people_inside,
            'branches': branch_list,
            'groups': group_list,
        }

    @http.route('/t4_gate_keeper/dashboard/resolve_alert', type='json', auth='user')
    def resolve_alert(self, alert_id, note):
        env = request.env
        alert = env['t4.gate_keeper.area_warning'].browse(alert_id)
        if alert.exists():
            alert.write({
                'resolution_notes': note,
            })
            alert.action_resolve()
            return {'status': 'success'}
        return {'status': 'error', 'message': 'Cảnh báo không tồn tại.'}
