import { useState, useSubEnv } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { ListController } from "@web/views/list/list_controller";
import { View } from "@web/views/view";


export class FormSplitController extends FormController {
    setup() {
        super.setup()
        // custom form controller
    }
}

export class FormView extends View {
    onWillUpdateProps(nextProps) {
        return this.loadView(nextProps);
    }
}

export class SplitViewController extends ListController {

    static template = `split_view.WebSplitListView`

    static components = {
        ...ListController.components,
        FormView
    }

    setup() {
        super.setup()

        this.selectedRecord = useState({
            record: undefined
        })
        
        useSubEnv({
            'onRecordSelected': this.onRecordSelected.bind(this),
        })

    }

    onRecordSelected(record) {
        this.selectedRecord.record = record
    }

    get formSplitViewProps() {

        return {
            type: 'form',
            resModel: this.selectedRecord.record.resModel,
            resId: this.selectedRecord.record.resId,
            context: this.model.config.context,
            display: {
                controlPanel: false
            },
            mode: 'readonly',
            noBreadcrumbs: true,
            jsClass: 'form_split'
        }
    }
}
