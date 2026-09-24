# Rebranding: de "Taller EC / Odoo" a BLER ERP

Notas sobre el cambio de nombre del proyecto a **BLER ERP**: qué permiten las licencias, qué no, y qué falta hacer. No es asesoría legal; ante una duda concreta, consultar con un abogado.

## Licencia real de cada componente

La licencia de Odoo 18 Community es la **LGPL-3**, no la GPL-3.0. Lo declara `odoo/release.py` (`license = 'LGPL-3'`), y cada módulo lo repite en su `__manifest__.py`.

| Componente | Origen | Licencia |
|---|---|---|
| Núcleo de Odoo 18 Community (imagen Docker `odoo:18`) | Odoo S.A. | LGPL-3 |
| `custom_addons/taller_ec_flota` | Propio | LGPL-3 |
| `custom_addons/muk_web_*` | MuK IT (`muk-it/odoo-modules`) | LGPL-3 |
| `custom_addons/web_dark_mode`, `web_responsive` | OCA (`OCA/web`) | **AGPL-3** |
| `odoo_ec_addons/l10n_ec_*` | Somatech (`somatechlat/odoo_saas_ecuador`) | LGPL-3 |

Si el repositorio se publica bajo GPL-3.0, las dos licencias son compatibles:

- El código LGPL-3 (lo propio, MuK y Somatech) se puede redistribuir bajo GPL-3.0; la sección 2 de la LGPL-3 lo permite.
- Los módulos AGPL-3 de OCA **no** se pueden relicenciar a GPL-3.0, pero sí pueden convivir en el mismo repositorio conservando su licencia (sección 13 de la GPL-3.0).

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
  - Los módulos AGPL-3 (`web_dark_mode`, `web_responsive`) tienen una obligación adicional: si se modifican y BLER ERP se ofrece como servicio por red, hay que dar a los usuarios acceso al código fuente modificado. Sin modificaciones, basta con conservar la licencia.
- **Nada de Odoo Enterprise.** Los módulos Enterprise tienen licencia propietaria (OEEL) y no pueden incluirse ni imitarse copiando su código.

## Cambio de nombres técnicos

Renombrar el nombre técnico de un módulo **ya instalado** (por ejemplo `taller_ec_flota` → `bler_flota`) no es solo renombrar la carpeta:

- Odoo lo trata como un módulo nuevo.
- Los `xml_id` (`taller_ec_flota.group_taller_full_menus`, etc.) y los datos que dependen de ellos quedan huérfanos.

Hay dos caminos:

- Mantener el nombre técnico actual y cambiar solo `name` y `author` en el manifest.
- Crear el módulo nuevo con un script de migración que reasigne los `ir_model_data`. Probarlo antes en una copia de la base.

## Pendiente

- [ ] Decidir la licencia de la raíz del repositorio (GPL-3.0 o LGPL-3) y añadir `LICENSE` con la aclaración de licencias por módulo.
- [ ] Crear el módulo `bler_branding` (título, favicon, logo, login, menú de usuario).
- [ ] Cambiar `author` a "BLER ERP" solo en módulos propios (`taller_ec_flota`).
- [ ] Revisar textos que digan "Taller EC" en vistas y menús.
- [ ] Añadir un `README.md` que diga "BLER ERP, basado en Odoo 18 Community", con créditos a MuK IT, OCA y Somatech.
