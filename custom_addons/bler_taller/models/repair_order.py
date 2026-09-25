# -*- coding: utf-8 -*-
from datetime import datetime, time, timedelta

import pytz
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RepairOrder(models.Model):
    _inherit = "repair.order"

    currency_id = fields.Many2one(related="company_id.currency_id")
    service_line_ids = fields.One2many(
        "repair.service.line", "repair_id", string="Servicios", copy=True,
    )
    amount_services = fields.Monetary(
        string="Total servicios", compute="_compute_amounts", store=True,
    )
    amount_parts = fields.Monetary(
        string="Total repuestos", compute="_compute_amounts", store=True,
    )
    amount_total = fields.Monetary(
        string="Total estimado", compute="_compute_amounts", store=True,
        help="Suma de servicios y repuestos, sin impuestos. El valor a pagar "
             "es el de la factura.",
    )

    # Datos del vehículo al ingreso y próximo mantenimiento (CarCare: "Odo").
    vehicle_brand_icon = fields.Char(related="vehicle_id.brand_icon_class", string="Marca")
    vehicle_brand_logo = fields.Char(related="vehicle_id.brand_logo_url", string="Logo de la marca")
    odometer = fields.Float(string="Kilometraje de ingreso")
    odometer_unit = fields.Selection(related="vehicle_id.odometer_unit")
    next_service_date = fields.Date(string="Próximo mantenimiento")
    next_service_km = fields.Float(string="Próximo mantenimiento (km)")

    # Agenda: duración según los servicios, para el calendario.
    taller_duration = fields.Float(
        string="Duración (h)", compute="_compute_taller_duration", store=True, readonly=False,
    )
    schedule_date_end = fields.Datetime(
        string="Fin previsto", compute="_compute_schedule_date_end", store=True,
    )

    # Facturación: la factura es un documento aparte que sale de la cotización.
    invoice_status = fields.Selection(
        related="sale_order_id.invoice_status", store=True, string="Estado de facturación",
    )
    invoice_ids = fields.Many2many(
        "account.move", string="Facturas", compute="_compute_invoice_ids",
    )
    invoice_count = fields.Integer(string="N.º de facturas", compute="_compute_invoice_ids")

    @api.depends(
        "service_line_ids.price_subtotal",
        "move_ids.product_uom_qty", "move_ids.repair_line_type", "move_ids.product_id",
        "move_ids.sale_line_id.price_unit", "move_ids.sale_line_id.discount",
        "under_warranty",
    )
    def _compute_amounts(self):
        for repair in self:
            repair.amount_parts = sum(line["subtotal"] for line in repair._get_part_lines())
            repair.amount_services = sum(repair.service_line_ids.mapped("price_subtotal"))
            repair.amount_total = repair.amount_parts + repair.amount_services

    def _get_part_lines(self):
        """Repuestos que se agregan al vehículo, con su precio de venta.

        El precio es el de la cotización si ya existe, o el precio de venta del
        producto. En garantía los repuestos no se cobran.
        """
        self.ensure_one()
        lines = []
        for move in self.move_ids.filtered(lambda m: m.repair_line_type == "add" and m.state != "cancel"):
            if self.under_warranty:
                price, discount = 0.0, 0.0
            elif move.sale_line_id:
                price, discount = move.sale_line_id.price_unit, move.sale_line_id.discount
            else:
                price, discount = move.product_id.lst_price, 0.0
            lines.append({
                "move": move,
                "price_unit": price,
                "discount": discount,
                "subtotal": price * (1 - discount / 100.0) * move.product_uom_qty,
            })
        return lines

    @api.depends("service_line_ids.duration")
    def _compute_taller_duration(self):
        for repair in self:
            repair.taller_duration = sum(repair.service_line_ids.mapped("duration")) or 1.0

    @api.depends("schedule_date", "taller_duration")
    def _compute_schedule_date_end(self):
        for repair in self:
            if repair.schedule_date:
                repair.schedule_date_end = repair.schedule_date + timedelta(hours=repair.taller_duration or 1.0)
            else:
                repair.schedule_date_end = False

    @api.depends("sale_order_id.invoice_ids")
    def _compute_invoice_ids(self):
        for repair in self:
            invoices = repair.sale_order_id.invoice_ids if repair.sale_order_id.has_access("read") else self.env["account.move"]
            repair.invoice_ids = invoices
            repair.invoice_count = len(invoices)

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id_odometer(self):
        if self.vehicle_id and not self.odometer:
            self.odometer = self.vehicle_id.odometer

    def _get_report_base_filename(self):
        self.ensure_one()
        return "OT %s %s" % (self.name, self.vehicle_id.license_plate or "")

    # --- Flujo ------------------------------------------------------------

    def action_create_sale_order(self):
        action = super().action_create_sale_order()
        self.service_line_ids._create_sale_lines()
        return action

    def action_repair_done(self):
        res = super().action_repair_done()
        self._update_vehicle_after_repair()
        return res

    def _update_vehicle_after_repair(self):
        """Registra el kilometraje y el próximo mantenimiento en el vehículo."""
        today = fields.Date.context_today(self)
        for repair in self.filtered("vehicle_id"):
            # sudo: el mecánico no tiene por qué administrar Flota; los datos
            # vienen de la propia orden.
            vehicle = repair.vehicle_id.sudo()
            if repair.odometer and repair.odometer > vehicle.odometer:
                self.env["fleet.vehicle.odometer"].sudo().create({
                    "vehicle_id": vehicle.id,
                    "value": repair.odometer,
                    "date": today,
                })
                # El kilometraje del vehículo se calcula sin dependencias.
                repair.vehicle_id.invalidate_recordset(["odometer"])
            vals = {}
            if repair.next_service_date:
                vals["next_service_date"] = repair.next_service_date
            if repair.next_service_km:
                vals["next_service_km"] = repair.next_service_km
            if vals:
                vehicle.write(vals)

    def action_taller_invoice(self):
        """Genera la factura desde la orden: cotización → pedido → factura."""
        self.ensure_one()
        if self.state == "cancel":
            raise UserError(_("No se puede facturar una orden cancelada."))
        if not self.sale_order_id:
            self.action_create_sale_order()
        order = self.sale_order_id
        if order.state in ("draft", "sent"):
            order.action_confirm()
        invoices = order.invoice_ids.filtered(lambda m: m.state == "draft")
        if order.invoice_status == "to invoice":
            invoices |= order._create_invoices()
        if not invoices:
            raise UserError(_("No hay nada pendiente por facturar en la orden %s.", self.name))
        return self._action_open_invoices(invoices)

    def action_view_invoices(self):
        self.ensure_one()
        return self._action_open_invoices(self.invoice_ids)

    def _action_open_invoices(self, invoices):
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) == 1:
            action.update({
                "views": [(self.env.ref("account.view_move_form").id, "form")],
                "res_id": invoices.id,
            })
        else:
            action["domain"] = [("id", "in", invoices.ids)]
        action["context"] = {"default_move_type": "out_invoice"}
        return action

    # --- Tablero ------------------------------------------------------------

    @api.model
    def _taller_today_bounds(self):
        """Inicio y fin del día de hoy (zona horaria del usuario) en UTC."""
        tz = pytz.timezone(self.env.user.tz or "UTC")
        today = fields.Date.context_today(self)
        start = tz.localize(datetime.combine(today, time.min)).astimezone(pytz.utc).replace(tzinfo=None)
        return start, start + timedelta(days=1)

    @api.model
    def get_taller_dashboard_data(self):
        today = fields.Date.context_today(self)
        day_start, day_end = self._taller_today_bounds()
        tz = pytz.timezone(self.env.user.tz or "UTC")
        state_labels = dict(self._fields["state"]._description_selection(self.env))

        today_domain = [
            ("schedule_date", ">=", fields.Datetime.to_string(day_start)),
            ("schedule_date", "<", fields.Datetime.to_string(day_end)),
            ("state", "!=", "cancel"),
        ]
        kpis = [
            {"key": "draft", "label": _("Por confirmar"), "icon": "fa-pencil-square-o",
             "domain": [("state", "=", "draft")]},
            {"key": "confirmed", "label": _("Confirmadas"), "icon": "fa-check",
             "domain": [("state", "=", "confirmed")]},
            {"key": "under_repair", "label": _("En reparación"), "icon": "fa-wrench",
             "domain": [("state", "=", "under_repair")]},
            {"key": "to_invoice", "label": _("Terminadas sin facturar"), "icon": "fa-file-text-o",
             "domain": [("state", "=", "done"), ("invoice_status", "!=", "invoiced")]},
            {"key": "today", "label": _("Agendadas hoy"), "icon": "fa-calendar",
             "domain": today_domain},
        ]
        for kpi in kpis:
            kpi["value"] = self.search_count(kpi["domain"])

        agenda = []
        for repair in self.search(today_domain, order="schedule_date", limit=15):
            agenda.append({
                "id": repair.id,
                "name": repair.name,
                "hour": pytz.utc.localize(repair.schedule_date).astimezone(tz).strftime("%H:%M"),
                "vehicle": repair.vehicle_id.license_plate or repair.vehicle_id.display_name or "",
                "icon": repair.vehicle_id.brand_icon_class or "",
                "logo": repair.vehicle_id.brand_logo_url or "",
                "partner": repair.partner_id.display_name or "",
                "user": repair.user_id.name or "",
                "state": repair.state,
                "state_label": state_labels.get(repair.state, repair.state),
            })

        workload = []
        groups = self._read_group(
            [("state", "in", ("confirmed", "under_repair"))], ["user_id"], ["__count"],
        )
        for user, count in sorted(groups, key=lambda g: -g[1]):
            workload.append({"user_id": user.id, "user": user.name or _("Sin asignar"), "count": count})

        Vehicle = self.env["fleet.vehicle"]
        upcoming = []
        if Vehicle.has_access("read"):
            upcoming_domain = [
                ("next_service_date", "!=", False),
                ("next_service_date", "<=", today + relativedelta(days=30)),
            ]
            for vehicle in Vehicle.search(upcoming_domain, order="next_service_date", limit=10):
                upcoming.append({
                    "id": vehicle.id,
                    "vehicle": vehicle.display_name,
                    "icon": vehicle.brand_icon_class or "",
                    "logo": vehicle.brand_logo_url or "",
                    "partner": vehicle.driver_id.display_name or "",
                    "date": fields.Date.to_string(vehicle.next_service_date),
                    "overdue": vehicle.next_service_date < today,
                })

        billing = False
        Move = self.env["account.move"]
        if Move.has_access("read"):
            month_start = today.replace(day=1)
            base = [("move_type", "in", ("out_invoice", "out_refund")), ("state", "=", "posted")]
            unpaid = base + [("payment_state", "in", ("not_paid", "partial"))]
            overdue = unpaid + [("invoice_date_due", "<", today)]
            month = base + [("invoice_date", ">=", month_start)]

            def _sum(domain, field):
                return sum(Move.search(domain).mapped(field))

            billing = {
                "currency_id": self.env.company.currency_id.id,
                "items": [
                    {"key": "month", "label": _("Facturado este mes"), "icon": "fa-line-chart",
                     "value": _sum(month, "amount_untaxed_signed"), "domain": month},
                    {"key": "unpaid", "label": _("Por cobrar"), "icon": "fa-money",
                     "value": _sum(unpaid, "amount_residual_signed"), "domain": unpaid},
                    {"key": "overdue", "label": _("Vencido"), "icon": "fa-exclamation-triangle",
                     "value": _sum(overdue, "amount_residual_signed"), "domain": overdue},
                ],
            }

        return {
            "kpis": kpis,
            "agenda": agenda,
            "workload": workload,
            "upcoming": upcoming,
            "billing": billing,
        }
