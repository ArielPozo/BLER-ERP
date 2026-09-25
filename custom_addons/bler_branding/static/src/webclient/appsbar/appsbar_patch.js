/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { url } from "@web/core/utils/urls";
import { AppsBar } from "@muk_web_appsbar/webclient/appsbar/appsbar";

// Tarjeta con el logo de la compañía arriba del menú de la barra lateral.
// Con la barra angosta se muestra el ícono (favicon) de la compañía.
patch(AppsBar.prototype, {
    setup() {
        super.setup();
        const companyId = this.companyService.currentCompany.id;
        this.companyLogoUrl = url("/web/binary/company_logo", { company: companyId });
        this.companyIconUrl = url("/web/image", {
            model: "res.company",
            field: "favicon",
            id: companyId,
        });
        this.companyName = this.companyService.currentCompany.name;
        // Opción de la compañía (pestaña Marca), enviada en session_info.
        this.companyCardTransparent = Boolean(
            this.companyService.currentCompany.bler_logo_card_transparent
        );
    },
});
