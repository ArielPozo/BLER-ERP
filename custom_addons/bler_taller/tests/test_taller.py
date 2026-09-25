# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import HttpCase, TransactionCase, tagged


class TallerCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Cliente Taller", "email": "cliente@example.com"})
        brand = cls.env["fleet.vehicle.model.brand"].create({"name": "Chevrolet"})
        model = cls.env["fleet.vehicle.model"].create({"name": "Aveo", "brand_id": brand.id})
        cls.vehicle = cls.env["fleet.vehicle"].create({
            "model_id": model.id,
            "license_plate": "PBA-1234",
            "driver_id": cls.partner.id,
        })
        cls.service = cls.env["product.product"].create({
            "name": "Cambio de aceite (MO)",
            "type": "service",
            "list_price": 20.0,
            "taller_duration": 1.5,
        })
        cls.part = cls.env["product.product"].create({
            "name": "Filtro de aceite",
            "type": "consu",
            "is_storable": True,
            "list_price": 8.0,
        })

    def _create_repair(self, **vals):
        return self.env["repair.order"].create({
            "partner_id": self.partner.id,
            "vehicle_id": self.vehicle.id,
            "service_line_ids": [fields.Command.create({"product_id": self.service.id, "quantity": 2})],
            "move_ids": [fields.Command.create({
                "product_id": self.part.id,
                "product_uom_qty": 1,
                "repair_line_type": "add",
            })],
            **vals,
        })


