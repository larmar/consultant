# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Contact - Extra Fields',
  'version': '10.0.0.1',
  'category': 'Tools',
  'summary': 'Contact - Extra Fields',
  'description': """
##############################################################
                  Contact - Extra Fields
##############################################################
This module adds extra fields in Partner form:
- Linkedin

  """,
  'author': 'Linserv AB',
  'website': 'www.linserv.se/en/',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],

  'depends': ['base'],
  'data': [ 
		'views/res_partner.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
