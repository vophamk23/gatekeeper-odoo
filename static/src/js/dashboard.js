/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component, onWillStart, onWillDestroy, useState } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

export class T4GatekeeperDashboard extends Component {
    setup() {
        this.state = useState({
            stats: {
                inside: 0,
                outside: 0,
                unknown: 0,
                events_today: 0,
                alerts_active: 0,
                device_active: 0,
                device_total: 0,
            },
            devices: [],
            alerts: [],
            events: [],
            peopleInside: [],
            branches: [],
            groups: [],
            showInsideModal: false,
            selectedLocationId: 'all',
            selectedBranchId: 'all',
            selectedGroupId: 'all',
            loading: true,
            resolveNotes: {},
            currentTime: this._formatTime(new Date()),
            currentDate: this._formatDate(new Date()),
            searchQuery: "",
            prevAlertCount: 0,
            soundEnabled: true,
        });

        onWillStart(async () => {
            await this.loadData();
            this.startTimer();
            this.startClock();
        });

        onWillDestroy(() => {
            this.stopTimer();
            this.stopClock();
        });
    }

    _toLocalTime(utcString) {
        if (!utcString) return "";
        const isoString = utcString.replace(" ", "T") + "Z";
        const date = new Date(isoString);
        if (isNaN(date.getTime())) return utcString;
        const pad = (n) => n.toString().padStart(2, '0');
        return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
    }

