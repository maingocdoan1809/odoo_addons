import { onWillUpdateProps, useComponent, useEffect, useState } from "@odoo/owl";
import { Domain } from "@web/core/domain";
import { useBus, useService } from "@web/core/utils/hooks";
import { SEARCH_KEYS } from "@web/search/with_search/with_search";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { ListRenderer } from "@web/views/list/list_renderer";

export function useX2ManySearch() {
    const component = useComponent()
    const orm = useService('orm')

    const records = useState(component.props.list.records)
    const searchState = useState({
        searchParams: {
            context: {}, 
            domain: [],
        }
    })

    useBus(component.env.searchModel, 'update', async (ev) => {
        const domain = component.env.searchModel['domain']
        searchState.searchParams['domain'] = domain
        if (domain && domain.length > 0) {
            const model = component.props.list.model.config.resModel
            const resId = component.props.list.model.config.resId
            const field = component.props.fieldName

            const domain = searchState.searchParams.domain
            const ids = await orm.call(model, 'search_x2many',[resId, domain, field])
            component.props.list.records = records.filter((r) => ids.includes(r.resId))

        } else {
            component.props.list.records = records
        }
    })
    
    return searchState
}

export class ListRendererX2Many extends ListRenderer {
    setup() {
        super.setup()
        this.searchState = useX2ManySearch()
    }
    static props = [...ListRenderer.props, 'fieldName']
}

export class KanbanRendererX2Many extends KanbanRenderer {
    static props = [...KanbanRenderer.props, 'fieldName']
}