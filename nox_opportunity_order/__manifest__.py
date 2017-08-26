# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'NOX Opportunity Order',
  'version': '10.0.0.1',
  'category': 'Tools',
  'summary': 'NOX Opportunity Order',
  'description': """
##############################################################
                NOX Opportunity Order
##############################################################
	*	This module adds following new fields in Opportunity & Quotation views:
			*	Cost hourly rate
			*	Avg FTE (%)
			*	Total hours
			*	Sales hourly rate
	*	Extra new field added in Quotation / Sales Order view:
			*	Contract Signed
	*	When an Quote is created from an Opportunity the initial values of the above five fields will be taken from the Opportunity. 
	*	When an Quote is created directly without associated opportunity the initial values will be null.
  * It adds a computation button "Calculate Expected Revenue" on Opportunity form header to set Expected Revenue as [[ Expected Revenue = Sales hourly rate x Total hours ]]
  """,
  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['sale_crm', 'nox_crm_lead'],
  'data': [ 
  		'views/crm_lead.xml',
  		'views/sale.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
