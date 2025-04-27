
import { NavSideBar } from "./search_apps";
import { ActionContainer } from "@web/webclient/actions/action_container";
import { xml } from "@odoo/owl";

ActionContainer.components = {
    ...ActionContainer.components,
    NavSideBar
}

ActionContainer.template = xml`
<t t-name="web.ActionContainer">
    <div class="o_action_manager">
        <NavSideBar t-if="!env.isSmall"/>
        <t t-if="info.Component" t-component="info.Component" className="'o_action'" t-props="info.componentProps" t-key="info.id"/>
    </div>
</t>`;

