/** @odoo-module **/

import { useRef } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";
import { SortableDropdownList } from "./sortable_dropdown_list";


patch(ListRenderer.prototype, {

    setup() {
        super.setup()
    },

    get optionalFieldGroups() {
        const propertyGroups = {};
        const optionalFields = [];
        const optionalColumns = this.state.columns.filter(
            (col) => !this.evalColumnInvisible(col.column_invisible)
        );
        for (const col of optionalColumns) {
            const optionalField = {
                label: col.label,
                name: col.name,
                value: this.optionalActiveFields[col.name],
                optional: col.optional
            };
            if (!col.relatedPropertyField) {
                optionalFields.push(optionalField);
            } else {
                const { displayName, id } = col.relatedPropertyField;
                if (propertyGroups[id]) {
                    propertyGroups[id].optionalFields.push(optionalField);
                } else {
                    propertyGroups[id] = { id, displayName, optionalFields: [optionalField] };
                }
            }
        }
        if (optionalFields.length) {
            return [{ optionalFields }, ...Object.values(propertyGroups)];
        }
        return Object.values(propertyGroups);
    },

    get displayOptionalFields() {
        return true;
    },

    onColumnDrop({element, previous, next}) {

        const indexes = [element, previous, next].map(
            (e) =>
                e &&
                Object.values(this.state.columns).findIndex(
                    ({ name }) => name === e.dataset.field_name
                )
        );
        let target;
        if (indexes[0] < indexes[1]) {
            target = previous ? indexes[1] : 0;
        } else {
            target = next ? indexes[2] : this.state.exportList.length - 1;
        }

        this.state.columns.splice(target, 0, this.state.columns.splice(indexes[0], 1)[0]);
    },

})

ListRenderer.components = {
    ...ListRenderer.components,
    SortableDropdownList
}
