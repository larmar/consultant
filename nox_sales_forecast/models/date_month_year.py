# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError

from datetime import datetime

MONTHS = {
	1: 'January',
	2: 'February',
	3: 'March',
	4: 'April',
	5: 'May',
	6: 'June',
	7: 'July',
	8: 'August',
	9: 'September',
	10: 'October',
	11: 'November',
	12: 'December'
}
class date_month_year(models.Model):
	_name = "date.month.year"
	_description = "Years"
	_order = "month,year"

	year = fields.Integer('Year', size=4, required=True)
	month = fields.Integer('Month', size=2, required=True)

	_sql_constraints = [('month_year_uniq', 'unique(year,month)', 'Duplicate Month-Year not allowed!')]

	@api.multi
	def name_get(self):
		res = []
		for rec in self:
			month = MONTHS[rec.month]
			res.append((rec.id, ' '.join([month, str(rec.year)])))
		return res

	@api.model
	def generate_current_year_months(self):
		"""Function to generate months of the current year on module installation
		"""
		year = datetime.now().year
		for month in MONTHS:
			if not self.search([('year','=',year), ('month','=',month)]):
				rec = self.create({
						'year': year,
						'month': month
					})
				self.env['date.month.working.hours'].create({
						'month_year_id': rec.id
					})
		return True

class date_month_working_hours(models.Model):
	_name = "date.month.working.hours"
	_description = "Working Hours Per Month"
	_rec_name = 'month_year_id'
	_order = "year,month"

	month_year_id = fields.Many2one('date.month.year', 'Month', required=True)
	month = fields.Integer(related="month_year_id.month", store=True)
	year = fields.Integer(related="month_year_id.year", store=True)
	working_hours = fields.Integer('Working Hours')

	@api.constrains('working_hours')
	def check_working_hours(self):
		if self.working_hours > 720:
			raise ValidationError('Invalid Hours!\n\nWorking hours exceeded total hours in a month.')
		if self.working_hours < 0:
			raise ValidationError('Invalid Hours!\n\nWorking hours cannot be less than 0.')
