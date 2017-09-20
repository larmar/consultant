# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'NOX Opportunity Order - Purchase',
  'version': '10.0.0.1',
  'category': 'NOX',
  'summary': 'NOX Opportunity Order - Purchase',
  'description': """
##############################################################
                NOX Opportunity Order - Purchase
##############################################################
This module adds following new fields in Purchase Order view :
    * Contract Signed (check box)
    *	Start Date
    *	End Date

If Purchase Order is created from Sales Order; Start Date & End Date are auto set from Sales Order.

  """,
  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['nox_opportunity_order'],
  'data': [ 
  		'views/purchase.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}