# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Purchase Close (Locked)',
  'version': '10.0.0.1',
  'category': 'Tools',
  'summary': 'Purchase Close (Locked)',
  'description': """
##############################################################
                  Purchase Close (Locked)
##############################################################
  * This module renames Lock button on PO to Close & related stage to Closed.
  * It also restricts creating Invoice from Closed PO.
  """,
  'author': 'Linserv AB',
  'website': 'www.linserv.se/en/',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],

  'depends': ['purchase'],
  'data': [ 
		'views/purchase.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
