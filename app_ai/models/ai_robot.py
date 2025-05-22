# -*- coding: utf-8 -*-

import requests, json
import base64

from odoo import api, fields, models, modules, tools, _
from odoo.exceptions import UserError
from .lib.WordsSearch import WordsSearch

import logging
_logger = logging.getLogger(__name__)


class AiRobot(models.Model):
    _inherit = 'ai.robot'

    # 以下 hook ，直接覆盖
    def get_ai_pre(self, data, author_id=False, answer_id=False, param={}):
        if self.is_filtering:
            search = WordsSearch()
            search.SetKeywords([])
            if isinstance(data, list):
                content = data[len(data)-1]['content']
            else:
                content = data
            sensi = search.FindFirst(content)
            if sensi is not None:
                _logger.error('==========敏感词：%s' % sensi['Keyword'])
                return _('温馨提示：您发送的内容含有敏感词，请修改内容后再向我发送。')
        elif not author_id.gpt_id and answer_id.gpt_id:
            user_id = answer_id.user_ids[:1]
            gpt_policy = user_id.gpt_policy
            gpt_wl_partners = user_id.gpt_wl_partners
            is_allow = author_id.id in gpt_wl_partners.ids
            if gpt_policy != 'all' and not is_allow:
                # 暂时有限用户的Ai
                return _('此Ai暂时未开放，请联系管理员。')
        else:
            return False

    def get_ai_post(self, res, author_id=False, answer_id=False, param=None):
        if param is None:
            param = {}
        if not res or not author_id or (not isinstance(res, list) and not isinstance(res, dict)):
            return res, False, False
        
        usage = content = data = None
        try:
            if self.provider == 'openai':
                usage = res['usage']
                content = res['choices'][0]['message']['content']
            elif self.provider == 'azure':
                # azure 格式
                if res.get('error'):
                    usage = False
                    content = res.get('error')
                else:
                    usage = res['usage']
                    content = res['choices'][0]['message']['content']
            elif self.provider == 'ali':
                usage = res['usage']
                content = res['output']['text']
            elif self.provider == 'baidu':
                usage = res['usage']
                content = res['result']
            else:
                usage = False
                content = res
            
            data = content.replace(' .', '.').strip()
            
            answer_user = False
            if answer_id:
                answer_user = answer_id.mapped('user_ids')[:1]
            
            if usage:
                if self.provider == 'ali':
                    prompt_tokens = usage['input_tokens']
                    completion_tokens = usage['output_tokens']
                    total_tokens = usage['input_tokens'] + usage['output_tokens']
                else:
                    prompt_tokens = usage['prompt_tokens']
                    completion_tokens = usage['completion_tokens']
                    total_tokens = usage['total_tokens']
                # 不是写到 user ，是要写到指定 m2m 相关模型， 如：  res.partner.ai.use
                ai_use = self.env['res.partner.ai.use'].search([('name', '=', author_id.id)], limit=1)
                ask_date = fields.Datetime.now()
                if not ai_use:
                    ai_use.create({
                        'name': author_id.id,
                        'ai_user_id': answer_user.id,
                        'human_prompt_tokens': prompt_tokens,
                        'ai_completion_tokens': completion_tokens,
                        'tokens_total': total_tokens,
                        'used_number': 1,
                        'first_ask_time': ask_date,
                        'latest_ask_time': ask_date
                    })
                else:
                    vals = {
                        'human_prompt_tokens': ai_use.human_prompt_tokens + prompt_tokens,
                        'ai_completion_tokens': ai_use.ai_completion_tokens + completion_tokens,
                        'tokens_total': ai_use.tokens_total + total_tokens,
                        'used_number': ai_use.used_number + 1,
                        'latest_ask_time': ask_date
                    }
                    if not ai_use.first_ask_time:
                        vals.update({
                            'first_ask_time': ask_date
                        })
                    ai_use.write(vals)
            return data, usage, True        
        except Exception as e:
            _logger.error('==========app_ai get_ai_post Error: %s' % e)
            return res, False, False
    
    def filter_sensitive_words(self, data):
        if self.is_filtering:
            search = WordsSearch()
            s = self.sensitive_words
            if s:
                search.SetKeywords(s.split('\n'))
            else:
                search.SetKeywords([])
            data = search.Replace(text=data)
            return data
        else:
            return data
