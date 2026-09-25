# -*- coding: utf-8 -*-
# Paso 2 de la creación de la demo (se ejecuta con `odoo shell` después de
# instalar los módulos). Crea datos ficticios para mostrar el flujo del taller:
# catálogo, clientes, vehículos, órdenes de trabajo en distintos estados, una
# factura y el usuario mecánico. Todas las personas, empresas, placas y números
# de identificación son inventados.
from datetime import datetime, time, timedelta

import pytz

from odoo import Command, fields

TZ = pytz.timezone("America/Guayaquil")
today = fields.Date.context_today(env.user)


def at(days, hour):
    """Fecha y hora local del taller (días desde hoy) en UTC, como la guarda Odoo."""
    local = TZ.localize(datetime.combine(today + timedelta(days=days), time(hour)))
    return local.astimezone(pytz.utc).replace(tzinfo=None)


def cedula(base9):
    """Cédula ecuatoriana ficticia con dígito verificador válido (módulo 10)."""
    total = 0
    for i, digit in enumerate(base9):
        value = int(digit) * (2 if i % 2 == 0 else 1)
        total += value - 9 if value > 9 else value
    return base9 + str((10 - total % 10) % 10)


def ruc_sociedad(base9):
    """RUC ficticio de sociedad privada (tercer dígito 9, módulo 11)."""
    total = sum(int(d) * c for d, c in zip(base9, (4, 3, 2, 7, 6, 5, 4, 3, 2)))
    check = 11 - total % 11
    check = 0 if check == 11 else check
    assert check != 10, "Base de RUC sin dígito verificador válido"
    return base9 + str(check) + "001"


company = env.company
ec = env.ref("base.ec")
it_dni = env.ref("l10n_ec.ec_dni")
it_ruc = env.ref("l10n_ec.ec_ruc")
company.partner_id.write({
    "vat": ruc_sociedad("179999999"),
    "l10n_latam_identification_type_id": it_ruc.id,
})

# --- Usuario mecánico: mismos permisos que "mecanica" en producción ---------
mechanic = env["res.users"].create({
    "name": "Diego Mecánico",
    "login": "mecanico",
    "password": "mecanico",
    "lang": "es_419",
    "tz": "America/Guayaquil",
    "groups_id": [Command.set([
        env.ref("base.group_user").id,
        env.ref("stock.group_stock_user").id,
        env.ref("fleet.fleet_group_manager").id,
        env.ref("account.group_account_invoice").id,
        env.ref("bler_taller.group_taller_catalog").id,
    ])],
})

# --- Catálogo: servicios (mano de obra) y repuestos (inventario) ------------
cat_services = env.ref("bler_taller.product_category_services")
cat_parts = env.ref("bler_taller.product_category_parts")


def service(name, price, hours):
    return env["product.product"].create({
        "name": name, "type": "service", "categ_id": cat_services.id,
        "list_price": price, "taller_duration": hours,
    })


def part(name, price, cost, qty, code):
    product = env["product.product"].create({
        "name": name, "type": "consu", "is_storable": True, "categ_id": cat_parts.id,
        "list_price": price, "standard_price": cost, "default_code": code,
    })
    env["stock.quant"].create({
        "product_id": product.id,
        "location_id": env.ref("stock.warehouse0").lot_stock_id.id,
        "inventory_quantity": qty,
    }).action_apply_inventory()
    return product


s_oil = service("Cambio de aceite y filtro (mano de obra)", 15.0, 0.75)
s_align = service("Alineación y balanceo", 25.0, 1.0)
s_brakes = service("ABC de frenos", 35.0, 2.0)
s_scan = service("Diagnóstico por escáner", 20.0, 0.5)
s_tuneup = service("Afinamiento de motor", 45.0, 2.5)
s_susp = service("Revisión de suspensión", 30.0, 1.5)

p_oil = part("Aceite de motor 10W-30 (galón)", 28.0, 18.0, 40, "ACE-1030")
p_filter = part("Filtro de aceite", 8.5, 4.0, 30, "FIL-ACE")
p_air = part("Filtro de aire", 14.0, 7.0, 15, "FIL-AIR")
p_pads = part("Pastillas de freno delanteras", 42.0, 24.0, 12, "FRE-PAS")
p_plugs = part("Juego de bujías (4)", 32.0, 18.0, 10, "BUJ-4")
p_battery = part("Batería 12V 60Ah", 110.0, 75.0, 4, "BAT-60")

# --- Clientes -----------------------------------------------------------------
Partner = env["res.partner"]
common = {"country_id": ec.id, "lang": "es_419"}
maria = Partner.create(dict(common, name="María Fernanda Salazar", city="Quito",
                            email="maria.salazar@example.com", mobile="+593 99 111 2233",
                            vat=cedula("171234567"), l10n_latam_identification_type_id=it_dni.id))
carlos = Partner.create(dict(common, name="Carlos Andrade", city="Quito",
                             email="carlos.andrade@example.com", mobile="+593 98 222 3344",
                             vat=cedula("170987654"), l10n_latam_identification_type_id=it_dni.id))
gabriela = Partner.create(dict(common, name="Gabriela Ortiz", city="Sangolquí",
                               email="gabriela.ortiz@example.com", mobile="+593 97 333 4455",
                               vat=cedula("171122334"), l10n_latam_identification_type_id=it_dni.id))
