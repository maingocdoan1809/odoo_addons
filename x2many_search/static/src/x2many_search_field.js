
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { SearchBar } from "@web/search/search_bar/search_bar";
import { useSearchBarToggler } from "@web/search/search_bar/search_bar_toggler";
import { SearchModel } from "@web/search/search_model";
import { WithSearch } from "@web/search/with_search/with_search";
import { x2ManyField, X2ManyField } from "@web/views/fields/x2many/x2many_field";
import { KanbanRendererX2Many, ListRendererX2Many } from "./components";
import { onWillUpdateProps, useEnv } from "@odoo/owl";
import { useBus } from "@web/core/utils/hooks";

export class X2ManySearchField extends X2ManyField {

    static template = "x2many_search.X2ManySearchField"
    static components = {...X2ManyField.components, WithSearch, Layout, SearchBar, KanbanRendererX2Many, ListRendererX2Many}

    setup() {
        super.setup()
        // this.searchBarToggler = useSearchBarToggler()
        this.searchBarToggler = {}
        this.env = useEnv()
    }

    get display() {
        return {
            controlPanel: {}
        }
    }

    get rendererProps() {
        return {
            ...super.rendererProps,
            fieldName: this.props.name
        }
    }

    get withSearchProps() {
        return {
            SearchModel: SearchModel,
            display: this.display,
            resModel: this.list.resModel,
            searchViewId: false,
            loadIrFilters: false,
            hideCustomGroupBy: true,
            activateFavorite: false,
            searchMenuTypes: ['filter']
        }
    }

}

registry.category("fields").add("x2many_search", {
    ...x2ManyField,
    component: X2ManySearchField
});
