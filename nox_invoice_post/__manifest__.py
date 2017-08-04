# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
    'name': 'NOX Invoice Posted',
    'version': '10.0.0.1',
    'category': 'Invoicing',
    'summary': 'NOX - Post Customer Invoice(s)',
    'description': """
##############################################################
                NOX - Post Customer Invoice(s)
##############################################################
    * This module adds a check box field "Invoice Posted to Customer" in Customer Invoices
    * It adds an window action to mark selected Invoices as Posted
  """,
    'author': 'Linserv AB',
    'website': 'www.linserv.se/en/',
    'depends': ['account'],
    'data': [ 
        'views/account_invoice.xml',
        'wizard/nox_invoice_post.xml',
    ],
    'application': False,
    'auto_install': False,
    'installable': True,
}
