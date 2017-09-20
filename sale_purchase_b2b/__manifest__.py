# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Back to Back Purchase Orders',
  'version': '10.0.0.1',
  'category': 'Sales',
  'summary': 'Back to Back Purchase Orders from Sales Order',
  'description': """
##############################################################
                Back to Back Purchase Orders
##############################################################
	*	This module adds a button in Sales Order screen "Create Draft Purchase Order" which creates Purchase order(s) by Vendors in RFQ state with all sale order line items having Products for which Vendor is set.
	*	This button is available only if Sales Order is confirmed.
	*	A new field "Analytic Account" is also added in Purchase Order.
  """,
  'author': 'Linserv AB',
  'website': 'www.linserv.se/en/',
  'depends': ['sale', 'purchase'],
  'application': False,
  'auto_install': False,
  'installable': True,
  'data': [ 
		'views/sale.xml',
		'views/purchase.xml',
	],
}
