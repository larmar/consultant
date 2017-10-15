# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime
import calendar

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def default_get(self, default_fields):
        """Set Vendor Bill Invoice Date as the last day of the month; if Current Date is between 1 to 10th of the month.
        Otherwise set current Date.
        """
        res = super(AccountInvoice, self).default_get(default_fields)
        if 'type' in res and res['type'] == 'in_invoice':
            current_date = datetime.now().date()
            year, month = current_date.year, current_date.month

            if current_date.day <= 10:
                month = month - 1
            if month == 0:
                month = 12
                year = year - 1

            if current_date.day <= 10:
                lastDayofMonth = calendar.monthrange(year, month)[1]
            else:
                lastDayofMonth = current_date.day
            
            invoice_date = str(year) + '-' + str(month) + '-' + str(lastDayofMonth)
            invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').date()
            invoice_date = invoice_date.strftime('%Y-%m-%d')

            res.update({'date_invoice': invoice_date})

            #set due date based on payment term
            pterm = res.get('payment_term_id', False)
            partner_id = False
            if not pterm:
                if 'purchase_id' in res:
                    partner_id = self.env['purchase.order'].browse([res['purchase_id']])[0].partner_id
                if 'partner_id' in res:
                    partner_id = self.env['res.partner'].browse([res['partner_id']])
                if partner_id:
                    pterm = partner_id.property_supplier_payment_term_id
            if pterm:
                currency_id = res.get('currency_id', False)
                pterm_list = pterm.with_context(currency_id=currency_id).compute(value=1, date_ref=invoice_date)[0]
                res.update({'date_due': max(line[0] for line in pterm_list)})
        return res

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('account_analytic_id')
    def _onchange_account_analytic_id(self):
        if self.invoice_id.origin:
            purchase_id = self.env['purchase.order'].search([('name','=',self.invoice_id.origin)])
            account_analytic_id = False
            if purchase_id and purchase_id.sale_id:
                for line in purchase_id.order_line:
                    account_analytic_id = line.account_analytic_id and line.account_analytic_id.id or False
                    break
                self.account_analytic_id = account_analytic_id