# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Consultant Product Link',
  'sequence': 20,
  'version': '10.0.0.1',
  'category': 'Consultant',
  'summary': 'Auto Link Standard Hour Product with Consultants',
  'description': """
##############################################################
              Consultant Product Link
##############################################################                    
Auto Link Standard Hour Product with Consultants
	* When a new Consultant created; auto create & link a Product with Consultant 

Auto set Consultant stage based on related sales order's Expiration Date.

Auto populate Quotation Lines when created from Opportunity with linked Consultant(s).

If any related sales order has valid expiry date (in future); set consultant stage as "On NOX Contract"; otherwise "Sale ready".
  """,

  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['consultant', 'sale_expense', 'purchase', 'nox_opportunity_order'],
  'data': [ 
    'views/consultant.xml',

    'data/data.xml',

    'security/ir.model.access.csv',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
