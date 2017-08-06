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
  'summary': 'Link Standard Hour Product with Consultants',
  'description': """
##############################################################
              Consultant Product Link
##############################################################                    
Link Standard Hour Product with Consultants
  """,

  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['consultant', 'sale', 'purchase'],
  'data': [ 
    'views/consultant.xml',

    'securiyt/ir.model.access.csv',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
