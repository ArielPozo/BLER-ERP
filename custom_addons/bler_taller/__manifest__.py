# -*- coding: utf-8 -*-
{
    "name": "BLER ERP - Taller",
    "version": "18.0.1.4.0",
    "category": "Inventory/Repair",
    "summary": "Órdenes de trabajo, agenda, tablero, historial por vehículo y portal de clientes",
    "description": """
Funciones de taller mecánico sobre Reparaciones y Flota (tomadas de las
aplicaciones de referencia CarCare y RepairOS):

* Catálogo separado de Servicios (mano de obra) y Repuestos (inventario).
* Líneas de servicio en la orden de trabajo, además de los repuestos, con
  total estimado. Pasan a la cotización/factura, que es un documento aparte.
* Kilometraje de ingreso y próximo mantenimiento (fecha y km) en la orden;
  al terminarla se actualizan en el vehículo.
* Agenda de trabajos (calendario por mecánico) y tablero con indicadores.
* Orden de trabajo en PDF (cliente, vehículo, servicios, repuestos, firmas).
* Vehículos asociados al cliente (pestaña y botón en la ficha del cliente).
* Ficha del vehículo con resumen e historial, también en PDF.
* Íconos de marcas de vehículos (librería car-makes-icons, MIT, la misma
  que usa CarCare), y marcas comunes en Ecuador que no trae Flota (Great
  Wall, Chery, JAC, Changan, Hino...) con su logo. Las marcas sin imagen
  toman el logo a color o, si no hay, el SVG de la librería.
* Portal de clientes (/my/vehiculos): historial, próximos mantenimientos y
  descarga de las órdenes de trabajo. Recordatorio por correo antes del
  próximo mantenimiento.
* Etiqueta QR/NFC para el tablero: enlace con token a una ficha pública
  (sin datos del cliente ni precios); el propietario con sesión ve la
  ficha completa. El enlace se puede regenerar.
    """,
    "author": "BLER ERP",
    "license": "LGPL-3",
    "depends": [
        "taller_ec_flota",
        "repair",
        "fleet",
        "sale_management",
        "sale_stock",
        "account",
        "portal",
        "mail",
    ],
    "data": [
        "security/taller_security.xml",
        "security/ir.model.access.csv",
        "data/product_data.xml",
        "data/mail_template_data.xml",
        "data/ir_cron_data.xml",
        "report/work_order_report.xml",
        "report/vehicle_report.xml",
        "report/vehicle_label_report.xml",
        "views/product_views.xml",
        "views/repair_order_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/res_partner_views.xml",
        "views/dashboard_views.xml",
        "views/portal_templates.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bler_taller/static/lib/car-makes-icons/car-makes-icons.css",
            "bler_taller/static/src/dashboard/**/*",
            "bler_taller/static/src/car_make_icon/**/*",
        ],
        "web.assets_frontend": [
            "bler_taller/static/lib/car-makes-icons/car-makes-icons.css",
        ],
        "web.report_assets_common": [
            "bler_taller/static/lib/car-makes-icons/car-makes-icons.css",
        ],
    },
    "post_init_hook": "_post_init_hook",
    "installable": True,
    "application": False,
}
