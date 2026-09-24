# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this workspace is

**BLER ERP** (formerly "Taller EC"): an Odoo 18 **Community** deployment for an Ecuadorian auto-repair shop. Repo: https://github.com/ArielPozo/BLER-ERP (public). `.gitignore` keeps the cloned references and DB backups out of it. See `rebranding.md` for the naming and licensing rules (Odoo is LGPL-3; "Odoo" is a trademark).

| Path | Role | Ours? |
|---|---|---|
| `odoo_stack/` | Docker Compose stack (Odoo 18 + Postgres 16), `odoo.conf`, DB backups | Yes |
| `custom_addons/taller_ec_flota/` | Our module: links `fleet.vehicle` to `repair.order`, menu restrictions | Yes |
| `custom_addons/muk_web_*`, `web_dark_mode`, `web_responsive` | Third-party UI addons vendored from `muk-it/odoo-modules` and `OCA/web` (branch 18.0). Don't edit; re-copy from upstream to update | No |
| `odoo_ec_addons/` | Vendored copy of `somatechlat/odoo_saas_ecuador` (commit in `VENDORED.md`): Ecuador SRI localization (`l10n_ec_*`) | No (vendored) |
| `odoo/` | Clone of Odoo 18.0 source, for reading core code only. The container uses the `odoo:18` image, not this. Git-ignored | No |
| `carcare/`, `repairos/` | Other workshop apps (.NET/Vue and Python) used only as feature references; `lista_necesarios.txt` lists which of their features to reproduce in Odoo. Git-ignored | No |

## Stack and commands

Run from `C:\proyectos\Taller`. In Git Bash, prefix `docker compose run` with `MSYS_NO_PATHCONV=1`, or `/etc/odoo/odoo.conf` gets rewritten to a Windows path.

```bash
# Start / rebuild (image adds zeep, cryptography, lxml for SRI signing)
docker compose -f odoo_stack/docker-compose.yml up -d --build
# UI: http://localhost:8069  (master password: admin). Working DB: taller_ec

# Install or upgrade a module (stop the web service first so the registry reloads cleanly)
docker compose -f odoo_stack/docker-compose.yml stop odoo
MSYS_NO_PATHCONV=1 docker compose -f odoo_stack/docker-compose.yml run --rm -T odoo \
  odoo -c /etc/odoo/odoo.conf -d taller_ec -u taller_ec_flota --stop-after-init --no-http
docker compose -f odoo_stack/docker-compose.yml start odoo

# Odoo shell (pipe Python on stdin)
MSYS_NO_PATHCONV=1 docker compose -f odoo_stack/docker-compose.yml run --rm -T odoo \
  odoo shell -c /etc/odoo/odoo.conf -d taller_ec --no-http

# Run a module's tests (use a throwaway DB, not taller_ec)
MSYS_NO_PATHCONV=1 docker compose -f odoo_stack/docker-compose.yml run --rm -T odoo \
  odoo -c /etc/odoo/odoo.conf -d test_taller -i taller_ec_flota --test-enable \
  --test-tags /taller_ec_flota --stop-after-init --no-http
# Single test class/method: --test-tags /module:ClassName.test_method

# Query the DB directly
docker exec odoo_stack-db-1 psql -U odoo -d taller_ec -c "select name,state from ir_module_module where name like 'muk%'"

# Backup before risky DB changes (convention: odoo_stack/backups/<db>_antes_<cambio>_<fecha>.dump)
docker exec odoo_stack-db-1 pg_dump -U odoo -Fc taller_ec > odoo_stack/backups/taller_ec_antes_X_YYYY-MM-DD.dump
```

Addon folders are mounted read-only into the container (`../odoo_ec_addons` → `/mnt/extra-addons`, `../custom_addons` → `/mnt/custom-addons`). Python/XML changes need a `-u <module>` upgrade. New modules need "Update Apps List" or `-i`.

## Things that span several files

- **addons_path order matters** (`odoo_stack/config/odoo.conf`): core addons come first, so core `l10n_ec` shadows Somatech's `odoo_ec_addons/l10n_ec`. Somatech's other modules have unique names (`l10n_ec_base`, `l10n_ec_edi` are installed). Don't reorder the path without checking for name collisions.
- **Localization tests live inside each module** (`l10n_ec_base/tests`, `l10n_ec_sri/tests`, …). The upstream repo also shipped a root-level `odoo_ec_addons/tests/`. We deleted it because it was outside any module (never discovered), mostly tautological, and its real tests failed on invalid sample RUC/cédula numbers. Keep it deleted when re-vendoring from upstream.
- **Backend UI comes from third-party addons only.** `muk_web_theme` (with `muk_web_appsbar`/`colors`/`chatter`/`dialog`) supplies the sidebar and brand colors (Settings → General → Branding). `web_dark_mode` adds a per-user "Dark Mode" toggle in the user menu. `web_responsive` is vendored but **uninstalled**, because it conflicts with MuK's app menu. `taller_ec_flota` ships only small fixes in `static/src/scss/` (currently `chatter.scss`, which wraps the chatter topbar buttons instead of showing a horizontal scrollbar in MuK's side chatter). Don't add CSS that restyles `.o_main_navbar`, because it fights MuK's appsbar.
- **Menu visibility for the mechanic user.** `taller_ec_flota/security/taller_security.xml` defines `group_taller_full_menus` (admin/root only). `views/menus.xml` restricts Dashboard, Discuss and Apps to that group and renames Fleet to "Vehículos". The `mecanica` user lacks the group on purpose.
- **Vehicle ↔ repair link.** `repair.order.vehicle_id` onchange pre-fills `partner_id` from `fleet.vehicle.driver_id`. The vehicle form gets a counter button (`action_view_repair_orders`) for per-plate history.

## Conventions

- UI strings, comments and docs are in Spanish; the DB language is `es_419`.
- Our modules use version `18.0.x.y.z`, license LGPL-3, author "Taller EC".
