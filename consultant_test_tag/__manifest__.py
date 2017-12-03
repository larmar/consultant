# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
	'name': 'Consultant - Test Tags',
	'version': '10.0.0.1',
	'category': 'Consultant',
	
	'summary': 'Consultant - Test Tags',
	'description': """
##############################################################
			Consultant - Test Tags
##############################################################                    
*	This module adds new tag type: Test Tags
*	New field Index Number is added in :
	*	Competence 
	*	Roles
	* 	Industries
	*	Regions
*	Default is set to 5; Index number can hold number 1-9
*	New tab **Other** is added in Consultant form.
*	Action added **Update test tag on Consultant(s)**
	""",
	
	'author': 'Linserv AB',
	'website': 'www.linserv.se/en/',
	'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],

	'depends': ['consultant'],
	'data': [ 
		'views/consultant_tag.xml',
		'views/consultant.xml',
		'wizard/consultant_test_tag_update.xml',
		
		'security/ir.model.access.csv',
	],

	'application': False,
	'auto_install': False,
	'installable': True,
}
