import { useState } from "@odoo/owl";
import { ListRenderer } from "@web/views/list/list_renderer";

export class SplitViewRenderer extends ListRenderer {
    static recordRowTemplate = "split_view.SplitViewRenderer.ListRecordRow";

    setup() {
        super.setup()
        this.state = useState({
            selectedRecord: undefined
        })
    }

    async onRowClicked(record, column, ev) {
        if (this.env.onRecordSelected && !((this.props.list.model.multiEdit && record.selected) || this.isInlineEditable(record))) {
            this.env.onRecordSelected(record)
            this.state.selectedRecord = record
        } else {
            super.onCellClicked(record, column, ev)
        }
    }

    async onRowDoubleClicked(record, column, ev) {
        return super.onCellClicked(record, column, ev)
    }

    getRowClass(record) {
        const className = super.getRowClass(record)
        if (record == this.state.selectedRecord) {
            return className + " o-row-active"
        }
        return className
    }

}