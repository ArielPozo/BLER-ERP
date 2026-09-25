# -*- coding: utf-8 -*-
{
    "name": "BLER ERP - Marca",
    "version": "18.0.1.6.0",
    "category": "Hidden",
    "summary": "Marca BLER ERP en la interfaz: título, favicon, login, portal y menú de usuario",
    "description": """
Aplica la marca BLER ERP sin modificar el núcleo, solo heredando plantillas,
controladores y JS:

* Título de la pestaña del navegador "BLER ERP" (cliente web y login).
* Favicon e íconos de la aplicación web (PWA) propios. Con muk_web_theme,
  al instalar se reemplaza el favicon de la compañía solo si aún es el de
  Odoo por defecto.
* Login con fondo oscuro (índigo noche) y el logo para fondo oscuro.
* Tarjeta con el logo de la compañía arriba del menú de la barra lateral
  (MuK); con la barra angosta, el ícono de la compañía. El fondo blanco de
  la tarjeta se puede quitar en la ficha de la compañía (pestaña Marca).
* Modo oscuro: los colores de marca del modo claro (Ajustes, colores de MuK)
  aparecen como línea inferior en la barra superior, los botones principales
  y el paso actual de la barra de estado.
* Quita "Powered by Odoo" del login y del portal.
* Quita del menú de usuario los enlaces a odoo.com (Documentación, Soporte,
  "Mi cuenta de Odoo.com").
* Cambia "Odoo" por "BLER ERP" en los títulos de los diálogos ("Error de
  servidor de Odoo", "Advertencia de Odoo", "Expiró la sesión de Odoo"...).
  "Odoo.com" y "Odoo Enterprise" no se cambian.
* Quita "Powered by Odoo" de los correos (notificaciones, contraseña,
  alerta de nuevo dispositivo, resumen periódico, invitación al portal).

Los logos e íconos de static/src/img salen de la carpeta brand/ del
repositorio (fuente en SVG). Para cambiarlos, reemplazar los archivos
conservando los nombres.
    """,
    "author": "BLER ERP",
    "license": "LGPL-3",
    # portal ya está instalado en esta implementación (account depende de él);
    # auth_signup y digest también (dependencias de portal y mail/account).
    # muk_web_appsbar/colors/theme: barra lateral, colores de marca y campo
    # favicon de la compañía que se usan en la tarjeta del logo y en el modo oscuro.
    "depends": ["web", "mail", "portal", "auth_signup", "digest",
                "muk_web_appsbar", "muk_web_colors", "muk_web_theme"],
    "data": [
        "views/webclient_templates.xml",
        "views/res_company_views.xml",
        "views/portal_templates.xml",
        "views/discuss_public_templates.xml",
        "views/mail_templates.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            ("before", "muk_web_colors/static/src/scss/colors.scss",
             "bler_branding/static/src/scss/brand_colors_capture.scss"),
        ],
        "web.assets_web_dark": [
            "bler_branding/static/src/scss/brand_accents.dark.scss",
        ],
        "web.assets_backend": [
            "bler_branding/static/src/webclient/appsbar/appsbar_patch.js",
            "bler_branding/static/src/webclient/appsbar/appsbar.xml",
            "bler_branding/static/src/webclient/appsbar/appsbar.scss",
            "bler_branding/static/src/js/brand.js",
            "bler_branding/static/src/js/title_service_patch.js",
            "bler_branding/static/src/js/user_menu_items.js",
            "bler_branding/static/src/js/dialogs_patch.js",
            "bler_branding/static/src/xml/dialogs.xml",
        ],
        "web.assets_frontend": [
            "bler_branding/static/src/scss/login.scss",
            "bler_branding/static/src/js/brand.js",
            "bler_branding/static/src/js/public_error_notifications_patch.js",
        ],
    },
    "post_init_hook": "_post_init_hook",
    "installable": True,
    "application": False,
}
