# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Purchase Order List view',
  'version': '10.0.0.1',
  'category': 'NOX',
  'summary': 'Purchase Order List view',
  'description': """
##############################################################
                NOX Purchase Order List view
##############################################################
This module modifies and sets Request for Quotation / Purchase Order list view as :
Request for Quotation list :
Order Number | Customer | Vendor | Consultant | Contract signed | Source Document | Start Date | End Date | Status

Purchase Orders list :
Order Number | Customer | Vendor | Consultant | Contract signed | Source Document | Start Date | End Date | Billing Status
  """,
  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['nox_opportunity_order', 'purchase'],
  'data': [ 
  		'views/purchase.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
