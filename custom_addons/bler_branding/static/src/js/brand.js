/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";

export const BRAND_NAME = "BLER ERP";

// "Odoo" como nombre del producto. Se excluyen "Odoo.com" y "Odoo Enterprise",
// que nombran servicios y productos de Odoo S.A., no esta instalación.
const PRODUCT_NAME = /\bOdoo\b(?!\.com|\s+Enterprise)/g;

/**
 * Reemplaza "Odoo" por "BLER ERP" en un texto ya traducido, por ejemplo
 * "Error de servidor de Odoo" → "Error de servidor de BLER ERP".
 */
export function rebrand(text) {
    if (text === undefined || text === null) {
        return text;
    }
    return String(text).replace(PRODUCT_NAME, BRAND_NAME);
}

/**
 * Como _t, pero con la marca aplicada. Es perezoso igual que las cadenas de
 * _t: la traducción se resuelve al mostrarse, no al cargar el módulo.
 */
class LazyBrandedString extends String {
    constructor(term) {
        super(term);
        this.term = term;
    }
    valueOf() {
        return rebrand(_t(this.term));
    }
    toString() {
        return this.valueOf();
    }
}

export function brandedT(term) {
    return new LazyBrandedString(term);
}
