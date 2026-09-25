# Rebranding: de "Taller EC / Odoo" a BLER ERP

Notas sobre el cambio de nombre del proyecto a **BLER ERP**: qué permiten las licencias, qué no, y qué falta hacer. No es asesoría legal; ante una duda concreta, consultar con un abogado.

## Licencia real de cada componente

La licencia de Odoo 18 Community es la **LGPL-3**, no la GPL-3.0. Lo declara `odoo/release.py` (`license = 'LGPL-3'`), y cada módulo lo repite en su `__manifest__.py`.

| Componente | Origen | Licencia |
|---|---|---|
| Núcleo de Odoo 18 Community (imagen Docker `odoo:18`) | Odoo S.A. | LGPL-3 |
| `custom_addons/bler_branding`, `custom_addons/taller_ec_flota` | Propio | LGPL-3 |
| `custom_addons/muk_web_*` | MuK IT (`muk-it/odoo-modules`) | LGPL-3 |
| `custom_addons/web_dark_mode` | OCA (`OCA/web`) | **AGPL-3** |
| `custom_addons/web_responsive` | OCA (`OCA/web`) | LGPL-3 (según su `__manifest__.py`) |
| `odoo_ec_addons/l10n_ec_*` | Somatech (`somatechlat/odoo_saas_ecuador`) | LGPL-3 |

Si el repositorio se publica bajo GPL-3.0, las dos licencias son compatibles:

- El código LGPL-3 (lo propio, MuK y Somatech) se puede redistribuir bajo GPL-3.0; la sección 2 de la LGPL-3 lo permite.
- El módulo AGPL-3 de OCA (`web_dark_mode`) **no** se pueden relicenciar a GPL-3.0, pero sí pueden convivir en el mismo repositorio conservando su licencia (sección 13 de la GPL-3.0).

Por eso cada módulo mantiene su propio `license` en el manifest. Si se añade un `LICENSE` en la raíz, debe aclarar que rige solo para lo que no tenga una licencia propia.

## Lo que sí se puede hacer

- **Llamar al producto "BLER ERP"** y usar su propio logo, colores y dominio.
- **Describirlo como "basado en Odoo Community"**. Es un uso descriptivo del nombre, no se presenta como producto de Odoo S.A.
- **Cambiar la marca visible en la interfaz** mediante un módulo propio (por ejemplo `bler_branding`) que herede plantillas y vistas, sin tocar el núcleo:
  - el título de la pestaña del navegador (`<title t-esc="title or 'Odoo'"/>` en `web/views/webclient_templates.xml`, y `title_service.js`);
  - el favicon y el logo de la pantalla de inicio de sesión;
  - el pie "Powered by Odoo" del login y del portal;
  - los enlaces del menú de usuario que llevan a odoo.com (Documentación, Soporte, "Mi cuenta de Odoo.com");
  - el texto "Your logo" de la barra lateral de MuK (se reemplaza subiendo el logo en Ajustes).
- **Modificar y redistribuir el código**, incluso cobrando por el servicio, siempre que se cumplan las obligaciones siguientes.

## Lo que hay que respetar

- **Avisos de copyright y licencia.** No se borran las cabeceras, los archivos `LICENSE` ni `COPYRIGHT` de Odoo, MuK, OCA ni Somatech. Tampoco se cambia el campo `author` de módulos que no son nuestros.
- **La marca "Odoo".** Es una marca registrada de Odoo S.A. y las licencias de software no dan derechos sobre marcas; la GPL-3/LGPL-3 lo deja explícito en la sección 7(e). No usar "Odoo" ni su logo en el nombre del producto, el logo, el dominio ni la publicidad. Lo mismo aplica a la marca "OCA".
- **Código fuente de lo modificado.**
  - Si se distribuye una versión modificada de algo LGPL-3 (por ejemplo, un parche al núcleo), hay que ofrecer el código fuente de esa modificación bajo LGPL-3.
  - El módulo AGPL-3 (`web_dark_mode`) tiene una obligación adicional: si se modifica y BLER ERP se ofrece como servicio por red, hay que dar a los usuarios acceso al código fuente modificado. Sin modificaciones, basta con conservar la licencia.
