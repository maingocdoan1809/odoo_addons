# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_app_ai_bard = fields.Boolean("Google Bard Ai")
    module_app_ai_baidu = fields.Boolean("Baidu Ai China", help='百度文心一格')
    module_app_ai_ali = fields.Boolean("Ali Ai China", help='阿里通义千问')
