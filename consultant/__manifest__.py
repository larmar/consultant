# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'Consultant',
  'sequence': 20,
  'version': '10.0.0.1',
  'category': 'Consultant',
  'summary': 'Manage consultants and search for knowledge',
  'description': """
##############################################################
                    CONSULTANTS
##############################################################                    

Manage consultants and search for knowledge
  """,
  'author': 'Martin WIlderoth',
  'website': 'www.linserv.se/en/',
  'depends': ['crm'],
  'application': True,
  'auto_install': False,
  'installable': True,
  'data': [ 
    'security/consultant_security.xml',

		'views/consultant_consult.xml',
		'views/crm_lead.xml',
    'wizard/consultant_opportunity_link.xml',

    'data/consultant.xml',
    
    'security/ir.model.access.csv',
	],
}
