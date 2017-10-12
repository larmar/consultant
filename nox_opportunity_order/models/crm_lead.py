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



    nox_cost_hourly_rate = fields.Float('Cost hourly rate')
    nox_ftepercent = fields.Float('Avg FTE (%)')
    nox_ftepercent_temp = fields.Float('Avg FTE (%)')
    nox_sum_hours = fields.Float(string='Total Hours', compute='_compute_nox_sum_hours', store=True)
    nox_sales_hourly_rate = fields.Float('Sales hourly rate')


    @api.multi
    def write(self, vals):
        if 'nox_ftepercent_temp' in vals:
            vals['nox_ftepercent'] = vals['nox_ftepercent_temp']
        return super(CrmLead, self).write(vals)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Search Filters : (1) Won w/o Order (2) Won w/o Order but Passed Start Date
        """
        context = self.env.context
        stages, opportunity_ids, sale_opportunities, result, result2 = [], [], [], [], []

        won_stage_ids = self.env['crm.stage'].search_read([('name', 'ilike', 'won')], fields=['id'])
        for stage in won_stage_ids:
            stages.append(str(stage['id']))

        if stages:
            if context and context.get('won_without_order', False):
                query = """select id from crm_lead where stage_id in (%s)""" % ','.join(stages)
                self._cr.execute(query)
                ids = self._cr.fetchall()
                for opportunity_id in ids:
                    opportunity_ids.append(opportunity_id[0])

                opportunity_ids = list(set(opportunity_ids))

                sale_ids = self.env['sale.order'].search_read([('opportunity_id', '!=', False)], fields=['opportunity_id'])
                for oppor in sale_ids:
                    sale_opportunities.append(oppor['opportunity_id'][0])
                sale_opportunities = list(set(sale_opportunities))

                temp = [result.append(a) for a in opportunity_ids if a not in sale_opportunities]

            if context and context.get('won_with_active_order', False):
                query = """select id from crm_lead where stage_id in (%s)""" % ','.join(stages)
                self._cr.execute(query)
                ids = self._cr.fetchall()
                for opportunity_id in ids:
                    opportunity_ids.append(opportunity_id[0])

                opportunity_ids = list(set(opportunity_ids))
                today = datetime.now().date()
                for oppor in self.env['crm.lead'].browse(opportunity_ids):
                    if oppor.nox_is_startdate and datetime.strptime(oppor.nox_is_startdate, "%Y-%m-%d").date() <= today:
                        result2.append(oppor.id)
                
            if result and result2:
                temp = [result.append(a) for a in result2]
                result = list(set(result))
                args += [('id', 'in', result)]
            elif result:
                args += [('id', 'in', result)]
            elif result2:
                args += [('id', 'in', result2)]
                
        return super(CrmLead, self).search(args, offset, limit, order, count)

    @api.onchange('nox_ftepercent_temp')
    def onchange_nox_ftepercent(self):
        self.nox_ftepercent = self.nox_ftepercent_temp

    @api.multi
    def compute_nox_expected_revenue(self):
        for oppr in self:
            oppr.write({'planned_revenue': (oppr.nox_sales_hourly_rate * oppr.nox_sum_hours)})
