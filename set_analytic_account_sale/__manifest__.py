# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Auto Set Analytic Account',
  'sequence': 20,
  'version': '10.0.0.1',
  'category': 'NOX',
  'summary': 'Auto set Analytic Account on Quotation/Sales Order Confirm',
  'description': """
####################################################################
      Auto set Analytic Account on Quotation/Sales Order Confirm
####################################################################              
This module auto sets analytic account on Sales Order when Sales Order(Quotation) is confirmed.

Analytic Account is created with name as: "Sale Order Number"/"Product Name"/"Customer Name"
  """,

  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['sale'],
  'data': [ 
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
