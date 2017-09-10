# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

from datetime import datetime
from dateutil.rrule import DAILY, rrule, MO, TU, WE, TH, FR

def get_weekdaysrange(start_date, end_date):
	return list(rrule(DAILY, dtstart=start_date, until=end_date, byweekday=(MO,TU,WE,TH,FR)))

def get_value_percent(value, percent):
	return value * (percent / 100)

class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.multi
    @api.depends('nox_is_startdate', 'nox_is_enddate', 'nox_ftepercent_temp')
    def _compute_nox_sum_hours(self):
    	for oppr in self:
    		oppr.nox_sum_hours = 0.0
    		if oppr.nox_is_startdate and oppr.nox_is_enddate and oppr.nox_ftepercent_temp and oppr.nox_is_enddate >= oppr.nox_is_startdate:
    			start_date = datetime.strptime(oppr.nox_is_startdate, "%Y-%m-%d").date()
    			end_date = datetime.strptime(oppr.nox_is_enddate, "%Y-%m-%d").date()
    			diffDays = get_weekdaysrange(start_date, end_date)
    			if diffDays:
    				nox_sum_hours = get_value_percent((len(diffDays) * 8), oppr.nox_ftepercent_temp)
    				oppr.nox_sum_hours = nox_sum_hours

    @api.multi
    @api.depends('nox_is_startdate', 'nox_is_enddate', 'nox_ftepercent_temp2')
    def _compute_nox_sum_hours2(self):
        for oppr in self:
            oppr.nox_sum_hours2 = 0.0
            if oppr.nox_is_startdate and oppr.nox_is_enddate and oppr.nox_ftepercent_temp2 and oppr.nox_is_enddate >= oppr.nox_is_startdate:
                start_date = datetime.strptime(oppr.nox_is_startdate, "%Y-%m-%d").date()
                end_date = datetime.strptime(oppr.nox_is_enddate, "%Y-%m-%d").date()
                diffDays = get_weekdaysrange(start_date, end_date)
                if diffDays:
                    nox_sum_hours2 = get_value_percent((len(diffDays) * 8), oppr.nox_ftepercent_temp2)
                    oppr.nox_sum_hours2 = nox_sum_hours2


    nox_cost_hourly_rate = fields.Float('Cost hourly rate')
    nox_ftepercent = fields.Float('Avg FTE (%)')
    nox_ftepercent_temp = fields.Float('Avg FTE (%)')
    nox_sum_hours = fields.Float(string='Total Hours', compute='_compute_nox_sum_hours', store=True)
    nox_sales_hourly_rate = fields.Float('Sales hourly rate')

    nox_cost_hourly_rate2 = fields.Float('Cost hourly rate')
    nox_ftepercent2 = fields.Float('Avg FTE (%)')
    nox_ftepercent_temp2 = fields.Float('Avg FTE (%)')
    nox_sum_hours2 = fields.Float(string='Total Hours', compute='_compute_nox_sum_hours2', store=True)
    nox_sales_hourly_rate2 = fields.Float('Sales hourly rate')

    nox_product1 = fields.Many2one('product.product', 'Related Product 1')
    nox_product2 = fields.Many2one('product.product', 'Related Product 2')


    @api.multi
    def write(self, vals):
        if 'nox_ftepercent_temp' in vals:
            vals['nox_ftepercent'] = vals['nox_ftepercent_temp']
        if 'nox_ftepercent_temp2' in vals:
            vals['nox_ftepercent2'] = vals['nox_ftepercent_temp2']
        return super(CrmLead, self).write(vals)

    @api.onchange('nox_ftepercent_temp')
    def onchange_nox_ftepercent(self):
        self.nox_ftepercent = self.nox_ftepercent_temp

    @api.onchange('nox_ftepercent_temp2')
    def onchange_nox_ftepercent2(self):
        self.nox_ftepercent2 = self.nox_ftepercent_temp2

    @api.multi
    def compute_nox_expected_revenue(self):
        for oppr in self:
            oppr.write({'planned_revenue': (oppr.nox_sales_hourly_rate * oppr.nox_sum_hours) + (oppr.nox_sales_hourly_rate2 * oppr.nox_sum_hours2)})
