# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api

from odoo.addons.bler_branding import _replace_default_favicon


def migrate(cr, version):
    # 18.0.1.3.0 cambia el favicon provisional por el logo oficial; las
    # compañías que aún tienen el provisional (o el de Odoo) lo reciben.
    env = api.Environment(cr, SUPERUSER_ID, {})
    _replace_default_favicon(env)
