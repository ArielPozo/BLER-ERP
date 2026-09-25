# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    # Logo de car-makes-icons para las marcas existentes que no tienen imagen.
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["fleet.vehicle.model.brand"].search([])._set_default_logo()
