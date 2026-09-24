# -*- coding: utf-8 -*-
from odoo import models, fields, api


class RepairOrder(models.Model):
    _inherit = "repair.order"

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehículo",
        help="Vehículo del cliente asociado a esta orden de reparación.",
    )

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        # Al elegir el vehículo, proponer su cliente (conductor) si no hay uno.
        if self.vehicle_id and self.vehicle_id.driver_id and not self.partner_id:
            self.partner_id = self.vehicle_id.driver_id
