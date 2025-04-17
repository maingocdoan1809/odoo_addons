# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers import domain
from odoo.addons.domain_extend.common  import domain as utils


class DomainExtend(domain.Domain):
    @http.route('/web/domain/validate', type='json', auth="user")
    def validate(self, model, domain):
        # validate domain doesn't need exact week_start
        date_range_transformer = utils.DateRangeCalculator(http.request.env.user.tz, week_start=1)
        new_domain = date_range_transformer.convert_domain(domain)
        return super().validate(model, new_domain)

    @http.route('/web/domain/parsing', type='json', auth="user")
    def parse_custom_domain(self, **params):
        query = params.get('query', False)
        default_day = params.get('default_day', 1)

        if not query:
            return False
        lang = http.request.env['res.lang'].search([('code', '=', http.request.env.user.lang)])
        date_range_transformer = utils.DateRangeCalculator(http.request.env.user.tz, week_start=(int(lang.week_start) or 1))
        new_domain = date_range_transformer.get_date_range_utc(query, int(default_day))
        return new_domain
