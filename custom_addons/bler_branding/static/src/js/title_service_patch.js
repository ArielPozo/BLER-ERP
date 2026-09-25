/** @odoo-module **/

import { titleService } from "@web/core/browser/title_service";
import { patch } from "@web/core/utils/patch";

export const BRAND_NAME = "BLER ERP";

/**
 * El servicio de título del núcleo usa "Odoo" cuando no hay ninguna parte de
 * título (por ejemplo, en la pantalla de inicio). Se envuelven setParts y
 * setCounters para usar "BLER ERP" en ese caso, sin copiar el servicio.
 */
patch(titleService, {
    start() {
        const service = super.start(...arguments);
        const { setParts, setCounters } = service;
        const applyBrand = () => {
            if (!Object.keys(service.getParts()).length) {
                document.title = document.title.replace(/Odoo$/, BRAND_NAME);
            }
        };
        service.setParts = (parts) => {
            setParts(parts);
            applyBrand();
        };
        service.setCounters = (counters) => {
            setCounters(counters);
            applyBrand();
        };
        return service;
    },
});
