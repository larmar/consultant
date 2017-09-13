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

    nox_product1 = fields.Many2one('product.product', 'Related Product 1')
    nox_product2 = fields.Many2one('product.product', 'Related Product 2')

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

                    'nox_cost_hourly_rate2': Opportunity.nox_cost_hourly_rate2,
                    'nox_ftepercent2': Opportunity.nox_ftepercent2,
                    'nox_ftepercent_temp2': Opportunity.nox_ftepercent_temp2,
                    'nox_sum_hours2': Opportunity.nox_sum_hours2,
                    'nox_sales_hourly_rate2': Opportunity.nox_sales_hourly_rate2,

                    'nox_product1': Opportunity.nox_product1 and Opportunity.nox_product1.id or False,
                    'nox_product2': Opportunity.nox_product2 and Opportunity.nox_product2.id or False,
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

        if self.nox_product1:
            self.validate_related_product_with_orderline(self.nox_product1, self.nox_sum_hours, self.nox_sales_hourly_rate, 1)
        if self.nox_product2:
            self.validate_related_product_with_orderline(self.nox_product2, self.nox_sum_hours2, self.nox_sales_hourly_rate2, 2)
        return res

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

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """Set default order lines with Consultants Product (from Opportunity)
        """
        res = super(SaleOrder, self).onchange_partner_id()
        context = self.env.context
        order_lines = []
        if 'active_model' in context and context['active_model'] == 'crm.lead' and context.get('default_opportunity_id', False):
            Opportunity = self.env['crm.lead'].browse(context['default_opportunity_id'])
            if Opportunity.nox_product1:
                order_lines.append({
                        'product_id': Opportunity.nox_product1.id,
                        'price_unit': Opportunity.nox_sales_hourly_rate,
                        'product_uom': Opportunity.nox_product1.uom_id.id,
                        'product_uom_qty': Opportunity.nox_sum_hours,
                        'name': Opportunity.nox_product1.name_get()[0][1],
                    })
            if Opportunity.nox_product2:
                order_lines.append({
                        'product_id': Opportunity.nox_product2.id,
                        'price_unit': Opportunity.nox_sales_hourly_rate2,
                        'product_uom': Opportunity.nox_product2.uom_id.id,
                        'product_uom_qty': Opportunity.nox_sum_hours2,
                        'name': Opportunity.nox_product2.name_get()[0][1],
                    })
        if order_lines:
            self.update({'order_line': order_lines})

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
