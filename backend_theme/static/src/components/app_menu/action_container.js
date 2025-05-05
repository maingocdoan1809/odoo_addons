
import { NavSideBar } from "./search_apps";
import { ActionContainer } from "@web/webclient/actions/action_container";
import { useEffect, useState, useSubEnv, xml } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";


patch(WebClient.prototype, {
    setup() {
        super.setup()
        this.navbarState = useState({
            isOpen: false
        })
        useSubEnv({
            navbarState: this.navbarState,
            toggleNavBar: () => {
                this.navbarState.isOpen = !this.navbarState.isOpen
            }
        })
    }
})


patch(ActionContainer.prototype, {
    setup() {
        super.setup()
        this.navbarState = useState(this.env.navbarState)
    }
})

ActionContainer.components = {
    ...ActionContainer.components,
    NavSideBar
}

ActionContainer.template = xml`
<t t-name="web.ActionContainer">
    <div class="o_action_manager">
        <NavSideBar t-if="!env.isSmall and navbarState.isOpen"/>
        <t t-if="info.Component" t-component="info.Component" className="'o_action'" t-props="info.componentProps" t-key="info.id"/>
    </div>
</t>`;

