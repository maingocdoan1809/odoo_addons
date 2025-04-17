/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SearchModel } from "@web/search/search_model";
import { useGetDomainTreeDescription } from "./utils";

patch(SearchModel.prototype, {
    setup(services) {
        super.setup(services)
        this.getDomainTreeDescription = useGetDomainTreeDescription(this.fieldService, services.name)
    }
})