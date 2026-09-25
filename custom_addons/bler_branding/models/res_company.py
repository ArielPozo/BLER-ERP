# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    bler_logo_card_transparent = fields.Boolean(
        string="Tarjeta del logo transparente",
        help="Quita el fondo blanco de la tarjeta con el logo de la compañía en "
             "la barra lateral. Útil si el logo está hecho para fondo oscuro.",
    )
