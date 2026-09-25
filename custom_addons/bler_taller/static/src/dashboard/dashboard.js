/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatMonetary } from "@web/views/fields/formatters";

/**
 * Tablero del taller (inspirado en RepairOS): órdenes por estado, cartera,
 * agenda del día, carga por mecánico y próximos mantenimientos.
 * Cada tarjeta abre la lista filtrada.
 */
export class TallerDashboard extends Component {
    static template = "bler_taller.Dashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ data: null });
        onWillStart(() => this.load());
    }

    async load() {
        this.state.data = await this.orm.call("repair.order", "get_taller_dashboard_data", []);
    }

    formatAmount(value) {
        return formatMonetary(value, { currencyId: this.state.data.billing.currency_id });
    }

    openRecords(resModel, name, domain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: resModel,
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    openRecord(resModel, resId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: resModel,
            views: [[false, "form"]],
            res_id: resId,
        });
    }

    openWorkload(row) {
        this.openRecords("repair.order", row.user, [
            ["state", "in", ["confirmed", "under_repair"]],
            ["user_id", "=", row.user_id || false],
        ]);
    }

    newRepair() {
        this.action.doAction("repair.action_repair_order_form");
    }

    openCalendar() {
        this.action.doAction("bler_taller.action_repair_order_calendar");
    }
}

registry.category("actions").add("bler_taller.dashboard", TallerDashboard);
