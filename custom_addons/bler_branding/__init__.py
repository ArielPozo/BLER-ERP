# -*- coding: utf-8 -*-
import base64
import hashlib
import re

from odoo.tools import file_open

from . import controllers
from . import models

BLER_FAVICON = "bler_branding/static/src/img/favicon.ico"

# SHA-256 de favicons que este módulo instaló antes (el provisional de
# 18.0.1.2.0 y anteriores). Se reemplazan igual que el de Odoo.
OLD_BLER_FAVICONS = {
    "c813109747305f09f0e9ffad1bae3b4dbb4a011877378bb7430c9e28904edb13",
}

BRAND_NAME = "BLER ERP"

# Correos guardados como mail.template (noupdate) que mencionan Odoo en el
# asunto o el cuerpo. Las vistas QWeb de correo se heredan en
# views/mail_templates.xml; estos son datos, así que se corrigen una vez.
MAIL_TEMPLATES_TO_REBRAND = [
    "auth_signup.set_password_email",
    "auth_signup.mail_template_user_signup_account_created",
    "portal.mail_template_data_portal_welcome",
    "auth_totp_mail.mail_template_totp_invite",
]

# "Odoo" como nombre del producto; "Odoo.com" y "Odoo Enterprise" se dejan
# (misma regla que static/src/js/brand.js).
PRODUCT_NAME = re.compile(r"\bOdoo\b(?!\.com|\s+Enterprise)")
TEXT_NODE = re.compile(r">([^<]*)<")

# Invitación (set_password_email): bloque promocional entre el correo de
# inicio de sesión y la firma ("Never heard of Odoo?…", "Odoo Tour",
# "Enjoy Odoo!"), en cualquier idioma.
PROMO_BLOCK = re.compile(
    r"(<a t-attf-href=\"/web/login\?login=[^\"]*\"[^>]*>.*?</a></b><br/><br/>)"
    r"(?:(?!--<br/>).)*?www\.odoo\.com/page/tour(?:(?!--<br/>).)*?"
    r"(\s*--<br/>)",
    re.DOTALL,
)

# La fila completa: <tr><td><table><tr><td>Powered by <a …odoo.com…>Odoo</a>
# </td></tr></table></td></tr>, con el comentario "POWERED BY" que la precede.
# "[^<]*" admite el texto traducido ("Con tecnología de", etc.).
POWERED_BY_ROW = re.compile(
    r"(?:<!--\s*POWERED BY\s*-->\s*)?"
    r"<tr>\s*<td[^>]*>\s*<table[^>]*>\s*<tr>\s*<td[^>]*>\s*[^<]*"
    r"<a[^>]*www\.odoo\.com[^>]*>.*?</a>\s*"
    r"</td>\s*</tr>\s*</table>\s*</td>\s*</tr>",
    re.DOTALL,
)


def _post_init_hook(env):
    _replace_default_favicon(env)
    _rebrand_mail_templates(env)


def _rebrand_body(body):
    body = POWERED_BY_ROW.sub("", body)
    body = PROMO_BLOCK.sub(r"\1\2", body)
    # Solo el texto visible; los atributos (enlaces, t-out…) no se tocan.
    return TEXT_NODE.sub(lambda m: ">" + PRODUCT_NAME.sub(BRAND_NAME, m.group(1)) + "<", body)


def _rebrand_mail_templates(env):
    """En los correos de MAIL_TEMPLATES_TO_REBRAND, y en cada idioma
    instalado: quita la fila "Powered by Odoo" y el bloque promocional de la
    invitación, y cambia "Odoo" por "BLER ERP" en el asunto y el texto.
    Al desinstalar bler_branding no se restaura; si hace falta, restablecer
    la plantilla desde Ajustes → Técnico → Plantillas de correo."""
    langs = [code for code, _name in env["res.lang"].get_installed()]
    for xmlid in MAIL_TEMPLATES_TO_REBRAND:
        template = env.ref(xmlid, raise_if_not_found=False)
        if not template:
            continue
        for lang in langs:
            localized = template.with_context(lang=lang)
            values = {}
            if localized.subject:
                subject = PRODUCT_NAME.sub(BRAND_NAME, localized.subject)
                if subject != localized.subject:
                    values["subject"] = subject
            if localized.body_html:
                body = _rebrand_body(str(localized.body_html))
                if body != str(localized.body_html):
                    values["body_html"] = body
            if values:
                localized.write(values)


def _replace_default_favicon(env):
    """Si muk_web_theme está instalado, el favicon sale del campo
    res.company.favicon, que MuK llena al instalarse con el favicon de Odoo.
    Solo se reemplaza en las compañías que aún tienen ese favicon por defecto
    o uno anterior de BLER ERP (OLD_BLER_FAVICONS); un favicon subido en
    Ajustes → Marca se respeta."""
    Company = env["res.company"].sudo()
    if "favicon" not in Company._fields:
        return
    with file_open("web/static/img/favicon.ico", "rb") as file:
        odoo_favicon = base64.b64encode(file.read())
    with file_open(BLER_FAVICON, "rb") as file:
        bler_favicon = base64.b64encode(file.read())
    for company in Company.with_context(bin_size=False).search([]):
        if not company.favicon or company.favicon == bler_favicon:
            continue
        old_hash = hashlib.sha256(base64.b64decode(company.favicon)).hexdigest()
        if company.favicon == odoo_favicon or old_hash in OLD_BLER_FAVICONS:
            company.favicon = bler_favicon
