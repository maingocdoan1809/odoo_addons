/** @odoo-module **/

import { DomainSelector } from "@web/core/domain_selector/domain_selector";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { TreeEditor, formatValue } from "@web/core/tree_editor/tree_editor";
import { getDomainDisplayedOperators } from "@web/core/domain_selector/domain_selector_operator_editor";
import { TreeEditorRangeTime } from "./tree_editor_range_time";
import { cloneTree, removeVirtualOperators } from "@web/core/tree_editor/condition_tree";
import { deepEqual } from "@web/core/utils/objects";
import { getValueEditorInfo } from "@web/core/tree_editor/tree_editor_value_editors";


export const OPTIONS = [['year', _t('Year')], ['fiscal_year', _t('Fiscal Year')], ['quarter', _t('Quarter')],['month',_t('Month')], ['week', _t('Week')], ['day', _t('Day')]]

export const dateOptions = {
    year: [
        ['current_year', _t('Current Year')],
        ['previous_year', _t('Previous Year')],
        ['previous_2_year', _t('Previous 2 Year')],
        ['3_year_ago', _t('3 Year ago')],
        ['next_year', _t('Next Year')],
        ['current_and_previous_year', _t('Current and Previous Year')],
        ['current_and_next_1_year', _t('Current and Next 1 Year')],
        ['current_and_previous_2_year', _t('Current and Previous 2 Year')]
    ],
    fiscal_year: [
        ['current_fiscal_year', _t('Current Fiscal Year')],
        ['previous_fiscal_year', _t('Previous Fiscal Year')],
        ['previous_2_fiscal_year', _t('Previous 2 Fiscal Year')],
        ['next_fiscal_year', _t('Next Fiscal Year')],
        ['current_and_previous_fiscal_year', _t('Current and Previous Fiscal Year')],
        ['current_and_previous_2_fiscal_year', _t('Current and Previous 2 Fiscal Year')],
        ['current_and_next_fiscal_year', _t('Current and Next Fiscal Year')]
    ],
    quarter: [
        ['current_quarter', _t('Current Quarter')],
        ['previous_quarter', _t('Previous Quarter')],
        ['next_quarter', _t('Next Quarter')],
        ['current_and_previous_quarter', _t('Current and Previous Quarter')],
        ['current_and_next_quarter', _t('Current and Next Quarter')],
        ['current_and_next_3_quarter', _t('Current and Next 3 Quarter')]
    ],
    month: [
        ['this_month', _t('This Month')],
        ['last_month', _t('Last Month')],
        ['next_month', _t('Next Month')],
        ['current_and_previous_month', _t('Current and Previous Month')],
        ['current_and_next_month', _t('Current and Next Month')]
    ],
    week: [
        ['this_week', _t('This Week')],
        ['last_week', _t('Last Week')],
        ['next_week', _t('Next Week')],
        ['current_and_previous_week', _t('Current and Previous Week')],
        ['current_and_next_week', _t('Current and Next Week')]
    ],
    day: [
        ['today', _t('Today')],
        ['yesterday', _t('Yesterday')],
        ['tomorrow', _t('Tomorrow')],
        ['current_and_previous_day', _t('Current and Previous Day')],
        ['current_and_next_day', _t('Current and Next Day')],
        ['last_n_day', _t('Last')],
        ['next_n_day', _t('Next')],
    ]
};


export const extraOperators = OPTIONS.map(pair => pair[0])

patch(TreeEditor.prototype, {
    getValueEditorInfo(node) {

        const fieldDef = this.getFieldDef(node.path);
        if (extraOperators.includes(node.operator) && ['date', 'datetime'].includes(fieldDef.type)) {
            const defaultValue = () => (dateOptions[node.operator][0][0])
            
            return {
                component: TreeEditorRangeTime,
                extractProps: ({value, update}) => {
                    return {
                        update, value, options: dateOptions[node.operator], node,
                        defaultValue, rangeProps: {
                            fieldDef: fieldDef,
                            info: getValueEditorInfo(fieldDef, "between")
                        }
                    }
                },
                defaultValue,
                isSupported: (value) => true // fix me
            }
        }
        return super.getValueEditorInfo(node)
    },
    setNodeValue(node, value) {
        let _value = value || this.getValueEditorInfo(node).defaultValue()
        let dateCount = 1
        if (_value.value) {
            dateCount = _value.dateCount
            _value = node.operator == 'current' ? _value.value : dateCount + " " + _value.value
        }
        node.value = _value
        node.dateCount = dateCount
        return _value
    },
    updateLeafOperator(node, operator, negate) {
        const previousNode = cloneTree(node);
        node.negate = negate;
        node.operator = operator;
        
        this.setNodeValue(node, node.value.value ? node.value : false)
        if (deepEqual(removeVirtualOperators(node), removeVirtualOperators(previousNode))) {
            this.render();
        }
        this.notifyChanges();
    },
    updateLeafValue(node, value) {
        const _value = this.setNodeValue(node, value)
        return super.updateLeafValue(node, _value)
    }
})

patch(DomainSelector.prototype, {
    getOperatorEditorInfo(node) {
        const info = super.getOperatorEditorInfo(node)
        const fieldDef = this.getFieldDef(node.path);
        const operators = getDomainDisplayedOperators(fieldDef);

        if (['date', 'datetime'].includes(fieldDef.type)) {
            
            const {extractProps, isSupported, stringify} = info
            return {
                ...info,
                extractProps: ({update, value}) => {
                    const extractPropsResult = extractProps({update: update, value: value})
                    let _value = extractPropsResult.value
                    const operator = value[0]
                    if (extraOperators.includes(operator)) {
                        _value = operator
                    }
                    return {
                        update: extractPropsResult.update,
                        options: [
                            ...extractPropsResult.options.filter((key) => operators.includes(key[0])),
                            ...OPTIONS
                        ],
                        value: _value
                    }
                },
                isSupported: ([operator]) => {
                    if (extraOperators.includes(operator)) {
                        return true
                    }
                    return isSupported([operator])
                }, stringify: ([operator, negate]) => {
                    if (extraOperators.includes(operator)) {
                        return OPTIONS.find(([op, str]) => op == operator)[1]
                    }
                    return stringify([operator, negate])
                }
            }
        }

        return info
    }
})

