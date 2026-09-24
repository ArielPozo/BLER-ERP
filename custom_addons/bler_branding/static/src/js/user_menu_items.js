/** @odoo-module **/

import { registry } from "@web/core/registry";
// Se importa para garantizar que los ítems del núcleo ya estén registrados.
import "@web/webclient/user_menu/user_menu_items";

// Quitar del menú de usuario los enlaces que llevan a odoo.com.
// Se conservan Atajos, Preferencias, Instalar app, Modo oscuro (web_dark_mode)
// y Cerrar sesión.
const userMenuItems = registry.category("user_menuitems");
for (const key of ["documentation", "support", "odoo_account"]) {
    if (userMenuItems.contains(key)) {
        userMenuItems.remove(key);
    }
}
