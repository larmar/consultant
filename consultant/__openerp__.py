{
  'name': 'Consultant Application',
  'version': '9.0.0.2',
  'category': 'Consultants',
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
  'data': [ 
		'data/consultant.xml',
		'views/consultant_consult.xml',
		'views/crm_lead.xml',
    'wizard/consultant_opportunity_link.xml',
	],
}
