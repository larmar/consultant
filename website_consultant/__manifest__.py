# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Consultant Website',
  'sequence': 20,
  'version': '10.0.0.1',
  'category': 'Website',
  'summary': 'Consultant Website',
  'description': """
##############################################################
                    CONSULTANTS
##############################################################                    

Manage Consultants Profile Online
  """,
  'author': 'Martin WIlderoth',
  'website': 'www.linserv.se/en/',
  'depends': [
  		'consultant',  
  		'website_portal',
  		],
  'application': False,
  'auto_install': False,
  'installable': True,
  'data': [
  		'security/security.xml',
  		'security/ir.model.access.csv',
  		
      'views/website_consultant_templates.xml',
	],
}
