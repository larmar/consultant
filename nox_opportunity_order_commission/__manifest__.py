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
  'category': 'Tools',
  'summary': 'NOX Opportunity Order - Commission Payment',
  'description': """
##############################################################
          NOX Opportunity Order - Commission Payment
##############################################################
This module adds following new fields in Opportunity & Quotation/Sales Order views:
    * Commission Payment? (Check box)
    *	Pay to (Vendors list)
    *	Amount per hour

  """,
  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['sale_crm'],
  'data': [ 
  		'views/crm_lead.xml',
  		'views/sale.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
