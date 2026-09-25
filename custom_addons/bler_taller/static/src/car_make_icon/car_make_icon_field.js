/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

/**
 * Muestra el ícono de la marca (car-makes-icons) a partir de un campo Char
 * con la clase CSS, p. ej. brand_icon_class = "car-toyota". Si la marca no
 * está en la librería, muestra su logo (opción logo_field: campo Char con la
 * URL de la imagen, que debe estar en la vista).
 */
export class CarMakeIconField extends Component {
    static template = "bler_taller.CarMakeIconField";
    static props = { ...standardFieldProps, logoField: { type: String, optional: true } };

    get iconClass() {
        return this.props.record.data[this.props.name] || "";
    }

    get logoUrl() {
        return (this.props.logoField && this.props.record.data[this.props.logoField]) || "";
    }
}

registry.category("fields").add("car_make_icon", {
    component: CarMakeIconField,
    supportedTypes: ["char"],
    displayName: "Ícono de marca de vehículo",
    supportedOptions: [{ label: "Campo con la URL del logo", name: "logo_field", type: "field" }],
    extractProps: ({ options }) => ({ logoField: options.logo_field }),
});
