# -*- coding: utf-8 -*-
# Paso 1 de la creación de la demo (se ejecuta con `odoo shell` sobre una base
# que solo tiene `base`). Deja la empresa en Ecuador y en dólares antes de
# instalar Contabilidad, para que Odoo cargue el plan de cuentas ecuatoriano
# (l10n_ec, IVA 15%) en vez del genérico.

company = env.company
ecuador = env.ref("base.ec")
usd = env.ref("base.USD")
usd.active = True

company.write({
    "name": "Taller Demo BLER",
    "currency_id": usd.id,
})
company.partner_id.write({
    "country_id": ecuador.id,
    "city": "Quito",
    "street": "Av. de los Shyris N35-12",
    "phone": "+593 2 600 0000",
    "email": "taller@demo.bler.ec",
    "tz": "America/Guayaquil",
})

admin = env.ref("base.user_admin")
admin.write({
    "name": "Administrador",
    "login": "admin",
    "password": "admin",
    "lang": "es_419",
    "tz": "America/Guayaquil",
})
env["res.lang"]._activate_lang("es_419")
env["ir.default"].set("res.partner", "lang", "es_419")
env.cr.commit()
print("Empresa demo configurada")
