# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
    'name': 'NOX - Journal Entries',
    'version': '10.0.0.1',
    'category': 'Tools',
    'summary': 'NOX - Journal Entries',
    'description': """
##############################################################
            NOX - Journal Entries
##############################################################                    
Journal Entries related changes for NOX:
    1) While creating Journal Item, set "Label" by default as the "Reference" field of Journal Entry.

  """,
    'author': 'Linserv AB',
    'website': 'www.linserv.se/en/',
    'depends': ['account'],

    'data': [ 
        'views/account.xml',
	],

    'auto_install': False,
    'installable': True,
}

