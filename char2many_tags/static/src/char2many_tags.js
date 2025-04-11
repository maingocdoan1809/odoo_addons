import { Component, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { TagsList } from "@web/core/tags_list/tags_list";
import { charField, CharField } from "@web/views/fields/char/char_field";
import { useInputField } from "@web/views/fields/input_field_hook";


export class Char2ManyTagsField extends CharField {
    static template = "char2many_tags.Char2ManyTagsField";
    static components = {TagsList}
    setup() {
        super.setup()
        useInputField({
            getValue: () => "",
            parse: (v) => this.parse(v),
        });
    }

    split() {
        const data = this.props.record.data[this.props.name]
        if (data) {
            const _d = data.split(';').filter((r) => r)
            return new Set(_d)
        }
        return new Set()
    }

    parse(value) {
        const val = super.parse(value)
        console.log([...this.split(), val].join(';'));
        
        return [...this.split(), val].join(';')
    }

    async deleteTag(index) {
        if (this.props.readonly) {
            return
        }
        const data = [...this.split()].filter((r, i) => i != index)
        await this.props.record.update({ [this.props.name]: data.join(';') });
        this.props.record.model.bus.trigger("FIELD_IS_DIRTY", true);
    }

    get tags() {
        return [...this.split()].map((record, index) => {
            return {
                id: index, // datapoint_X
                text: record,
                colorIndex: index,
                canEdit: false,
                onDelete: !this.props.readonly ? () => this.deleteTag(index) : undefined,
                onKeydown: (ev) => {
                    console.log("Key down");
                },
            };
        });
    }
}

export const char2ManyTagsField = {
    ...charField,
    component: Char2ManyTagsField,
};

registry.category("fields").add("char2many_tags", char2ManyTagsField);
