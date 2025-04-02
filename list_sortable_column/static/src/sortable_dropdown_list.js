/** @odoo-module **/


import { useRef, onWillUnmount, useEffect, onWillUpdateProps } from "@odoo/owl";
import { useSortable } from "@web/core/utils/sortable_owl";
import { ListRenderer } from "@web/views/list/list_renderer";

const Dropdown = ListRenderer.components.Dropdown

export class SortableDropdownList extends Dropdown {

    static props = {
        ...Dropdown.props,
        onDrop: {type: Function, optional: true}
    }

    setup() {

        super.setup()
        this.menuRef = useRef('menuRef')
        useSortable({
            ref: this.menuRef,
            elements: ".optional_field_item",
            enable: () => true,
            cursor: "grabbing",
            handle: ".o_sort_field",
            // Hooks
            onDrop: async ({ element, previous, next }) => {
                
                if (this.props.onDrop) {
                    this.props.onDrop({element, previous, next})
                }
            },
        });

    }

    onWindowClicked(ev) {

        const activeElement = document.activeElement
        if (this.menuRef.el && this.menuRef.el.contains(activeElement)) {
            return
        }
        return super.onWindowClicked(ev)
    }

}
