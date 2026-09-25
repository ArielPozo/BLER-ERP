/** @odoo-module **/

import { registry } from "@web/core/registry";
// Se importa para que las notificaciones del núcleo ya estén registradas.
import "@web/public/error_notifications";
import { brandedT } from "./brand";

// Páginas públicas (portal, login): la sesión expirada se muestra como
// notificación con "Expiró la sesión de Odoo".
const notifications = registry.category("error_notifications");
for (const key of ["odoo.http.SessionExpiredException", "werkzeug.exceptions.Forbidden"]) {
    if (notifications.contains(key)) {
        notifications.add(
            key,
            {
                ...notifications.get(key),
                title: brandedT("Odoo Session Expired"),
                message: brandedT(
                    "Your Odoo session expired. The current page is about to be refreshed."
                ),
            },
            { force: true }
        );
    }
}
