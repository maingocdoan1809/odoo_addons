from odoo import models, api
from odoo.addons.domain_extend.common  import domain as utils


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        try:
            crr_tz = self.env.context.get('tz', 'UTC')
            lang = self.env['res.lang'].search([('code', '=', self.env.user.lang)])
            converter = utils.DateRangeCalculator(crr_tz, week_start=(int(lang.week_start) or 1))
            new_domain = converter.convert_domain(domain)
            return super().web_search_read(new_domain, specification, offset, limit, order, count_limit)
        except:
            return super().web_search_read(domain, specification, offset, limit, order, count_limit)
