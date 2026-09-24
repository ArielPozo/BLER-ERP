# -*- coding: utf-8 -*-
from odoo import models, fields


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    repair_order_ids = fields.One2many(
        "repair.order",
        "vehicle_id",
        string="Órdenes de reparación",
    )
    repair_order_count = fields.Integer(
        string="N.º de órdenes",
        compute="_compute_repair_order_count",
    )

    def _compute_repair_order_count(self):
        # Contador para el botón de historial en la ficha del vehículo.
        data = self.env["repair.order"].read_group(
            [("vehicle_id", "in", self.ids)],
            ["vehicle_id"],
            ["vehicle_id"],
        )
        mapped = {d["vehicle_id"][0]: d["vehicle_id_count"] for d in data}
        for vehicle in self:
            vehicle.repair_order_count = mapped.get(vehicle.id, 0)

    def action_view_repair_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Órdenes de reparación",
            "res_model": "repair.order",
            "view_mode": "list,form",
            "domain": [("vehicle_id", "=", self.id)],
            "context": {
                "default_vehicle_id": self.id,
                "default_partner_id": self.driver_id.id,
            },
        }
