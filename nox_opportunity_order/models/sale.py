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
import dateutil.relativedelta as rt

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

    @api.depends('nox_is_startdate')
    def _compute_followup_startdate(self):
        for order in self:
            date = False
            if order.nox_is_startdate:
                date = datetime.strptime(order.nox_is_startdate, "%Y-%m-%d") + rt.relativedelta(months=1)
            order.nox_followup_startdate = date

    @api.depends('nox_is_enddate')
    def _compute_followup_enddate(self):
        for order in self:
            date = False
            if order.nox_is_enddate:
                date = datetime.strptime(order.nox_is_enddate, "%Y-%m-%d") - rt.relativedelta(months=2)
            order.nox_followup_enddate = date

    nox_is_startdate = fields.Date("Start Date")
    nox_is_enddate = fields.Date("End Date")
    nox_cost_hourly_rate = fields.Float('Cost hourly rate')
    nox_ftepercent = fields.Float('Avg FTE (%)')
    nox_ftepercent_temp = fields.Float('Avg FTE (%)')
    nox_sum_hours = fields.Float(string='Total Hours', compute='_compute_nox_sum_hours', store=True)
    nox_sales_hourly_rate = fields.Float('Sales hourly rate')

    nox_followup_startdate = fields.Date(compute='_compute_followup_startdate', string='Start Follow-up Date', store=True)
    nox_followup_enddate = fields.Date(compute='_compute_followup_enddate', string='End Follow-up Date', store=True)

    nox_contract_signed = fields.Boolean('Contract Signed')

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
                    'nox_cost_hourly_rate': Opportunity.nox_cost_hourly_rate,
                    'nox_ftepercent': Opportunity.nox_ftepercent,
                    'nox_ftepercent_temp': Opportunity.nox_ftepercent_temp,
                    'nox_sum_hours': Opportunity.nox_sum_hours,
                    'nox_sales_hourly_rate': Opportunity.nox_sales_hourly_rate,                    
                })

            #create Order line items for each Consultant in onchange_partner

        return res

    @api.multi
    def write(self, vals):
        if 'nox_ftepercent_temp' in vals:
            vals['nox_ftepercent'] = vals['nox_ftepercent_temp']

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
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """Set default order lines with Consultants Product (from Opportunity)
        """
        res = super(SaleOrder, self).onchange_partner_id()
        context = self.env.context
        if 'active_model' in context and context['active_model'] == 'crm.lead' and context.get('default_opportunity_id', False):
            Opportunity = self.env['crm.lead'].browse([context['default_opportunity_id']])
            consultants,  order_lines = [], []
            temp = [consultants.append(consultant) for consultant in Opportunity.consultant_ids]

            temp_product = self.env['product.product'].search([('sale_ok','=',True)], limit=1) #to set default Tax on order line
            for consultant in consultants:
                hour_uom = self.env['ir.model.data'].xmlid_to_res_id('product.product_uom_hour')

                User = self.env['res.users'].browse([self._uid])
                taxes = []
                customer_default_tax = self.env['ir.values'].get_default('product.template', 'taxes_id', company_id = User.company_id.id)
                if customer_default_tax:
                    taxes = customer_default_tax
                line_data = {
                    'product_id': temp_product and temp_product.id or False,
                    'name': consultant.name,
                    'consultant_line_check': True,
                    'product_dummy_check': True,
                    'consultant_id': consultant.id,
                    'product_uom': hour_uom or False,
                    'price_unit': Opportunity.nox_sales_hourly_rate,
                    'product_uom_qty': Opportunity.nox_sum_hours,
                    'tax_id': [[6, 0, taxes]],
                }
                order_lines.append(line_data)

            if order_lines:
                self.update({'order_line': order_lines})

    @api.depends('order_line')
    def compute_consultant_names(self):
        for sale in self:
            consultant_names = []
            temp = [consultant_names.append(line.consultant_id.name) for line in sale.order_line if line.consultant_id]
            consultant_names = list(set(consultant_names))
            sale.consultant_names = ', '.join(consultant_names)

    @api.onchange('nox_ftepercent_temp')
    def onchange_nox_ftepercent(self):
        self.nox_ftepercent = self.nox_ftepercent_temp

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    consultant_line_check = fields.Boolean('Consultant Product Line?', help="If checked, Product and Description are not allowed to modify; Product is auto Created & set on Save.")
    consultant_id = fields.Many2one('consultant.consult', 'Related Consultant', copy=False)

    #dummy fields to hide original product id field if Order is created from Opportunity:
    product_dummy_id = fields.Many2one('product.product', 'Product(dummy)', readonly=False, copy=False)
    product_dummy_check = fields.Boolean('Product Check')

    @api.model
    def create(self, vals):
        """Create & Set Product for Consultant Order lines
        """
        sales_hourly_rate, cost_hourly_rate = 0, 0
        if vals.get('order_id', False):
            Order = self.env['sale.order'].browse([vals['order_id']])
            sales_hourly_rate, cost_hourly_rate = Order.nox_sales_hourly_rate, Order.nox_cost_hourly_rate
        if vals.get('consultant_line_check', False) and vals.get('consultant_id', False):
            product = self.env['consultant.consult'].browse([vals['consultant_id']]).with_context(sales_hourly_rate=sales_hourly_rate, cost_hourly_rate=cost_hourly_rate).create_order_line_product()
            vals['product_id'] = product.id
            vals['product_dummy_check'] = False
            vals['product_dummy_id'] = False
        return super(SaleOrderLine, self).create(vals)
