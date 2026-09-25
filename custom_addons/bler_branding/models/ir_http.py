# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        # La tarjeta del logo de la barra lateral (static/src/webclient/appsbar)
        # lee esta opción de la compañía actual.
        result = super().session_info()
        if self.env.user._is_internal():
            allowed = result["user_companies"]["allowed_companies"]
            for company in self.env.user.company_ids:
                if company.id in allowed:
                    allowed[company.id]["bler_logo_card_transparent"] = company.bler_logo_card_transparent
        return result
