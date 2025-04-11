from odoo import models, fields

class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'
    
    view_mode = fields.Selection(selection_add=[('split', "Split View")], ondelete={'split': 'cascade'})
