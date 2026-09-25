# BLER ERP

**BLER ERP, basado en Odoo 18 Community.** Sistema de gestión para un taller mecánico de Ecuador: órdenes de reparación ligadas a los vehículos de los clientes, inventario, facturación y facturación electrónica del SRI.

BLER ERP es un proyecto independiente. No es un producto de Odoo S.A. ni está respaldado por ella; "Odoo" es una marca registrada de Odoo S.A. y aquí se menciona solo para describir la base técnica. Ver [`rebranding.md`](rebranding.md) para las reglas de marca y licencias.

## Contenido del repositorio

| Ruta | Contenido |
|---|---|
| `odoo_stack/` | Stack de Docker Compose (Odoo 18 + PostgreSQL 16), `Dockerfile` (añade `zeep`, `cryptography` y `lxml` para la firma del SRI) y `config/odoo.conf` |
| `custom_addons/bler_branding/` | Módulo propio: marca BLER ERP en la interfaz (título de la pestaña, favicon, login, portal, menú de usuario) |
| `custom_addons/taller_ec_flota/` | Módulo propio: liga el vehículo (`fleet.vehicle`) a la orden de reparación (`repair.order`), historial por placa y restricción de menús para el usuario mecánico |
| `custom_addons/muk_web_*` | Tema del backend de MuK IT (barra lateral de apps, colores, chatter, diálogos). Copia sin modificar de `muk-it/odoo-modules` (rama 18.0) |
| `custom_addons/web_dark_mode`, `web_responsive` | Módulos de OCA (`OCA/web`, rama 18.0). `web_responsive` está incluido pero no instalado |
| `odoo_ec_addons/` | Localización ecuatoriana del SRI (`l10n_ec_*`) de Somatech (`somatechlat/odoo_saas_ecuador`). Ver `odoo_ec_addons/VENDORED.md` |
| `rebranding.md` | Notas sobre el cambio de nombre a BLER ERP, licencias y marca |

Los logos e íconos de `custom_addons/bler_branding/static/src/img/` son **provisionales**. Para cambiarlos, reemplazar los archivos conservando sus nombres y actualizar el módulo.

## Cómo ejecutarlo

Requisitos: Docker con Docker Compose. Los comandos se ejecutan desde la raíz del repositorio. En Git Bash (Windows), anteponer `MSYS_NO_PATHCONV=1` a los `docker compose run`, o la ruta `/etc/odoo/odoo.conf` se convierte en una ruta de Windows.

```bash
# Levantar (o reconstruir) el stack
docker compose -f odoo_stack/docker-compose.yml up -d --build
# Interfaz: http://localhost:8069  (contraseña maestra: admin)

# Instalar o actualizar un módulo (detener antes el servicio web)
docker compose -f odoo_stack/docker-compose.yml stop odoo
MSYS_NO_PATHCONV=1 docker compose -f odoo_stack/docker-compose.yml run --rm -T odoo \
  odoo -c /etc/odoo/odoo.conf -d taller_ec -i bler_branding -u taller_ec_flota --stop-after-init --no-http
docker compose -f odoo_stack/docker-compose.yml start odoo

# Consola de Odoo (enviar el código Python por stdin)
MSYS_NO_PATHCONV=1 docker compose -f odoo_stack/docker-compose.yml run --rm -T odoo \
  odoo shell -c /etc/odoo/odoo.conf -d taller_ec --no-http

# Pruebas de un módulo (usar una base desechable, no taller_ec)
MSYS_NO_PATHCONV=1 docker compose -f odoo_stack/docker-compose.yml run --rm -T odoo \
  odoo -c /etc/odoo/odoo.conf -d test_taller -i taller_ec_flota --test-enable \
  --test-tags /taller_ec_flota --stop-after-init --no-http

# Respaldo antes de cambios riesgosos en la base
docker exec odoo_stack-db-1 pg_dump -U odoo -Fc taller_ec > odoo_stack/backups/taller_ec_antes_X_AAAA-MM-DD.dump
```

Las carpetas de módulos se montan en el contenedor en solo lectura. Los cambios en Python o XML requieren actualizar el módulo (`-u <módulo>`); los módulos nuevos requieren "Actualizar lista de aplicaciones" o `-i`.

## Créditos y licencias

Cada componente conserva la licencia de su proyecto de origen, declarada en el campo `license` de su `__manifest__.py` y en sus propios archivos de licencia. El repositorio no tiene una licencia única en la raíz.

| Componente | Autor | Licencia |
|---|---|---|
| Odoo 18 Community (imagen Docker `odoo:18`) | Odoo S.A. | LGPL-3 |
| `muk_web_theme`, `muk_web_appsbar`, `muk_web_colors`, `muk_web_chatter`, `muk_web_dialog` | MuK IT | LGPL-3 |
| `web_dark_mode` | Odoo Community Association (OCA) | AGPL-3 |
| `web_responsive` | Odoo Community Association (OCA) | LGPL-3 |
| `odoo_ec_addons/` (`l10n_ec_*`) | Somatech | LGPL-3 |
| `bler_branding`, `taller_ec_flota` | BLER ERP | LGPL-3 |