    _formatTime(d) {
        return d.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false });
    }

    _formatDate(d) {
        const days = ["Chủ Nhật", "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"];
        return `${days[d.getDay()]}, ${d.getDate().toString().padStart(2,"0")}/${(d.getMonth()+1).toString().padStart(2,"0")}/${d.getFullYear()}`;
    }

    startClock() {
        this.clockTimer = setInterval(() => {
            const now = new Date();
            this.state.currentTime = this._formatTime(now);
            this.state.currentDate = this._formatDate(now);
        }, 1000);
    }

    stopClock() {
        if (this.clockTimer) clearInterval(this.clockTimer);
    }

    async loadData() {
        try {
            const data = await rpc("/t4_gate_keeper/dashboard/data", {});
            if (data) {
                const prevCount = this.state.prevAlertCount;
                const newCount = (data.stats || {}).alerts_active || 0;

                this.state.stats    = data.stats   || this.state.stats;
                this.state.devices  = data.devices  || [];
                this.state.alerts   = (data.alerts || []).map(alert => ({
                    ...alert,
                    alert_time: this._toLocalTime(alert.alert_time)
                }));
                this.state.events   = (data.events || []).map(ev => ({
                    ...ev,
                    time: this._toLocalTime(ev.time)
                }));
                this.state.peopleInside = data.people_inside || [];
                this.state.branches = data.branches || [];
                this.state.groups = data.groups || [];

                // Phát âm thanh nếu cảnh báo mới xuất hiện
                if (!this.state.loading && newCount > prevCount) {
                    this._playAlertSound();
                }
                this.state.prevAlertCount = newCount;
            }
            this.state.loading = false;
        } catch (e) {
            console.error("Lỗi tải dữ liệu dashboard:", e);
        }
    }

    _initAudioContext() {
        if (!this.audioCtx) {
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
    }

    onDashboardClick() {
        this._initAudioContext();
        if (this.audioCtx && this.audioCtx.state === 'suspended') {
            this.audioCtx.resume().catch(e => console.warn("Failed to resume AudioContext: ", e));
        }
    }

    showBreakdownModal() {
        this.state.selectedLocationId = 'all'; // Reset to 'all' on open
        this.state.selectedBranchId = 'all';
        this.state.selectedGroupId = 'all';
        this.state.showInsideModal = true;
    }

    closeBreakdownModal() {
        this.state.showInsideModal = false;
    }

    selectLocation(locId) {
        this.state.selectedLocationId = locId;
    }

    onBranchChange(ev) {
        const val = ev.target.value;
        this.state.selectedBranchId = val === 'all' ? 'all' : parseInt(val);
        this.state.selectedGroupId = 'all'; // Reset group when branch changes
    }

    onGroupChange(ev) {
        const val = ev.target.value;
        this.state.selectedGroupId = val === 'all' ? 'all' : parseInt(val);
    }

    get availableGroups() {
        const branchId = this.state.selectedBranchId;
        if (!branchId || branchId === 'all') return this.state.groups;
        return this.state.groups.filter(g => !g.branch_id || g.branch_id === branchId);
    }

    get filteredPeopleInside() {
        let people = this.state.peopleInside;
        
        // 1. Lọc theo Khu vực
        const locId = this.state.selectedLocationId;
        if (locId && locId !== 'all') {
            people = people.filter(p => p.location_id === locId);
        }
        
        // 2. Lọc theo Chi nhánh
        const branchId = this.state.selectedBranchId;
        if (branchId && branchId !== 'all') {
            people = people.filter(p => p.branch_id === branchId);
        }
        
        // 3. Lọc theo Nhóm đối tượng
        const groupId = this.state.selectedGroupId;
        if (groupId && groupId !== 'all') {
            people = people.filter(p => p.group_ids && p.group_ids.includes(groupId));
        }
        
        return people;
    }

    toggleSound() {
        this.state.soundEnabled = !this.state.soundEnabled;
        if (this.state.soundEnabled) {
            this._initAudioContext();
            if (this.audioCtx && this.audioCtx.state === 'suspended') {
                this.audioCtx.resume().then(() => this.testSound()).catch(e => console.warn(e));
            } else {
                this.testSound();
            }
        }
    }

    testSound() {
        this._playAlertSound(true);
    }

    _playAlertSound(force = false) {
        if (!this.state.soundEnabled && !force) return;
        try {
            this._initAudioContext();
            if (!this.audioCtx) return;

            const play = () => {
                const oscillator = this.audioCtx.createOscillator();
                const gainNode = this.audioCtx.createGain();
                oscillator.connect(gainNode);
                gainNode.connect(this.audioCtx.destination);
                oscillator.type = "sine";
                oscillator.frequency.setValueAtTime(880, this.audioCtx.currentTime);
                oscillator.frequency.setValueAtTime(660, this.audioCtx.currentTime + 0.15);
                gainNode.gain.setValueAtTime(0.2, this.audioCtx.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.4);
                oscillator.start(this.audioCtx.currentTime);
                oscillator.stop(this.audioCtx.currentTime + 0.4);
            };

            if (this.audioCtx.state === 'suspended') {
                this.audioCtx.resume().then(() => {
                    play();
                }).catch(e => {
                    console.warn("Could not resume AudioContext on auto-play trigger: ", e);
                });
            } else {
                play();
            }
        } catch (e) {
            console.warn("Browser blocked sound activation: ", e);
        }
    }

    startTimer() {
        this.timer = setInterval(async () => { await this.loadData(); }, 15000);
    }

    stopTimer() {
        if (this.timer) clearInterval(this.timer);
    }

    handleNoteChange(ev, alertId) {
        this.state.resolveNotes[alertId] = ev.target.value;
    }

    handleSearch(ev) {
        this.state.searchQuery = ev.target.value.toLowerCase();
    }

    get filteredEvents() {
        const q = this.state.searchQuery;
        if (!q) return this.state.events;
        return this.state.events.filter(ev =>
            (ev.person || "").toLowerCase().includes(q) ||
            (ev.gate   || "").toLowerCase().includes(q) ||
            (ev.location || "").toLowerCase().includes(q)
        );
    }

    get priorityLabel() {
        return { critical: "🚨 KHẨN CẤP", high: "⚠️ CAO", medium: "🔵 TRUNG BÌNH", low: "🟢 THẤP" };
    }

    get directionLabel() {
        return { in: "VÀO", out: "RA", unknown: "K.XĐ" };
    }

    async resolveAlert(alertId) {
        const note = this.state.resolveNotes[alertId] || "Bảo vệ trực ban đã xác nhận và xử lý.";
        try {
            const result = await rpc("/t4_gate_keeper/dashboard/resolve_alert", { alert_id: alertId, note });
            if (result && result.status === "success") {
                delete this.state.resolveNotes[alertId];
                await this.loadData();
            }
        } catch (e) {
            console.error("Lỗi xác nhận cảnh báo:", e);
        }
    }
}

T4GatekeeperDashboard.template = "t4_gate_keeper.DashboardTemplate";
registry.category("actions").add("t4_gatekeeper_dashboard_tag", T4GatekeeperDashboard);
