# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Consultant - Portal User link',
  'version': '10.0.0.1',
  'category': 'Consultant',
  
  'summary': 'Consultant - Portal User Link',
  
  'description': """
##############################################################
              CONSULTANT - PORTAL USER LINK
##############################################################                    
This module on inviting Partner for sign up (Portal Access Management), assigns created user to all Consultants where Business Contact's email is the same as of the Partner (new user).
  """,
  
  'author': 'Linserv AB',
  'website': 'www.linserv.se/en/',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],

  'depends': ['consultant', 'portal'],
  'data': [ 
  ],

  'application': False,
  'auto_install': False,
  'installable': True,

}