- **Nada de Odoo Enterprise.** Los módulos Enterprise tienen licencia propietaria (OEEL) y no pueden incluirse ni imitarse copiando su código.

## Cambio de nombres técnicos

Renombrar el nombre técnico de un módulo **ya instalado** (por ejemplo `taller_ec_flota` → `bler_flota`) no es solo renombrar la carpeta:

- Odoo lo trata como un módulo nuevo.
- Los `xml_id` (`taller_ec_flota.group_taller_full_menus`, etc.) y los datos que dependen de ellos quedan huérfanos.

Hay dos caminos:

- Mantener el nombre técnico actual y cambiar solo `name` y `author` en el manifest.
- Crear el módulo nuevo con un script de migración que reasigne los `ir_model_data`. Probarlo antes en una copia de la base.

## Pendiente

- [x] Licencia de la raíz del repositorio: **resuelto sin `LICENSE` en la raíz**. Por decisión del propietario, cada componente conserva exactamente la licencia de su proyecto y módulo de origen (campo `license` de cada `__manifest__.py`, archivos `LICENSE`/`COPYRIGHT` y cabeceras). No se cambia la licencia ni el `author` de módulos de terceros. El `README.md` resume las licencias por componente.
- [x] Crear el módulo `bler_branding` (título de la pestaña, favicon e íconos PWA, pie del login y del portal, menú de usuario). El logo y los íconos son provisionales: reemplazar los archivos de `bler_branding/static/src/img/` y `static/description/icon.png` conservando los nombres.
- [x] Cambiar `author` a "BLER ERP" solo en módulos propios (`taller_ec_flota`, `bler_branding`).
- [x] Revisar textos que digan "Taller EC" en vistas y menús (`taller_ec_flota`: nombre del módulo y del grupo "BLER ERP: menús completos"). El nombre técnico `taller_ec_flota` se mantiene.
- [x] Añadir un `README.md` que diga "BLER ERP, basado en Odoo 18 Community", con créditos a Odoo S.A., MuK IT, OCA y Somatech.
- [ ] Subir el logo oficial de BLER ERP como logo de la compañía (Ajustes → Compañías) y en Ajustes → Marca de MuK (reemplaza "Your logo" de la barra lateral). Mientras tanto se puede usar `bler_branding/static/src/img/bler_logo_placeholder.png`.
- [x] Textos con "Odoo" en diálogos y correos (`bler_branding` 18.0.1.2.0):
  - Diálogos: título por defecto y encabezados ("Error de servidor de BLER ERP", "Advertencia de BLER ERP", "Expiró la sesión de BLER ERP") y el aviso de sesión expirada de las páginas públicas. Se reemplaza "Odoo" sobre el texto ya traducido; "Odoo.com" y "Odoo Enterprise" se dejan porque nombran servicios de Odoo S.A.
  - Correos QWeb (notificaciones, restablecer contraseña, alerta de nuevo dispositivo, resumen periódico): sin "Powered by Odoo". Se conservan "Unfollow" y el enlace para darse de baja del resumen, que queda como "Sent by BLER ERP".
  - Correos guardados en la base (`mail.template`): invitación (sin el párrafo promocional ni el "Odoo Tour"), cuenta creada, bienvenida al portal y asunto de la invitación a la verificación en dos pasos. Se corrigen en todos los idiomas instalados mediante el `post_init_hook` y una migración. Si se instala un idioma nuevo después, volver a ejecutar la actualización con `-u bler_branding` no basta: hay que llamar a `_rebrand_mail_templates` desde `odoo shell`.
- [ ] Textos con "Odoo" que quedan: el aviso de permiso de cámara del lector de códigos de barras ("Odoo necesita su autorización primero") y el diálogo de mejora a "Odoo Enterprise", que se deja a propósito.
