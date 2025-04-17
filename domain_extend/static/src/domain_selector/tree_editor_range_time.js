/** @odoo-module **/
import { Component, useEffect, useEnv, useState } from "@odoo/owl";
import { Select } from "@web/core/tree_editor/tree_editor_components";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
import { useDebounced } from "@web/core/utils/timing";
import { formatDateTime } from "@web/core/l10n/dates";

const { DateTime } = luxon

export class TreeEditorRangeTime extends Component {
    static template = 'nev_helpdesk.TreeEditor.RangeTime'
    static props = ["value", "update", "options", "defaultValue", "node", "rangeProps"];
    static components = {Select, DateTimeInput}

    setup() {
        this.rpc = useService('rpc')

        this.user = useService('user')

        this.state = useState({
            dateCount: this.nodeCount,
            currentValue: this.nodeValue || "",
            showInputBox: this.showInputBox,
            dateStart: undefined,
            dateEnd: undefined,
        })

        this.getDateDetail = useDebounced(() => {
            this.rpc('/web/domain/parsing', {
                query: this.state.currentValue,
                default_day: this.state.dateCount
            }).then(data => {
                if(data && data.length == 2) {
                    this.state.dateStart = this.convertToBrowserTimeString(data[0])
                    this.state.dateEnd = this.convertToBrowserTimeString(data[1])
                }
            })
        }, 500)

        useEffect(() => {
            this.state.showInputBox = this.showInputBox
            this.state.currentValue = this.nodeValue
            this.state.dateCount = this.nodeCount
            
        }, () => [this.state.currentValue, this.showInputBox, this.nodeValue, this.nodeCount])

        useEffect(() => {
            this.getDateDetail()
        }, () => [this.state.currentValue, this.state.dateCount])

    }

    onKeydown(ev) {
        if (ev.key == '-') {
            ev.preventDefault()
        }
    }


    convertToBrowserTimeString(utcDateString) {
        if (!utcDateString) {
            return ""
        }
        const utcDate = new Date(utcDateString + " UTC");
        const localDate = new Date(utcDate);
        return formatDateTime(DateTime.fromJSDate(localDate))
    }

    get nodeValue() {
        const propsVal = this.props.node.value
        if (propsVal) {
            const val = propsVal.split(' ')
            if (val.length == 1) {
                return val[0]
            }
            return val[1]
        }
        return this.nodeDefaultValue
    }
    get nodeCount() {
        const propsVal = this.props.node.value
        if (propsVal) {
            const val = propsVal.split(' ')
            if (val.length == 2) {
                return val[0]
            }
        }
        return 1
    }
    get nodeDefaultValue() {
        return this.props.defaultValue().value
    }
    get showInputBox() {
        return ['last_n_day', 'next_n_day'].includes(this.state?.currentValue)
    }
    onInputChange(ev) {
        this.state.dateCount = Number(ev.target.value)
        this.props.update({
            dateCount: this.state.dateCount,
            value: this.state.currentValue
        })
    }
    get extractProps() {
        return {
            value: this.state.currentValue,
            update: (value) => {
                let dateCount = this.state.dateCount
                this.state.currentValue = value
                if (this.showInputBox) {
                    value = {
                        dateCount, value
                    }
                }
                this.props.update(value)
            },
            options: this.props.options
        }
    }
}