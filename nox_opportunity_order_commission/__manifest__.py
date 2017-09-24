# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'NOX Opportunity Order - Commission Payment',
  'version': '10.0.0.1',
  'category': 'NOX',
  'summary': 'NOX Opportunity Order - Commission Payment',
  'description': """
##############################################################
          NOX Opportunity Order - Commission Payment
##############################################################
This module adds following new fields in Opportunity & Quotation/Sales Order views:
    * Commission Payment? (Check box)
    *	Pay to (Vendors list)
    *	Amount per hour

If Commission Payment check box is ticked; "Create Commission Order" button and "Commission Order" tab shows up.
  """,
  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['sale_crm', 'purchase'],
  'data': [ 
  		'views/crm_lead.xml',
  		'views/sale.xml',
  		'views/product.xml',

  		'data/product_data.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
