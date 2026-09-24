# -*- coding: utf-8 -*-
{
    "name": "BLER ERP - Marca",
    "version": "18.0.1.0.0",
    "category": "Hidden",
    "summary": "Marca BLER ERP en la interfaz: título, favicon, login, portal y menú de usuario",
    "description": """
Aplica la marca BLER ERP sin modificar el núcleo, solo heredando plantillas,
controladores y JS:

* Título de la pestaña del navegador "BLER ERP" (cliente web y login).
* Favicon e íconos de la aplicación web (PWA) propios. Con muk_web_theme,
  al instalar se reemplaza el favicon de la compañía solo si aún es el de
  Odoo por defecto.
* Quita "Powered by Odoo" del login y del portal.
* Quita del menú de usuario los enlaces a odoo.com (Documentación, Soporte,
  "Mi cuenta de Odoo.com").

Los logos e íconos de static/src/img son PROVISIONALES (placeholder):
reemplazarlos por los oficiales conservando los nombres de archivo.
    """,
    "author": "BLER ERP",
    "license": "LGPL-3",
    # portal ya está instalado en esta implementación (account depende de él).
    "depends": ["web", "mail", "portal"],
    "data": [
        "views/webclient_templates.xml",
        "views/portal_templates.xml",
        "views/discuss_public_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bler_branding/static/src/js/title_service_patch.js",
            "bler_branding/static/src/js/user_menu_items.js",
        ],
    },
    "post_init_hook": "_post_init_hook",
    "installable": True,
    "application": False,
}
