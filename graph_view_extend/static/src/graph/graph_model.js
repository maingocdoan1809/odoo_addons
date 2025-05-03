import { patch } from "@web/core/utils/patch";
import { GraphModel } from "@web/views/graph/graph_model";


patch(GraphModel.prototype, {
    _getDatasetLabel(dataPoint) {
        const {domains, mode } = this.metaData;
        const {originIndex } = dataPoint;
        if (mode === "funnel") {
            return domains[originIndex].description || "";
        }
        return super._getDatasetLabel(dataPoint)
    }
})
