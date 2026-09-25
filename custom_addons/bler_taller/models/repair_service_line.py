# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RepairServiceLine(models.Model):
    """Servicio (mano de obra) de una orden de trabajo.

    Los repuestos siguen siendo movimientos de inventario (``move_ids``); los
    servicios no mueven stock, por eso van en este modelo aparte. Cuando la
    orden tiene cotización, cada línea se refleja en una línea de venta.
    """
    _name = "repair.service.line"
    _description = "Servicio de la orden de trabajo"
    _order = "repair_id, sequence, id"

    repair_id = fields.Many2one(
        "repair.order", string="Orden", required=True, ondelete="cascade", index=True,
    )
    company_id = fields.Many2one(related="repair_id.company_id", store=True)
    currency_id = fields.Many2one(related="company_id.currency_id")
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product", string="Servicio", required=True,
        domain="[('type', '=', 'service'), ('sale_ok', '=', True)]",
    )
    name = fields.Char(
        string="Descripción", compute="_compute_name", store=True, readonly=False,
    )
    quantity = fields.Float(string="Cantidad", default=1.0, digits="Product Unit of Measure")
    price_unit = fields.Float(
        string="Precio unitario", compute="_compute_price_unit", store=True,
        readonly=False, digits="Product Price",
    )
    discount = fields.Float(string="Desc. %", digits="Discount")
    price_subtotal = fields.Monetary(
        string="Subtotal", compute="_compute_price_subtotal", store=True,
    )
    duration = fields.Float(
        string="Horas", compute="_compute_duration", store=True, readonly=False,
    )
    sale_line_id = fields.Many2one("sale.order.line", string="Línea de venta", copy=False, readonly=True)

    @api.depends("product_id")
    def _compute_name(self):
        for line in self:
            if line.product_id:
                line.name = line.product_id.get_product_multiline_description_sale()

    @api.depends("product_id")
    def _compute_price_unit(self):
        for line in self:
            if line.product_id:
                line.price_unit = line.product_id.lst_price

    @api.depends("product_id", "quantity")
    def _compute_duration(self):
        for line in self:
            line.duration = line.product_id.taller_duration * line.quantity

    @api.depends("quantity", "price_unit", "discount", "repair_id.under_warranty")
    def _compute_price_subtotal(self):
        for line in self:
            if line.repair_id.under_warranty:
                line.price_subtotal = 0.0
            else:
                line.price_subtotal = line.quantity * line.price_unit * (1 - line.discount / 100.0)

    # --- Sincronización con la cotización -------------------------------

    def _prepare_sale_line_vals(self):
        self.ensure_one()
        return {
            "order_id": self.repair_id.sale_order_id.id,
            "product_id": self.product_id.id,
            "name": self.name,
            "product_uom_qty": self.quantity,
            "price_unit": 0.0 if self.repair_id.under_warranty else self.price_unit,
            "discount": self.discount,
        }

    def _create_sale_lines(self):
        for line in self:
            order = line.repair_id.sale_order_id
            if line.sale_line_id or not order or order.state == "cancel":
                continue
            line.sale_line_id = self.env["sale.order.line"].create(line._prepare_sale_line_vals())

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._create_sale_lines()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if {"product_id", "name", "quantity", "price_unit", "discount"} & set(vals):
            for line in self.filtered(lambda l: l.sale_line_id and l.sale_line_id.order_id.state != "cancel"):
                sale_vals = line._prepare_sale_line_vals()
                sale_vals.pop("order_id")
                if line.sale_line_id.product_id == line.product_id:
                    sale_vals.pop("product_id")
                line.sale_line_id.write(sale_vals)
        return res

    def unlink(self):
        sale_lines = self.sale_line_id.filtered(lambda l: l.order_id.state != "cancel")
        res = super().unlink()
        # En cotización se borra la línea; en pedido confirmado se deja en 0.
        sale_lines.filtered(lambda l: l.order_id.state in ("draft", "sent")).unlink()
        sale_lines.exists().write({"product_uom_qty": 0.0})
        return res
