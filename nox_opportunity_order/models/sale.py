# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

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

    nox_is_startdate = fields.Date("Start Date")
    nox_is_enddate = fields.Date("End Date")
    nox_cost_hourly_rate = fields.Float('Cost hourly rate')
    nox_ftepercent = fields.Float('Avg FTE (%)')
    nox_ftepercent_temp = fields.Float('Avg FTE (%)')
    nox_sum_hours = fields.Float(string='Total Hours', compute='_compute_nox_sum_hours', store=True)
    nox_sales_hourly_rate = fields.Float('Sales hourly rate')

    nox_contract_signed = fields.Boolean('Contract Signed')

    nox_ftepercent2 = fields.Float('Avg FTE (%)')
    nox_ftepercent_temp2 = fields.Float('Avg FTE (%)')
    nox_sum_hours2 = fields.Float(string='Total Hours', compute='_compute_nox_sum_hours2', store=True)
    nox_sales_hourly_rate2 = fields.Float('Sales hourly rate')
    nox_cost_hourly_rate2 = fields.Float('Cost hourly rate')

    nox_product1 = fields.Many2one('product.product', 'Consultant 1')
    nox_product2 = fields.Many2one('product.product', 'Consultant 2')
    consultant_names = fields.Char(compute='compute_consultant_names', string='Consultants', store=True)

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
                    
                })

            self._cr.execute(""" select consultant_id from consultant_consult_opportunity_rel
                                where opportunity_id=%s """%(opportunity_id))
            result = self._cr.fetchall()
            consultants = []
            for r in result:
                consultants.append(r[0])

            #set Related Product on Quotation:
            if consultants:
                consultant1_product = self.env['consultant.consult'].browse([consultants[0]])[0].product_id
                res.update({
                        'nox_product1': consultant1_product and consultant1_product.id or False,
                        'nox_cost_hourly_rate': Opportunity.nox_cost_hourly_rate,
                        'nox_ftepercent': Opportunity.nox_ftepercent,
                        'nox_ftepercent_temp': Opportunity.nox_ftepercent_temp,
                        'nox_sum_hours': Opportunity.nox_sum_hours,
                        'nox_sales_hourly_rate': Opportunity.nox_sales_hourly_rate,
                    })
                
                #set Related Product 2 and related fields if more than one consutant is linked with Opportunity:
                if len(consultants) > 1:
                    consultant2_product = self.env['consultant.consult'].browse([consultants[1]])[0].product_id
                    res.update({
                            'nox_product2': consultant2_product and consultant2_product.id or False,
                            'nox_cost_hourly_rate2': Opportunity.nox_cost_hourly_rate,
                            'nox_ftepercent2': Opportunity.nox_ftepercent,
                            'nox_ftepercent_temp2': Opportunity.nox_ftepercent_temp,
                            'nox_sum_hours2': Opportunity.nox_sum_hours,
                            'nox_sales_hourly_rate2': Opportunity.nox_sales_hourly_rate,
                        })

        return res

    @api.multi
    def write(self, vals):
        if 'nox_ftepercent_temp' in vals:
            vals['nox_ftepercent'] = vals['nox_ftepercent_temp']
        if 'nox_ftepercent_temp2' in vals:
            vals['nox_ftepercent2'] = vals['nox_ftepercent_temp2']
        
        #check & match Related Product, Total Hours & Sales hourly rate with respective Order line product, Ordered Quantity & Unit price in Order lines:
        res = super(SaleOrder, self).write(vals)

        #Validate Start Date & End Date
        start_date = self.nox_is_startdate
        end_date = self.nox_is_enddate
        if 'nox_is_startdate' in vals:
            start_date = vals['nox_is_startdate']
        if 'nox_is_enddate' in vals:
            end_date = vals['nox_is_enddate']

        if start_date and end_date and start_date > end_date:
            raise ValidationError(_('Invalid Start Date!\n\nContract Start Date cannot be greater than End Date!'))

        if self.nox_product1:
            self.validate_related_product_with_orderline(self.nox_product1, self.nox_sum_hours, self.nox_sales_hourly_rate, 1)
        if self.nox_product2:
            self.validate_related_product_with_orderline(self.nox_product2, self.nox_sum_hours2, self.nox_sales_hourly_rate2, 2)

        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Filter Not Started | Started | Ended
        """
        context = self.env.context or {}
        filter_flag, ids = False, []
        if context.get('nox_not_started', False):
            filter_flag = True
            now = datetime.now().date()
            self._cr.execute("""select id from sale_order 
                                    where nox_is_startdate > '%s'"""%(now))
            result = self._cr.fetchall()
            for res in result:
                ids.append(res[0])
        
        if context.get('nox_started', False):
            filter_flag = True
            now = datetime.now().date()
            self._cr.execute("""select id from sale_order 
                                    where nox_is_startdate <= '%s' and
                                    nox_is_enddate > '%s'"""%(now, now))
            result = self._cr.fetchall()
            for res in result:
                ids.append(res[0])
        
        if context.get('nox_ended', False):
            filter_flag = True
            now = datetime.now().date()
            self._cr.execute("""select id from sale_order 
                                    where nox_is_enddate <= '%s'"""%(now))
            result = self._cr.fetchall()
            for res in result:
                ids.append(res[0])

        if filter_flag:
            ids = list(set(ids))
            if not args:
                args = [['id', 'in', ids]]
            else:
                args.append(['id', 'in', ids])
        return super(SaleOrder, self).search(args, offset, limit, order, count)

    @api.multi
    def validate_related_product_with_orderline(self, product=False, sum_hours=0.0, unit_price=0.0, line_counter=1):
        product_matching_flag, qty_flag, unit_price_flag = False, True, True
        for line in self.order_line:
            if line.product_id.id == product.id:
                product_matching_flag = True
                if line.product_uom_qty != sum_hours:
                    qty_flag = False
                    break
                if line.price_unit != unit_price:
                    unit_price_flag = False
                    break

        if not product_matching_flag:
            raise ValidationError(_('Missing Related Product in Order Lines!\n\n\
                                    Please add Order line item with Related Product %s - %s'%(str(line_counter), product.name)))
        if not qty_flag:
            raise ValidationError(_('Ordered Quantity Mismatch with Total Hours!\n\n\
                                    Ordered Quantity in Order lines for Product %s should be same as Total hours for related Product %s.'%(product.name, str(line_counter))))
        if not unit_price_flag:
            raise ValidationError(_('Unit Price Mismatch with Sales hourly rate!\n\n\
                                    Unit Price in Order lines for Product %s should be same as Sales hourly rate for related Product %s.'%(product.name, str(line_counter))))
        return True

    @api.depends('nox_product1', 'nox_product2')
    def compute_consultant_names(self):
        for sale in self:
            consultant_names = ', '.join(filter(bool, list(set([sale.nox_product1 and sale.nox_product1.name or False, sale.nox_product2 and sale.nox_product2.name or False]))))
            sale.consultant_names = consultant_names

    @api.onchange('nox_ftepercent_temp')
    def onchange_nox_ftepercent(self):
        self.nox_ftepercent = self.nox_ftepercent_temp

    @api.onchange('nox_ftepercent_temp2')
    def onchange_nox_ftepercent2(self):
        self.nox_ftepercent2 = self.nox_ftepercent_temp2

    @api.multi
    def action_update_nox_product_price(self):
        """Update Related Product 1 and 2's Sales price with their Sales hourly rate and Vendor Price with Cost hourly rate
        """
        for order in self:
            if order.nox_product1:
                if order.nox_product1.lst_price != order.nox_sales_hourly_rate:
                    order.nox_product1.write({'lst_price': order.nox_sales_hourly_rate})

                #update vendor's price
                for seller in order.nox_product1.seller_ids:
                    seller.write({'price': order.nox_cost_hourly_rate})

            if order.nox_product2:
                if order.nox_product2.lst_price != order.nox_sales_hourly_rate2:
                    order.nox_product2.write({'lst_price': order.nox_sales_hourly_rate2})
                    
                #update vendor's price
                for seller in order.nox_product2.seller_ids:
                    seller.write({'price': order.nox_cost_hourly_rate2})
