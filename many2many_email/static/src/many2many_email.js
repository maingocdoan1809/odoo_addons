/* @odoo-module */

import { fieldMany2ManyTagsEmail, FieldMany2ManyTagsEmail } from "@mail/views/web/fields/many2many_tags_email/many2many_tags_email"
import { markRaw, useEffect, useState } from "@odoo/owl";
import { AutoComplete } from "@web/core/autocomplete/autocomplete";
import { registry } from "@web/core/registry";
import { getId } from "@web/model/relational_model/utils";
import { Many2XAutocomplete } from "@web/views/fields/relational_utils";


export class AutoCompleteEmail extends AutoComplete {
    setup() {
        super.setup()
    }
    selectOption(indices, params = {}) {
        const option = this.sources[indices[0]].options[indices[1]];
        this.inEdition = false;
        if (option.unselectable) {
            const inputValue = this.inputRef.el.value
            option.value = getId('virtual')
            option.displayName = inputValue
            option.label = inputValue
        }

        if (this.props.resetOnSelect) {
            this.inputRef.el.value = "";
        }

        this.forceValFromProp = true;
        this.props.onSelect(option, {
            ...params,
            input: this.inputRef.el,
        });
        this.close();
    }
}

export class Many2XAutocompleteEmail extends Many2XAutocomplete {
    static components = {
        ...Many2XAutocomplete.components,
        AutoComplete: AutoCompleteEmail
    }
}

export class Many2ManyEmail extends FieldMany2ManyTagsEmail {
    static components = {
        ...FieldMany2ManyTagsEmail.components,
        Many2XAutocomplete: Many2XAutocompleteEmail
    }
    setup() {
        super.setup()
        this.virtualRecord = useState({
            records: []
        })

        const update = this.update

        this.update = async (recordlist) => {
            
            if (!recordlist) {
                return;
            }
            const actualRecord = []
            if (Array.isArray(recordlist)) {
                for(let record of recordlist) {
                    if((typeof record.id === 'string') && record.id.startsWith(`virtual`)) {
                        
                        if (!this.validateEmail(record.display_name)) {
                            return
                        }

                        const list = this.props.record.data[this.props.name]
                        
                        for(let k of Object.values(list.activeFields)) {
                            k.forceSave = true
                        }
                        
                        const newDatapoint = list._createRecordDatapoint({
                            email: record.display_name,
                            name: record.display_name,
                            display_name: record.display_name
                        }, {
                            virtualId: record.id,
                            activeFields: list.activeFields,
                            mode: 'readonly',
                            context: list.context
                        })
                        
                        list._addRecord(newDatapoint)
                        this.virtualRecord.records.push(record)

                    } else {
                        actualRecord.push(record)
                    }
                }
            } else {
                actualRecord.push(recordlist)
            }
            if (actualRecord.length > 0) {
                return await update(actualRecord)
            }
        };

    }

    validateEmail(email) {
        const re =
            /^([a-z0-9][-a-z0-9_+.]*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,63}(?:\.[a-z]{2})?)$/i;
        return re.test(email);
    }

    async deleteTag(id) {
        const tagRecord = this.props.record.data[this.props.name].records.find(
            (record) => record.id === id
        );

        if (this.virtualRecord.records.map((r) => r.id).includes(tagRecord._virtualId)) {
            
            this.virtualRecord.records = this.virtualRecord.records.filter((r) => r.id != tagRecord._virtualId)
            return await this.props.record.data[this.props.name].delete(tagRecord);
        }
        return await this.props.record.data[this.props.name].forget(tagRecord);
    }
}

registry.category("fields").add("many2many_email", {
    ...fieldMany2ManyTagsEmail,
    component: Many2ManyEmail,
    extractProps(args) {
        const props = fieldMany2ManyTagsEmail.extractProps(...arguments);
        props.canQuickCreate = false
        props.canCreateEdit = false
        return props;
    },
    relatedFields: (fieldInfo) => {
        return [...fieldMany2ManyTagsEmail.relatedFields(fieldInfo), { name: "name", type: "char" }];
    },
});
