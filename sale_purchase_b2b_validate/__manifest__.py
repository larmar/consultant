# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Back to Back Purchase Orders - Validations',
  'version': '10.0.0.1',
  'category': 'Sales',
  'summary': 'Validations on Back to Back Purchase Orders from Sales Order',
  'description': """
Validations on Back to Back Purchase Orders
===========================================
This module adds validations while creating Purchase Order from Sales Order.
  1)  Validates for missing Vendor or Vendor price on Product(s).
  2)  Validates for Product Vendor price on Purchase order lines for equality with Cost hourly rate.
  """,
  'author': 'Linserv AB',
  'website': 'www.linserv.se/en/',
  'depends': ['sale_purchase_b2b', 'nox_opportunity_order'],
  'application': False,
  'auto_install': False,
  'installable': True,
  'data': [ 
	],
}