@tagged("post_install", "-at_install")
class TestTaller(TallerCommon):

    def test_amounts_and_duration(self):
        repair = self._create_repair()
        self.assertEqual(repair.amount_services, 40.0)
        self.assertEqual(repair.amount_parts, 8.0)
        self.assertEqual(repair.amount_total, 48.0)
        self.assertEqual(repair.taller_duration, 3.0)
        self.assertEqual(repair.schedule_date_end, repair.schedule_date + timedelta(hours=3))

    def test_quotation_has_services_and_parts(self):
        repair = self._create_repair()
        repair.action_create_sale_order()
        order = repair.sale_order_id
        self.assertEqual(set(order.order_line.product_id.ids), {self.service.id, self.part.id})
        service_line = order.order_line.filtered(lambda l: l.product_id == self.service)
        self.assertEqual(service_line.product_uom_qty, 2)
        # Un servicio agregado después también llega a la cotización.
        repair.write({"service_line_ids": [fields.Command.create({"product_id": self.service.id, "quantity": 1})]})
        self.assertEqual(sum(order.order_line.filtered(lambda l: l.product_id == self.service).mapped("product_uom_qty")), 3)
        # Y al quitarlo se elimina de la cotización (aún en borrador).
        repair.service_line_ids[-1].unlink()
        self.assertEqual(len(order.order_line.filtered(lambda l: l.product_id == self.service)), 1)

    def test_done_updates_vehicle_and_invoice(self):
        self.env["stock.quant"]._update_available_quantity(
            self.part, self.env.ref("stock.stock_location_stock"), 5)
        next_date = fields.Date.today() + timedelta(days=90)
        repair = self._create_repair(odometer=15000, next_service_date=next_date, next_service_km=20000)
        repair.action_validate()
        repair.action_repair_start()
        repair.action_repair_end()
        self.assertEqual(repair.state, "done")
        self.assertEqual(self.vehicle.odometer, 15000)
        self.assertEqual(self.vehicle.next_service_date, next_date)
        self.assertEqual(self.vehicle.next_service_km, 20000)
        self.assertEqual(self.vehicle.repair_done_count, 1)

        action = repair.action_taller_invoice()
        invoice = self.env["account.move"].browse(action["res_id"])
        self.assertEqual(invoice.move_type, "out_invoice")
        self.assertEqual(invoice.amount_untaxed, 48.0)
        self.assertEqual(repair.invoice_count, 1)
        self.assertEqual(repair.invoice_status, "invoiced")

    def test_reminder_cron(self):
        self.vehicle.next_service_date = fields.Date.today() + timedelta(days=3)
        self.env["fleet.vehicle"]._cron_send_service_reminders()
        self.assertTrue(self.vehicle.next_service_reminder_sent)
        self.assertTrue(self.vehicle.message_ids.filtered(lambda m: "Recordatorio" in (m.subject or "")))
        # Cambiar la fecha vuelve a habilitar el recordatorio.
        self.vehicle.next_service_date = fields.Date.today() + timedelta(days=60)
        self.assertFalse(self.vehicle.next_service_reminder_sent)

    def test_dashboard_and_reports(self):
        repair = self._create_repair(schedule_date=fields.Datetime.now())
        data = self.env["repair.order"].get_taller_dashboard_data()
        kpis = {k["key"]: k["value"] for k in data["kpis"]}
        self.assertGreaterEqual(kpis["draft"], 1)
        self.assertIn(repair.id, [row["id"] for row in data["agenda"]])
        self.assertTrue(data["billing"])
        html = self.env["ir.actions.report"]._render_qweb_html(
            "bler_taller.action_report_work_order", repair.ids)[0].decode()
        self.assertIn("PBA-1234", html)
        self.assertIn("Cambio de aceite (MO)", html)
        html = self.env["ir.actions.report"]._render_qweb_html(
            "bler_taller.action_report_vehicle_history", self.vehicle.ids)[0].decode()
        self.assertIn(repair.name, html)

    def test_repair_user_sees_customer_vehicles(self):
        user = self.env["res.users"].create({
            "name": "Mecánico",
            "login": "mecanico_test",
            "groups_id": [fields.Command.set([
                self.env.ref("base.group_user").id,
                self.env.ref("stock.group_stock_user").id,
                self.env.ref("fleet.fleet_group_user").id,
            ])],
        })
        vehicles = self.env["fleet.vehicle"].with_user(user).search([("id", "=", self.vehicle.id)])
        self.assertEqual(vehicles, self.vehicle)
        new_vehicle = self.env["fleet.vehicle"].with_user(user).create({
            "model_id": self.vehicle.model_id.id,
            "license_plate": "GYE-0001",
            "driver_id": self.partner.id,
        })
        self.assertIn(new_vehicle, self.partner.taller_vehicle_ids)

    def test_catalog_group_can_create_products(self):
        user = self.env["res.users"].create({
            "name": "Mecánico catálogo",
            "login": "mecanico_catalogo",
            "groups_id": [fields.Command.set([
                self.env.ref("base.group_user").id,
                self.env.ref("stock.group_stock_user").id,
            ])],
        })
        Product = self.env["product.template"].with_user(user)
        with self.assertRaises(AccessError):
            Product.create({"name": "Sin permiso", "type": "service"})

        user.groups_id = [fields.Command.link(self.env.ref("bler_taller.group_taller_catalog").id)]
        service = Product.create({"name": "Alineación", "type": "service", "list_price": 15.0})
        part = Product.create({"name": "Pastillas de freno", "type": "consu", "is_storable": True})
        part.write({"list_price": 30.0})
        self.assertEqual(service.type, "service")
        self.assertTrue(part.is_storable)


