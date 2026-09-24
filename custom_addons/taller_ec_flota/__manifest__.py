# -*- coding: utf-8 -*-
{
    "name": "BLER ERP - Flota en Órdenes de Reparación",
    "version": "18.0.1.0.1",
    "category": "Inventory/Repair",
    "summary": "Liga el vehículo (fleet) a la orden de reparación y muestra el historial por vehículo",
    "description": """
Módulo puente para talleres mecánicos:

* Agrega el campo Vehículo a la orden de reparación.
* Al elegir el vehículo, propone automáticamente su cliente (conductor).
* Muestra el historial de órdenes de reparación en la ficha del vehículo
  (botón con contador), para consultar el historial por placa.
    """,
    "author": "BLER ERP",
    "license": "LGPL-3",
    "depends": ["repair", "fleet", "mail", "spreadsheet_dashboard"],
    "data": [
        "security/taller_security.xml",
        "views/repair_order_views.xml",
        "views/fleet_vehicle_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "taller_ec_flota/static/src/scss/chatter.scss",
        ],
    },
    "installable": True,
    "application": False,
}
