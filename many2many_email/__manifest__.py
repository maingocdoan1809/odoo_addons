# -*- coding: utf-8 -*-
{
    'name': "Many2Many Email",
    'author': "Nissho Electronic Vietnam",
    'category': 'Customizations',
    'version': '1.0',
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'depends': [
        'web'
    ],
    'assets': {
        'web.assets_backend': [
            'many2many_email/static/src/many2many_email.js'
        ],
    }
}
