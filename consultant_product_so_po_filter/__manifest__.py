# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Consultant Product - Products Filter',
  'sequence': 20,
  'version': '10.0.0.1',
  'category': 'Consultant',
  'summary': 'Filter consultant Products in Sales Order & Purchase Order',
  'description': """
##############################################################
          Consultant Product - Products Filter
##############################################################                    
This module filters Product in SO & PO if Consultant Product has ongoing SO or PO.

It also removes "Create and Edit.." option from Products drop down from Sale Order lines & Purchase Order lines.
  """,

  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['consultant_product_link', 'nox_opportunity_order'],
  'data': [ 
    'views/sale.xml',
    'views/purchase.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
