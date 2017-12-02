# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Sale Cancel',
  'version': '10.0.0.1',
  'category': 'Tools',
  'summary': 'Sale Cancel',
  'description': """
##############################################################
                  Sale Cancel
##############################################################
  * On Cancelling SO, related  PO also gets cancelled (if allowed).
  """,
  'author': 'Linserv AB',
  'website': 'www.linserv.se/en/',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],

  'depends': ['sale_purchase_b2b'],
  'data': [ 
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
