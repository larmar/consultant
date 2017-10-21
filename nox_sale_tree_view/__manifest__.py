# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Sale Order List view',
  'version': '10.0.0.1',
  'category': 'NOX',
  'summary': 'Sale Order List view',
  'description': """
##############################################################
                NOX Sale Order List view
##############################################################
This module modifies and sets Quotation / Sales Order list views.
Quotation List view :
Order Number | Customer | Consultant | Contract signed | Start Date | Start Follow-up Date | End Date | End Follow-up Date | Salesperson | Status

Sales Order List view :
Order Number | Customer | Consultant | Contract signed | Start Date | Start Follow-up Date | End Date | End Follow-up Date | Salesperson | Invoice Status

  """,
  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['sale_crm', 'nox_opportunity_order', 'sale_order_dates'],
  'data': [ 
  		'views/sale.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
