# -*- coding: utf-8 -*-
import base64

from odoo.tools import file_open

from . import controllers

BLER_FAVICON = "bler_branding/static/src/img/favicon_placeholder.ico"


def _post_init_hook(env):
    """Si muk_web_theme está instalado, el favicon sale del campo
    res.company.favicon, que MuK llena al instalarse con el favicon de Odoo.
    Solo se reemplaza en las compañías que aún tienen ese favicon por defecto;
    un favicon subido en Ajustes → Marca se respeta."""
    Company = env["res.company"].sudo()
    if "favicon" not in Company._fields:
        return
    with file_open("web/static/img/favicon.ico", "rb") as file:
        odoo_favicon = base64.b64encode(file.read())
    with file_open(BLER_FAVICON, "rb") as file:
        bler_favicon = base64.b64encode(file.read())
    for company in Company.with_context(bin_size=False).search([]):
        if company.favicon == odoo_favicon:
            company.favicon = bler_favicon
