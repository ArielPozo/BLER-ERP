# -*- coding: utf-8 -*-
import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Días de anticipación del recordatorio de mantenimiento por correo.
REMINDER_DAYS = 7


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    brand_icon_class = fields.Char(related="brand_id.icon_class", string="Ícono de la marca")
    brand_logo_url = fields.Char(related="brand_id.logo_url", string="Logo de la marca")
    next_service_date = fields.Date(string="Próximo mantenimiento", tracking=True)
    next_service_km = fields.Float(string="Próximo mantenimiento (km)", tracking=True)
    next_service_reminder_sent = fields.Boolean(
        string="Recordatorio enviado", copy=False,
        help="Se marca al enviar el correo de recordatorio y se desmarca al "
             "cambiar la fecha del próximo mantenimiento.",
    )
    service_status = fields.Selection(
        [("none", "Sin programar"), ("ok", "Al día"), ("soon", "Próximo"), ("overdue", "Vencido")],
        string="Mantenimiento", compute="_compute_service_status",
    )
    last_repair_date = fields.Datetime(string="Última visita", compute="_compute_repair_summary")
    repair_done_count = fields.Integer(string="Trabajos terminados", compute="_compute_repair_summary")
    repair_amount_total = fields.Monetary(string="Total en trabajos", compute="_compute_repair_summary")

    @api.depends("next_service_date")
    def _compute_service_status(self):
        today = fields.Date.context_today(self)
        for vehicle in self:
            if not vehicle.next_service_date:
                vehicle.service_status = "none"
            elif vehicle.next_service_date < today:
                vehicle.service_status = "overdue"
            elif vehicle.next_service_date <= today + relativedelta(days=30):
                vehicle.service_status = "soon"
            else:
                vehicle.service_status = "ok"

    @api.depends("repair_order_ids.state", "repair_order_ids.amount_total")
    def _compute_repair_summary(self):
        for vehicle in self:
            done = vehicle.repair_order_ids.filtered(lambda r: r.state == "done")
            vehicle.repair_done_count = len(done)
            vehicle.repair_amount_total = sum(done.mapped("amount_total"))
            dates = vehicle.repair_order_ids.filtered(lambda r: r.state != "cancel").mapped("schedule_date")
            vehicle.last_repair_date = max(dates) if dates else False

    def write(self, vals):
        if "next_service_date" in vals:
            vals = dict(vals, next_service_reminder_sent=False)
        return super().write(vals)

    @api.model
    def _taller_portal_domain(self, partner):
        """Vehículos que un usuario del portal puede ver: los de su empresa."""
        return [("driver_id", "child_of", partner.commercial_partner_id.id)]

    def _get_report_base_filename(self):
        self.ensure_one()
        return "Ficha %s" % (self.license_plate or self.name)

    def action_new_repair_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Nueva orden de trabajo",
            "res_model": "repair.order",
            "view_mode": "form",
            "context": {
                "default_vehicle_id": self.id,
                "default_partner_id": self.driver_id.id,
                "default_odometer": self.odometer,
            },
        }

    def action_print_vehicle_history(self):
        return self.env.ref("bler_taller.action_report_vehicle_history").report_action(self)

    @api.model
    def _cron_send_service_reminders(self):
        """Avisa por correo al cliente cuando se acerca el próximo mantenimiento."""
        today = fields.Date.context_today(self)
        vehicles = self.search([
            ("next_service_date", "!=", False),
            ("next_service_date", ">=", today),
            ("next_service_date", "<=", today + relativedelta(days=REMINDER_DAYS)),
            ("next_service_reminder_sent", "=", False),
            ("driver_id.email", "!=", False),
        ])
        template = self.env.ref("bler_taller.mail_template_service_reminder")
        for vehicle in vehicles:
            vehicle.message_post_with_source(template, subtype_xmlid="mail.mt_comment")
            vehicle.next_service_reminder_sent = True
        _logger.info("Recordatorios de mantenimiento enviados: %s", len(vehicles))
