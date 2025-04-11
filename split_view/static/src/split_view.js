
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { FormSplitController, SplitViewController } from "./split_view_controller";
import { SplitViewRenderer } from "./split_view_renderer";
import { SplitViewArchParser } from "./split_view_arch_parser";
import { formView } from "@web/views/form/form_view";

export const splitFormView = {
    ...formView,
    Controller: FormSplitController
}

export const splitView = {
    ...listView,
    type: "split",
    Controller: SplitViewController,
    Renderer: SplitViewRenderer,
    ArchParser: SplitViewArchParser,
};

registry.category("views").add("split", splitView);
registry.category("views").add("form_split", splitFormView);