@tagged("post_install", "-at_install")
class TestTallerPortal(HttpCase, TallerCommon):

    def test_portal_vehicle_pages(self):
        portal_user = self.env["res.users"].create({
            "name": "Cliente Portal",
            "login": "cliente_portal",
            "password": "cliente_portal",
            "partner_id": self.partner.id,
            "groups_id": [fields.Command.set([self.env.ref("base.group_portal").id])],
        })
        other = self.env["fleet.vehicle"].create({
            "model_id": self.vehicle.model_id.id,
            "license_plate": "OTRO-999",
            "driver_id": self.env["res.partner"].create({"name": "Otro"}).id,
        })
        repair = self._create_repair()
        self.authenticate(portal_user.login, "cliente_portal")

        res = self.url_open("/my/vehiculos")
        self.assertEqual(res.status_code, 200)
        self.assertIn("PBA-1234", res.text)
        self.assertNotIn("OTRO-999", res.text)

        res = self.url_open("/my/vehiculos/%s" % self.vehicle.id)
        self.assertEqual(res.status_code, 200)
        self.assertIn(repair.name, res.text)

        self.assertEqual(self.url_open("/my/vehiculos/%s" % other.id).status_code, 404)

    def test_public_vehicle_link(self):
        repair = self._create_repair()
        vehicle = self.vehicle
        self.assertFalse(vehicle.public_url, "Sin token no hay enlace")
        vehicle.action_print_qr_label()
        self.assertTrue(vehicle.access_token)
        self.assertTrue(vehicle.public_url.endswith(
            "/vehiculo/%s?access_token=%s" % (vehicle.id, vehicle.access_token)))
        url = "/vehiculo/%s" % vehicle.id

        # Sin token o con uno inválido: no existe.
        self.assertEqual(self.url_open(url).status_code, 404)
        self.assertEqual(self.url_open(url + "?access_token=malo").status_code, 404)

        # Con el token: ficha pública sin datos del cliente.
        token = vehicle.access_token
        res = self.url_open(url + "?access_token=" + token)
        self.assertEqual(res.status_code, 200)
        self.assertIn("PBA-1234", res.text)
        self.assertIn(repair.service_line_ids[:1].product_id.name, res.text)
        self.assertNotIn(self.partner.name, res.text)
        self.assertNotIn("/my/vehiculos/%s/orden" % vehicle.id, res.text)
        self.assertEqual(res.headers.get("Referrer-Policy"), "no-referrer")

        # Regenerar invalida la etiqueta anterior.
        vehicle.action_regenerate_public_url()
        self.assertNotEqual(vehicle.access_token, token)
        self.assertEqual(self.url_open(url + "?access_token=" + token).status_code, 404)

    def test_public_vehicle_link_owner_redirect(self):
        self.env["res.users"].create({
            "name": "Cliente Portal",
            "login": "cliente_qr",
            "password": "cliente_qr",
            "partner_id": self.partner.id,
            "groups_id": [fields.Command.set([self.env.ref("base.group_portal").id])],
        })
        self.vehicle._portal_ensure_token()
        self.authenticate("cliente_qr", "cliente_qr")
        res = self.url_open("/vehiculo/%s?access_token=%s" % (self.vehicle.id, self.vehicle.access_token),
                            allow_redirects=False)
        self.assertIn(res.status_code, (302, 303))
        self.assertTrue(res.headers["Location"].endswith("/my/vehiculos/%s" % self.vehicle.id))

    def test_vehicle_label_report(self):
        self.vehicle.action_print_qr_label()
        self.assertTrue(self.vehicle.access_token, "Imprimir la etiqueta genera el enlace")
        html = self.env["ir.actions.report"]._render_qweb_html(
            "bler_taller.report_vehicle_label", self.vehicle.ids)[0].decode()
        self.assertIn("PBA-1234", html)
        self.assertIn("data:image/png;base64", html)


@tagged("post_install", "-at_install")
class TestCarMakeIcons(TransactionCase):

    def test_brand_icon_and_logo(self):
        Brand = self.env["fleet.vehicle.model.brand"]
        gmc = Brand.create({"name": "GMC"})
        self.assertEqual(gmc.icon_class, "car-gmc")
        self.assertTrue(gmc.image_128, "La marca sin imagen toma el logo por defecto")
        self.assertTrue(gmc.logo_url)
        self.assertEqual(Brand.new({"name": "Mercedes"}).icon_class, "car-mercedes-benz")
        self.assertEqual(Brand.new({"name": "Rolls-Royce"}).icon_class, "car-rolls-royce")
        # Marca sin ícono en la fuente pero con logo a color.
        great_wall = Brand.create({"name": "Great wall"})
        self.assertFalse(great_wall.icon_class)
        self.assertTrue(great_wall.image_128)
        self.assertTrue(Brand.create({"name": "Lynk & Co"}).image_128)
        # Marca desconocida: sin ícono ni logo.
        unknown = Brand.create({"name": "Marca Inventada"})
        self.assertFalse(unknown.icon_class)
        self.assertFalse(unknown.image_128)
        self.assertFalse(unknown.logo_url)

    def test_load_extra_brands_without_duplicates(self):
        Brand = self.env["fleet.vehicle.model.brand"]
        Brand._load_extra_brands()
        count = Brand.search_count([])
        Brand._load_extra_brands()
        self.assertEqual(Brand.search_count([]), count)
        for name in ("Chery", "JAC", "Hino", "Changan"):
            brand = Brand.search([("name", "=", name)])
            self.assertEqual(len(brand), 1, name)
            self.assertTrue(brand.image_128, name)
