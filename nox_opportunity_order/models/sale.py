# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

from datetime import datetime

from odoo.addons.nox_opportunity_order.models.crm_lead import get_weekdaysrange
from odoo.addons.nox_opportunity_order.models.crm_lead import get_value_percent

class SaleOrder(models.Model):
    _inherit = "sale.order"

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

    nox_is_startdate = fields.Date("Start Date")
    nox_is_enddate = fields.Date("End Date")
    nox_cost_hourly_rate = fields.Float('Cost hourly rate')
    nox_ftepercent = fields.Float('Avg FTE (%)')
    nox_ftepercent_temp = fields.Float('Avg FTE (%)')
    nox_sum_hours = fields.Float(string='Total Hours', compute='_compute_nox_sum_hours', store=True)
    nox_sales_hourly_rate = fields.Float('Sales hourly rate')

    nox_contract_signed = fields.Boolean('Contract Signed')

    @api.model
    def default_get(self, fields):
        """Set default values on NOX Order fields if Quotation is created from Opportunity
        """
        context = self._context
        res = super(SaleOrder, self).default_get(fields)
        opportunity_id = context.get('default_opportunity_id', False)
        if opportunity_id:
            Opportunity = self.env['crm.lead'].browse([opportunity_id])
            res.update({
                    'nox_is_startdate': Opportunity.nox_is_startdate,
                    'nox_is_enddate': Opportunity.nox_is_enddate,
                    'nox_cost_hourly_rate': Opportunity.nox_cost_hourly_rate,
                    'nox_ftepercent': Opportunity.nox_ftepercent,
                    'nox_ftepercent_temp': Opportunity.nox_ftepercent_temp,
                    'nox_sum_hours': Opportunity.nox_sum_hours,
                    'nox_sales_hourly_rate': Opportunity.nox_sales_hourly_rate,
                })
        return res

    @api.multi
    def write(self, vals):
        if 'nox_ftepercent_temp' in vals:
            vals['nox_ftepercent'] = vals['nox_ftepercent_temp']
        return super(SaleOrder, self).write(vals)

    @api.onchange('nox_ftepercent_temp')
    def onchange_nox_ftepercent(self):
        self.nox_ftepercent = self.nox_ftepercent_temp