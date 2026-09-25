# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class TallerCustomerPortal(CustomerPortal):
    """Portal del cliente: sus vehículos, historial y próximos mantenimientos.

    Los usuarios del portal no tienen permisos sobre Flota ni Reparaciones, así
    que se lee con sudo() filtrando siempre por la empresa del usuario.
    """

    def _taller_vehicles(self):
        partner = request.env.user.partner_id
        Vehicle = request.env["fleet.vehicle"].sudo()
        return Vehicle.search(Vehicle._taller_portal_domain(partner), order="license_plate")

    def _taller_vehicle_or_404(self, vehicle_id):
        vehicle = self._taller_vehicles().filtered(lambda v: v.id == vehicle_id)
        if not vehicle:
            raise request.not_found()
        return vehicle

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "taller_vehicle_count" in counters:
            values["taller_vehicle_count"] = len(self._taller_vehicles())
        return values

    @http.route(["/my/vehiculos"], type="http", auth="user", website=True)
    def portal_my_vehicles(self, **kw):
        values = self._prepare_portal_layout_values()
        values.update({
            "vehicles": self._taller_vehicles(),
            "page_name": "taller_vehicles",
        })
        return request.render("bler_taller.portal_my_vehicles", values)

    @http.route(["/my/vehiculos/<int:vehicle_id>"], type="http", auth="user", website=True)
    def portal_my_vehicle(self, vehicle_id, **kw):
        vehicle = self._taller_vehicle_or_404(vehicle_id)
        repairs = vehicle.repair_order_ids.filtered(lambda r: r.state != "cancel").sorted(
            "schedule_date", reverse=True)
        values = self._prepare_portal_layout_values()
        values.update({
            "vehicle": vehicle,
            "repairs": repairs,
            "page_name": "taller_vehicle",
        })
        return request.render("bler_taller.portal_my_vehicle", values)

    @http.route(["/my/vehiculos/<int:vehicle_id>/orden/<int:repair_id>"], type="http", auth="user", website=True)
    def portal_my_work_order_pdf(self, vehicle_id, repair_id, **kw):
        vehicle = self._taller_vehicle_or_404(vehicle_id)
        repair = vehicle.repair_order_ids.filtered(lambda r: r.id == repair_id and r.state != "cancel")
        if not repair:
            raise request.not_found()
        return self._show_report(repair, "pdf", "bler_taller.action_report_work_order", download=kw.get("download"))

    @http.route(["/my/vehiculos/<int:vehicle_id>/ficha"], type="http", auth="user", website=True)
    def portal_my_vehicle_pdf(self, vehicle_id, **kw):
        vehicle = self._taller_vehicle_or_404(vehicle_id)
        return self._show_report(vehicle, "pdf", "bler_taller.action_report_vehicle_history", download=kw.get("download"))
