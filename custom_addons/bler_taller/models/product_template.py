# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    taller_duration = fields.Float(
        string="Duración estimada (h)",
        help="Horas de trabajo que toma el servicio. Se usa para calcular la "
             "duración de la orden en la agenda.",
    )
