# -*- coding: utf-8 -*-

import requests, json
import datetime
# from transformers import TextDavinciTokenizer, TextDavinciModel
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.addons.app_common.models.base import get_ua_type

import logging
_logger = logging.getLogger(__name__)


class Channel(models.Model):
    _inherit = 'discuss.channel'

    description = fields.Text(translate=True)
