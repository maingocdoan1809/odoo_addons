/** @odoo-module */
import { NavBar } from "@web/webclient/navbar/navbar";
import { registry } from "@web/core/registry";
import { fuzzyLookup } from "@web/core/utils/search";
import { computeAppsAndMenuItems } from "@web/webclient/menus/menu_helpers";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useEffect, useRef, useState } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";

patch(NavBar.prototype, {
    // To modify the Navbar properties and functions.
    setup() {
        super.setup()
        this.fetch_data()
    },

    async fetch_data() {
        // To fetch colors from database.
        this.orm = useService("orm")
        var result = await this.orm.call("res.config.settings", "config_color_settings", [0])
        if (result.primary_accent !== false) {
            document.documentElement.style.setProperty("--primary-accent", result.primary_accent)
        }
        if (result.appbar_color !== false) {
            document.documentElement.style.setProperty("--app-bar-accent", result.appbar_color)
        }
        if (result.primary_hover !== false) {
            document.documentElement.style.setProperty("--primary-hover", result.primary_hover)
        }
        if (result.full_bg_img !== false) {
            var imageUrl = 'url(data:image/png;base64,' + result.full_bg_img + ')';
            var appComponentsDivs = document.getElementsByClassName('app_components');

            for (var i = 0; i < appComponentsDivs.length; i++) {
                appComponentsDivs[i].style.backgroundImage = imageUrl;
            }
        }
        if (result.appbar_text !== false) {
            document.documentElement.style.setProperty("--app-menu-font-color", result.appbar_text)
        }
        if (result.secondary_hover !== false) {
            document.documentElement.style.setProperty("--secondary-hover", result.secondary_hover)
        }
        if (result.kanban_bg_color !== false) {
            document.documentElement.style.setProperty("--kanban-bg-color", result.kanban_bg_color)
        }
    },
})


export class NavSideBar extends NavBar {
    static template = "theme.NavSideBar"


}

