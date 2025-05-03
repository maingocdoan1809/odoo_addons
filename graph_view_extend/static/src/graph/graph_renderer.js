import { onMounted, onRendered, onWillStart } from "@odoo/owl";
import { loadJS } from "@web/core/assets";
import { patch } from "@web/core/utils/patch";
import { GraphRenderer } from "@web/views/graph/graph_renderer";


patch(GraphRenderer.prototype, {
    setup() {
        super.setup()

        onMounted(async () => {
            await loadJS('/graph_view_extend/static/src/lib/index.umd.js')
        })

    },

    prepareOptions() {
        const options = super.prepareOptions()
        const {mode} = this.model.metaData
        if (mode == 'funnel') {
            options.indexAxis = 'y'
            options.plugins.legend.position = 'right'
            delete options.scales
            
        }
        return options
    },

    getChartConfig() {
        const { mode } = this.model.metaData;
        let data;
        if (mode == 'funnel') {
            data = this.getFunnelChartData()
            const options = this.prepareOptions();
            const config = { data, options, type: mode };
            return config;
        }
        return super.getChartConfig()
    },

    generateGradientColors(count) {
        const base = [52, 152, 219]; // blue
        return Array.from({ length: count }, (_, i) => {
            const factor = 1 - (i / count) * 0.5; // giảm độ sáng
            return `rgba(${base[0] * factor}, ${base[1] * factor}, ${base[2] * factor}, 1)`;
        });
    },    

    transformToTrueFunnelData(rawData) {
        const labelTotals = rawData.labels.map((label, index) => {
            const total = rawData.datasets.reduce((sum, dataset) => {
                return sum + (dataset.data[index] || 0);
            }, 0);
            return {
                label,
                value: total
            };
        });
    
        labelTotals.sort((a, b) => b.value - a.value);
    
        return {
            labels: labelTotals.map(item => item.label),
            datasets: [{
                data: labelTotals.map(item => item.value),
                backgroundColor: this.generateGradientColors(labelTotals.length),
            }]
        };
    },
    

    getFunnelChartData() {
        return this.getPieChartData()
    }

})
