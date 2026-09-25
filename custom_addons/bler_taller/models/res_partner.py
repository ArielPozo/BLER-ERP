# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    taller_vehicle_ids = fields.One2many("fleet.vehicle", "driver_id", string="Vehículos")
    taller_vehicle_count = fields.Integer(string="N.º de vehículos", compute="_compute_taller_counts")
    taller_repair_count = fields.Integer(string="N.º de órdenes de trabajo", compute="_compute_taller_counts")

    def _compute_taller_counts(self):
        Vehicle = self.env["fleet.vehicle"]
        Repair = self.env["repair.order"]
        can_vehicle = Vehicle.has_access("read")
        can_repair = Repair.has_access("read")
        for partner in self:
            partner.taller_vehicle_count = can_vehicle and Vehicle.search_count(
                [("driver_id", "child_of", partner.id)])
            partner.taller_repair_count = can_repair and Repair.search_count(
                [("partner_id", "child_of", partner.id)])

    def action_view_taller_vehicles(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Vehículos",
            "res_model": "fleet.vehicle",
            "view_mode": "kanban,list,form",
            "domain": [("driver_id", "child_of", self.id)],
            "context": {"default_driver_id": self.id},
        }

    def action_view_taller_repairs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Órdenes de trabajo",
            "res_model": "repair.order",
            "view_mode": "list,form,calendar",
            "domain": [("partner_id", "child_of", self.id)],
            "context": {"default_partner_id": self.id},
        }
