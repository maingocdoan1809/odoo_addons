from odoo import models, fields, _

class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('split', "Split View")])

    def get_view_info(self):
        info = super().get_view_info()
        _view_info = self._get_view_info()

        info['split'] = {
            'display_name': _('Split View'),
            'icon': _view_info['split']['icon'],
            'multi_record': True,
        }

        return info

    def _get_view_info(self):
        info = super()._get_view_info()
        info['split'] = {'icon': 'fa fa-columns'}
        return info
