/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { ErrorDialog, SessionExpiredDialog } from "@web/core/errors/error_dialogs";
import { patch } from "@web/core/utils/patch";
import { BRAND_NAME, brandedT, rebrand } from "./brand";

// Título por defecto de cualquier diálogo que no defina uno ("Odoo").
Dialog.defaultProps = { ...Dialog.defaultProps, title: BRAND_NAME };

// Encabezado de todos los diálogos: "Error de servidor de Odoo",
// "Advertencia de Odoo", "Expiró la sesión de Odoo", etc. Lo usa la plantilla
// web.Dialog.header (ver static/src/xml/dialogs.xml).
patch(Dialog.prototype, {
    get brandedTitle() {
        return rebrand(this.props.title);
    },
});

// Título repetido dentro de "Ver detalles técnicos" de los diálogos de error.
patch(ErrorDialog.prototype, {
    get brandedErrorTitle() {
        return rebrand(this.title || this.constructor.title);
    },
});

// Cuerpo del diálogo de sesión expirada.
patch(SessionExpiredDialog.prototype, {
    get brandedMessage() {
        return brandedT("Your Odoo session expired. The current page is about to be refreshed.");
    },
});
