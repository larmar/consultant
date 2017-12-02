# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Sale Close (Locked)',
  'version': '10.0.0.1',
  'category': 'Tools',
  'summary': 'Sale Close (Locked)',
  'description': """
##############################################################
                  Sale Close (Locked)
##############################################################
  * This module renames Lock button on SO to Close & related stage to Closed.
  * It also restricts creating Invoice from Closed SO.
  """,
  'author': 'Linserv AB',
  'website': 'www.linserv.se/en/',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],

  'depends': ['sale'],
  'data': [ 
		'views/sale.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
