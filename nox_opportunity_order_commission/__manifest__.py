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
Commission Order details:
  * Commission Order is created with Vendor selected and Product(s) of type "Is Commission Product".
  * Quantity on Commission order line is set to sum of Total Hours for Consultant 1 & Consultant 2 from related Sales Order.
  * When Vendor bill is created for Commission Order; Bill quantity is the sum of all Vendor bills quantity for all Vendor Bills related to Purchase Order(s); where Purchase Orders & Commission Orders are related to same Sales Order.

  """,
  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['sale_crm', 'sale_purchase_b2b', 'nox_opportunity_order'],
  'data': [ 
  		'views/crm_lead.xml',
  		'views/sale.xml',
  		'views/product.xml',
  		'views/purchase.xml',

  		'data/product_data.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
