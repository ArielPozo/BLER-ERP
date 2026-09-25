# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this workspace is

**BLER ERP** (formerly "Taller EC"): an Odoo 18 **Community** deployment for an Ecuadorian auto-repair shop. Repo: https://github.com/ArielPozo/BLER-ERP (public). `.gitignore` keeps the cloned references and DB backups out of it. See `rebranding.md` for the naming and licensing rules (Odoo is LGPL-3; "Odoo" is a trademark).

| Path | Role | Ours? |
|---|---|---|
| `odoo_stack/` | Docker Compose stack (Odoo 18 + Postgres 16), `odoo.conf`, DB backups | Yes |
| `custom_addons/taller_ec_flota/` | Our module: links `fleet.vehicle` to `repair.order`, menu restrictions | Yes |
| `custom_addons/bler_branding/` | Our module: BLER ERP brand in the UI (tab title, favicon/PWA icons, login and portal footer, user menu without odoo.com links). Logo/icons in `static/src/img/` are exported from `brand/` | Yes |
| `custom_addons/bler_taller/` | Our module: workshop features from `lista_necesarios.txt` (service lines on repairs, services/parts catalog, calendar, OWL dashboard, work-order and vehicle PDFs, customer↔vehicle, portal `/my/vehiculos`, maintenance reminder cron). Depends on `taller_ec_flota` | Yes |
| `brand/` | Logo sources (SVG), PNG exports, palette and brand notes (`brand/README.md`) | Yes |
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
- **Backend UI comes from third-party addons only.** `muk_web_theme` (with `muk_web_appsbar`/`colors`/`chatter`/`dialog`) supplies the sidebar and brand colors (Settings → General → Branding). `web_dark_mode` adds a per-user "Dark Mode" toggle in the user menu. `web_responsive` is vendored but **uninstalled**, because it conflicts with MuK's app menu. `taller_ec_flota` ships only small fixes in `static/src/scss/` (currently `chatter.scss`, which wraps the chatter topbar buttons instead of showing a horizontal scrollbar in MuK's side chatter). Don't add CSS that restyles `.o_main_navbar`, because it fights MuK's appsbar (the one exception is `bler_branding`'s dark-mode bottom border, below).
- **Branding lives only in `bler_branding`.** The login (and reset-password/signup, same `web.login_layout`) is dark: body class `o_bler_login`, `bg-100` removed from the card, dark logo `static/src/img/bler_logo_dark.png`, styles in `static/src/scss/login.scss` (frontend bundle; the HTML editor's `:where(.card) .card-body` rules need the `!important`/extra specificity there). SCSS-only changes need an Odoo restart to rebuild the bundle. `bler_branding` also patches MuK's `AppsBar` (`static/src/webclient/appsbar/`) to add a company-logo card above the sidebar menu (favicon when the sidebar is narrow; its white background can be turned off per company: `res.company.bler_logo_card_transparent`, "Marca" tab of the company form, sent to the client through `ir.http.session_info`), and in dark mode shows the *light-mode* MuK brand/primary colors as a bottom line on the navbar, `.btn-primary` and the current statusbar step: `brand_colors_capture.scss` saves `$mk_color_brand`/`$mk_color_primary` into `$bler-light-*` right after `colors_light.scss` (which the dark bundle also includes, customized or not) and `brand_accents.dark.scss` (in `web.assets_web_dark`) uses them. It inherits `web.layout`, `web.webclient_bootstrap`, `web.login_layout`, `web.brand_promotion`, `portal.portal_record_sidebar` and `mail.discuss_public_channel_template`, patches `titleService` (default title) and removes the `documentation`, `support` and `odoo_account` entries from the `user_menuitems` registry. `muk_web_theme` overrides the favicon with `res.company.favicon`, so `bler_branding`'s post-init hook swaps that field only while it still holds Odoo's default favicon. It also rebrands dialog titles (`static/src/js/brand.js` `rebrand()`: replaces "Odoo" in already-translated text, skipping "Odoo.com"/"Odoo Enterprise"; applied through a `brandedTitle` getter in `web.Dialog.header`) and email footers (QWeb mail views inherited in `views/mail_templates.xml`). Stored `mail.template` records are the one exception to not editing other modules' data: `_rebrand_mail_templates` in `__init__.py` rewrites subject/body of the templates listed in `MAIL_TEMPLATES_TO_REBRAND` for every installed language, run from the post-init hook and `migrations/18.0.1.2.0`. Bump the version and add a migration when that list changes. Don't rename OdooBot or edit other data records.
- **Menu visibility for the mechanic user.** `taller_ec_flota/security/taller_security.xml` defines `group_taller_full_menus` (admin/root only). `views/menus.xml` restricts Dashboard, Discuss and Apps to that group and renames Fleet to "Vehículos". The `mecanica` user lacks the group on purpose.
- **Workshop flow (`bler_taller`).** Parts stay as core `repair.order.move_ids` (stock); services (labour) live in `repair.service.line`, which syncs itself to the linked `sale.order` lines (create/write/unlink). The invoice is always a separate document: repair → quotation → confirmed SO → invoice (`action_taller_invoice`). On `action_repair_done` the intake odometer and next-service date/km are copied to `fleet.vehicle`. `fleet.fleet_group_user` only sees vehicles where the user is the driver, so `bler_taller/security` adds access rights and an always-true `ir.rule` on `fleet.vehicle`/odometer for `stock.group_stock_user` (the mechanic). Creating/editing products is opt-in per user via `bler_taller.group_taller_catalog` (Settings → Users → Permissions → "Catálogo del taller", under Inventory). Brand icons come from the vendored `car-makes-icons` font (MIT, same library CarCare uses) in `bler_taller/static/lib/car-makes-icons/`: use `<i class="o_car_make car-<make>"/>` (our trimmed CSS scopes the font to `.o_car_make`), or the `car_make_icon` field widget on `fleet.vehicle.model.brand.icon_class` / `fleet.vehicle.brand_icon_class`. Name→icon matching and aliases are in `models/fleet_vehicle_model_brand.py`; brands without an image get a color PNG from `static/src/img/brands/` (car-logos-dataset thumbnails; `EXTRA_BRANDS` also creates the Ecuador-market brands Flota lacks, deduplicated by normalized name) or, failing that, the font's SVG. The widget falls back to the brand logo via `options="{'logo_field': ...}"`. Its simplified vehicle form has priority 5, so it replaces Fleet's form everywhere. Portal controllers read with `sudo()` filtered by `_taller_portal_domain` (driver `child_of` the user's commercial partner).
- **Vehicle ↔ repair link.** `repair.order.vehicle_id` onchange pre-fills `partner_id` from `fleet.vehicle.driver_id`. The vehicle form gets a counter button (`action_view_repair_orders`) for per-plate history.

## Conventions

- UI strings, comments and docs are in Spanish; the DB language is `es_419`.
- Our modules use version `18.0.x.y.z`, license LGPL-3, author "BLER ERP". Third-party modules keep their own `license` and `author`; there is no root `LICENSE` on purpose (see `rebranding.md`).
