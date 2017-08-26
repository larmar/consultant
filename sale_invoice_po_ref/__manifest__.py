# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Sales - PO Number',
  'version': '10.0.0.1',
  'category': 'Extra Tools',
  'summary': 'Add Customer PO Ref in Sales Order',
  'description': """
##############################################################
            Sales - Invoice : Customer PO Number
##############################################################                    
  * This module adds new field in Quotation / Sales Order: "Customer PO Number"
  * Customer PO Number, if exists; is also shown on related Invoice report
  """,

  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['sale'],
  'data': [ 
    'views/sale_view.xml',
    'views/report_invoice_po_number.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
