# -*- coding: utf-8 -*-

# Created on 2023-10-11
# author: 欧度智能，https://www.odooai.cn
# email: 300883@qq.com
# Copyright (C) 2009~2024 odooAi.cn

# Odoo16在线用户手册（长期更新）
# https://www.odooai.cn/documentation/16.0/zh_CN/index.html

# Odoo16在线开发者手册（长期更新）
# https://www.odooai.cn/documentation/16.0/zh_CN/developer.html

##############################################################################
#    Copyright (C) 2009-TODAY odooAi.cn Ltd. https://www.odooai.cn
#    Author: Ivan Deng，300883@qq.com
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#    See <http://www.gnu.org/licenses/>.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
##############################################################################

{
    'name': 'Ai Center,Mass AIGC Generator.Ai Integrate ERP.全Ai服务管理中心',
    'version': '18.0.25.01.05',
    'author': 'odooai.cn',
    'category': 'Industry',
    'website': 'https://www.odooai.cn',
    'live_test_url': 'https://demo.odooapp.cn',
    'license': 'OPL-1',
    'sequence': 2,
    'price': 68.00,
    'currency': 'EUR',
    'images': ['static/description/banner.gif'],
    'summary': '''
    Odoo AI Center. Manage all Ai in odoo. Mass AIGC support. Ai Employee.
    Multi Ai aigc support with Chatgpt,Microsoft Cognitive, Azure ai, Azure openai, Ali Qwen Ai, Azure Ai, Baidu Ai,etc.
    Support chatgpt all version like 4 32k.
    ''',
    'description': '''
    Easy Integrate all ai to serve the odoo erp business.
    1. Multi ChatGpt openAI robot Connector. Chat and train.
    2. Multi Ai support including Azure Ai, Alibaba Ai, Baidu Ai, Chatgpt 4, Chatgpt 3.5 Turbo, Chatgpt 3 Davinci.
    3. Bind ChatGpt Api to user. So we can chat to robot user or use ChatGpt Channel for Group Chat.
    4. White and black List for ChatGpt.
    5. Setup Demo Chat time for every new user.
    6. Easy Start and Stop ChatGpt.
    7. Evaluation the ai robot to make better response. This training.
    8. Add api support Connect the Microsoft Azure OpenAI Service.
    9. Can set Synchronous or Asynchronous mode for Ai response.
    10.Filter Sensitive Words Setup.
    11. Multi-language Support. Multi-Company Support.
    12. Support Odoo 18,17,16,15,14,13,12, Enterprise and Community and odoo.sh Edition.
    13. Full Open Source.
    ''',
    'depends': [
        'app_chatgpt',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
    ],
    # 'pre_init_hook': 'pre_init_hook',
    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': True,
    'auto_install': False,
}
