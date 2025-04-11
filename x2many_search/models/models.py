from odoo import models, fields, api

class Model(models.AbstractModel):
    _inherit = 'base'

    def search_x2many(self, domain, field_name):
        return self[field_name].search(domain)._ids
