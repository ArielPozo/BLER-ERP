# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    # Marcas comunes en Ecuador que no trae Flota, y logos para las que no
    # tienen imagen.
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["fleet.vehicle.model.brand"]._load_extra_brands()
