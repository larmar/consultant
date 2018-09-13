# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta as rdelta
from calendar import monthrange
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    nox_contract_signed = fields.Boolean('Contract Signed', copy=False)
    nox_is_startdate = fields.Date("Start Date", copy=False)
    nox_is_enddate = fields.Date("End Date", copy=False)

    nox_sale_partner_id = fields.Many2one(related="sale_id.partner_id", string="Customer", store=False)
    nox_sale_consultants = fields.Char(related="sale_id.consultant_names", string="Consultants", store=False)

    date_search_po_bills = fields.Date('Bills not received for month')

    @api.model
    def default_get(self, fields):
        """Set Start Date & End Date from Sales Order when Purchase Order is created from SO
        """
        res = super(PurchaseOrder, self).default_get(fields)

        context = self._context
        if isinstance(context, dict) and context.get('active_model', False) == 'sale.order':
            Sale = self.env['sale.order'].browse(context['active_ids'])
            if Sale:
                res.update({
                    'nox_is_startdate': Sale.nox_is_startdate,
                    'nox_is_enddate': Sale.nox_is_enddate,
                })
        return res

    @api.multi
    def write(self, vals):
        """Set Contract Signed unticked on changing End Date
        """
        if not vals: vals = {}
        if 'nox_is_enddate' in vals:
            vals['nox_contract_signed'] = False
        return super(PurchaseOrder, self).write(vals)

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Search Filters: Not Started | Started | Ended
        """
        context = self.env.context or {}
        filter_flag, ids = False, []
        if context.get('nox_not_started', False):
            filter_flag = True
            now = datetime.now().date()
            self._cr.execute("""select id from purchase_order 
                                    where nox_is_startdate > '%s'"""%(now))
            result = self._cr.fetchall()
            for res in result:
                ids.append(res[0])
        
        if context.get('nox_started', False):
            filter_flag = True
            now = datetime.now().date()
            self._cr.execute("""select id from purchase_order 
                                    where nox_is_startdate <= '%s' and
                                    nox_is_enddate > '%s'"""%(now, now))
            result = self._cr.fetchall()
            for res in result:
                ids.append(res[0])
        
        if context.get('nox_ended', False):
            filter_flag = True
            now = datetime.now().date()
            self._cr.execute("""select id from purchase_order 
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

        if context.get('date_search_po_bills', False):
            """Filter Purchase orders for which Vendor Bills in selected month have not been registered
            - instead of calendar month, 2nd day of the selected month TO 1st day of the next month is checked
            """
            date_search_po_bill = datetime.strptime(context['date_search_po_bills'], '%Y-%m-%d').date()
            
            last_day = monthrange(date_search_po_bill.year, date_search_po_bill.month)[1]

            start_date = date_search_po_bill.replace(day=2)
            end_date = date_search_po_bill.replace(day=last_day) + timedelta(days=1)

            self._cr.execute("""select id from purchase_order where
                                    state in ('purchase')"""
                            )
            result = self._cr.fetchall()

            po_ids, orders = [], []
            temp = [orders.append(res[0]) for res in result]
            for po in self.browse(orders):
                if not po.invoice_ids:
                    po_ids.append(po.id)
                
                flag = True
                for invoice in po.invoice_ids:
                    if invoice.date_invoice:
                        invoice_date = datetime.strptime(invoice.date_invoice, "%Y-%m-%d").date()
                        if invoice_date >= start_date and invoice_date <= end_date and invoice.state in ('open', 'paid'):
                            flag = False
                            break
                if flag:
                    po_ids.append(po.id)
            po_ids = list(set(po_ids))

            if not args:
                args = [['id','in',po_ids]]
            else:
                args.append(['id','in',po_ids])

            #remove date_search_po_bills from domain:
            result = []
            for res in args:
                if res[0] != 'date_search_po_bills':
                    result.append(res)
            args = result
        return super(PurchaseOrder, self).search(args, offset, limit, order, count)

    @api.multi
    def action_add_nonstandard_product(self):
        for po in self:
            consultant, consultant_product, account_analytic_id, sales_hourly_rate, cost_hourly_rate, taxes  = False, False, False, 0, 0, []
            Order = po.sale_id or False
            if Order:
                sales_hourly_rate, cost_hourly_rate = Order.nox_sales_hourly_rate, Order.nox_cost_hourly_rate

            for line in po.order_line:
                if line.product_id and line.product_id.consultant_product and line.product_id.consultant_id:
                    consultant = line.product_id.consultant_id.id
                    consultant_product = line.product_id.id
                    account_analytic_id = line.account_analytic_id and line.account_analytic_id.id or False
                    temp = [taxes.append(tax.id) for tax in line.taxes_id]
                    break

            if not consultant:
                raise ValidationError(('Purchase Order %s is not related to any Consultant.'%(po.name)))

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'nonstandard.product.create',
                'name': 'Add Non-Standard Product',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                                'po': po.id,
                                'sale_id': Order.id,
                                'sales_hourly_rate': sales_hourly_rate,
                                'cost_hourly_rate': cost_hourly_rate,
                                'consultant': consultant,
                                'consultant_product': consultant_product,
                                'account_analytic_id': account_analytic_id,
                                'taxes': taxes
                            }
            }