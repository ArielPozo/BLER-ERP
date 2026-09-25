# -*- coding: utf-8 -*-
{
    "name": "BLER ERP - Marca",
    "version": "18.0.1.2.0",
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
* Cambia "Odoo" por "BLER ERP" en los títulos de los diálogos ("Error de
  servidor de Odoo", "Advertencia de Odoo", "Expiró la sesión de Odoo"...).
  "Odoo.com" y "Odoo Enterprise" no se cambian.
* Quita "Powered by Odoo" de los correos (notificaciones, contraseña,
  alerta de nuevo dispositivo, resumen periódico, invitación al portal).

Los logos e íconos de static/src/img son PROVISIONALES (placeholder):
reemplazarlos por los oficiales conservando los nombres de archivo.
    """,
    "author": "BLER ERP",
    "license": "LGPL-3",
    # portal ya está instalado en esta implementación (account depende de él);
    # auth_signup y digest también (dependencias de portal y mail/account).
    "depends": ["web", "mail", "portal", "auth_signup", "digest"],
    "data": [
        "views/webclient_templates.xml",
        "views/portal_templates.xml",
        "views/discuss_public_templates.xml",
        "views/mail_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bler_branding/static/src/js/brand.js",
            "bler_branding/static/src/js/title_service_patch.js",
            "bler_branding/static/src/js/user_menu_items.js",
            "bler_branding/static/src/js/dialogs_patch.js",
            "bler_branding/static/src/xml/dialogs.xml",
        ],
        "web.assets_frontend": [
            "bler_branding/static/src/js/brand.js",
            "bler_branding/static/src/js/public_error_notifications_patch.js",
        ],
    },
    "post_init_hook": "_post_init_hook",
    "installable": True,
    "application": False,
}
