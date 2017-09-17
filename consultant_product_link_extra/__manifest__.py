# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Consultant Product Link - Extra',
  'sequence': 20,
  'version': '10.0.0.1',
  'category': 'Consultant',
  'summary': 'Link Upto 3 Related Products with Consultants',
  'description': """
##############################################################
          Consultant Product Link - Extra Products
##############################################################                    
This module adds 2 extra fields to link Related Product on the Consultant Card.
	* Related Product 2
	* Related Product 3

**When a Consultant Card is created, a new product with Consultant name as Product name and other default settings, is auto created and set on a Consultant Card (consultant_product_link app).**

**This module extends Related Product link on Consultant Card and allows to link upto 2 more Related Products on Consultant Card; on demand; manually by clicking on button Link Product 2 & Link Product 3.**
  """,

  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['consultant_product_link'],
  'data': [ 
    'views/consultant.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
