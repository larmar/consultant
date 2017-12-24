# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
    'name': 'HR Expenses - Unposted Journal Entries',
    'version': '10.0.0.1',
    'category': '',
    'summary': 'HR Expenses - Unposted Journal Entries',
    'description': """
##############################################################
            HR Expenses - Unposted Journal Entries
##############################################################                    
This module changes default functionality to create Unposted Journal Entries from HR Expenses
  """,
    'author': 'Linserv AB',
    'website': 'www.linserv.se/en/',
    'depends': ['hr_expense'],

    'data': [ 
        'views/hr_expense.xml',
	],

    'auto_install': False,
    'installable': True,
}