andinos = Partner.create(dict(common, name="Transportes Andinos S.A.", is_company=True, city="Quito",
                              email="flota@transportesandinos.example.com", phone="+593 2 244 5566",
                              vat=ruc_sociedad("179111111"), l10n_latam_identification_type_id=it_ruc.id))
Partner.create(dict(common, name="Luis Cevallos", parent_id=andinos.id, function="Jefe de flota",
                    email="luis.cevallos@transportesandinos.example.com", mobile="+593 99 444 5566"))

# --- Vehículos ----------------------------------------------------------------
Brand = env["fleet.vehicle.model.brand"]
Model = env["fleet.vehicle.model"]


def vehicle(brand_name, model_name, plate, year, color, driver, odometer):
    brand = Brand.search([("name", "=ilike", brand_name)], limit=1) or Brand.create({"name": brand_name})
    model = Model.search([("brand_id", "=", brand.id), ("name", "=ilike", model_name)], limit=1) \
        or Model.create({"name": model_name, "brand_id": brand.id})
    car = env["fleet.vehicle"].create({
        "model_id": model.id, "license_plate": plate, "model_year": str(year),
        "color": color, "driver_id": driver.id,
    })
    env["fleet.vehicle.odometer"].create({
        "vehicle_id": car.id, "value": odometer, "date": today - timedelta(days=200),
    })
    return car


aveo = vehicle("Chevrolet", "Aveo", "PCA-1234", 2018, "Gris", maria, 84000)
hilux = vehicle("Toyota", "Hilux", "PBX-5678", 2021, "Blanco", andinos, 61000)
tiggo = vehicle("Chery", "Tiggo 4", "PBX-7777", 2022, "Negro", andinos, 30500)
sportage = vehicle("Kia", "Sportage", "PDF-9012", 2020, "Rojo", carlos, 45000)
accent = vehicle("Hyundai", "Accent", "GYE-3456", 2019, "Azul", gabriela, 73000)

# --- Órdenes de trabajo -------------------------------------------------------
Repair = env["repair.order"]


def repair(car, when, odometer, services, parts, request, next_days=None, next_km=None, **extra):
    order = Repair.create(dict({
        "vehicle_id": car.id,
        "partner_id": car.driver_id.id,
        "user_id": mechanic.id,
        "schedule_date": when,
        "odometer": odometer,
        "internal_notes": False,
        "repair_request": request,
        "next_service_date": today + timedelta(days=next_days) if next_days is not None else False,
        "next_service_km": next_km or 0.0,
        "service_line_ids": [Command.create({"product_id": s.id}) for s in services],
        "move_ids": [Command.create({
            "product_id": p.id, "product_uom_qty": qty, "repair_line_type": "add",
        }) for p, qty in parts],
    }, **extra))
    return order


def finish(order):
    order.action_validate()
    order.action_repair_start()
    for move in order.move_ids:
        move.quantity = move.product_uom_qty
        move.picked = True
    order.action_repair_end()
    return order


# Historial terminado (el Aveo y la Tiggo), una de ellas ya facturada.
old = finish(repair(aveo, at(-150, 9), 86500, [s_oil], [(p_oil, 1), (p_filter, 1)],
                    "Mantenimiento de 5.000 km", next_days=-60, next_km=91500))
recent = finish(repair(aveo, at(-12, 10), 91800, [s_oil, s_align], [(p_oil, 1), (p_filter, 1), (p_air, 1)],
                       "Mantenimiento y vibración en el volante", next_days=10, next_km=96800))
invoice_action = recent.action_taller_invoice()
invoice = env["account.move"].browse(invoice_action.get("res_id"))
try:
    with env.cr.savepoint():
        invoice.action_post()
except Exception as exc:  # la localización puede pedir datos extra; queda en borrador
    print("Factura demo en borrador: %s" % exc)
finish(repair(tiggo, at(-30, 8), 35200, [s_scan, s_tuneup], [(p_plugs, 1)],
              "Pérdida de potencia y luz de check engine", next_days=90, next_km=45000))

# Kia con el mantenimiento vencido y una cita para mañana (confirmada).
finish(repair(sportage, at(-200, 11), 48000, [s_oil], [(p_oil, 1), (p_filter, 1)],
              "Mantenimiento de 5.000 km", next_days=-15, next_km=53000))
tomorrow = repair(sportage, at(1, 9), 53400, [s_brakes], [(p_pads, 1)], "Ruido al frenar")
tomorrow.action_validate()

# Hilux de la flota en el taller hoy (en reparación).
today_repair = repair(hilux, at(0, 8), 62300, [s_susp, s_align], [], "Golpeteo en la suspensión delantera")
today_repair.action_validate()
today_repair.action_repair_start()

# Accent: presupuesto en borrador, pendiente de aprobación del cliente.
quote = repair(accent, at(2, 14), 74100, [s_scan, s_oil], [(p_battery, 1), (p_oil, 1), (p_filter, 1)],
               "No arranca en las mañanas; revisar batería")
quote.action_create_sale_order()

# Marca que usa iniciar_demo.bat para saber que la base quedó completa.
env["ir.config_parameter"].sudo().set_param("bler_demo.seeded", fields.Datetime.now())
env.cr.commit()
print("Datos de demo creados: %s vehículos, %s órdenes, factura %s (%s)" % (
    env["fleet.vehicle"].search_count([]), Repair.search_count([]), invoice.name, invoice.state))
