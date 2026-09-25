# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, api

from odoo.addons.bler_branding import _rebrand_mail_templates


def migrate(cr, version):
    # Instalaciones anteriores a 18.0.1.2.0 no ejecutaron esta limpieza en el
    # post_init_hook.
    env = api.Environment(cr, SUPERUSER_ID, {})
    _rebrand_mail_templates(env)
