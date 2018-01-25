# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

{
  'name': 'NOX - Sales Forecast',
  'version': '10.0.0.1',
  'category': 'NOX',
  'summary': 'NOX - Sales Forecast',
  'description': """
##############################################################
                NOX - Sales Forecast
##############################################################
Sales Forecasting for Cost & Revenue
	*	Auto generate "Working Hours by month" records for every calendar year

  """,
  'author': 'Linserv AB',
  'contributors': ['Riyaj Pathan <rjpathan19@gmail.com>'],
  'website': 'www.linserv.se/en/',
  'depends': ['analytic', 'nox_opportunity_order'],
  'data': [ 
  		
  		'security/ir.model.access.csv',

  		'data/data.xml',
  		'data/scheduler.xml',

  		'views/date_month_view.xml',
      'views/analytic_account_view.xml',

      'report/sale_forecast_report.xml',
	],

  'application': False,
  'auto_install': False,
  'installable': True,
}
