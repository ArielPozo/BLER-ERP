# -*- coding: utf-8 -*-
from odoo.http import request

from odoo.addons.web.controllers.webmanifest import WebManifest

BRAND_NAME = "BLER ERP"
BRAND_COLOR = "#1E1B4B"


class BlerWebManifest(WebManifest):

    def _get_webmanifest(self):
        # Manifiesto de la aplicación web (PWA): nombre, colores e íconos de BLER ERP.
        manifest = super()._get_webmanifest()
        custom_name = request.env["ir.config_parameter"].sudo().get_param("web.web_app_name")
        if not custom_name:
            manifest["name"] = BRAND_NAME
        manifest["background_color"] = BRAND_COLOR
        manifest["theme_color"] = BRAND_COLOR
        manifest["icons"] = [{
            "src": "/bler_branding/static/src/img/bler_icon_%s.png" % size,
            "sizes": "%sx%s" % (size, size),
            "type": "image/png",
        } for size in (192, 512)]
        return manifest
