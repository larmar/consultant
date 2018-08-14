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
        if 'type' in res and res['type'] in ('in_invoice', 'out_invoice'):
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
                    res.update({'partner_id': partner_id.id})
            if pterm:
                currency_id = res.get('currency_id', False)
                pterm_list = pterm.with_context(currency_id=currency_id).compute(value=1, date_ref=invoice_date)[0]
                res.update({'date_due': max(line[0] for line in pterm_list), 'payment_term_id': pterm.id})
        return res

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """Override function to reset Due Date based on Vendor Payment Term which is being set to False on load of Vendor Bill from PO
        """
        date_due = self.date_due
        res = super(AccountInvoice, self)._onchange_partner_id()
        
        if date_due and self.partner_id.property_supplier_payment_term_id:
            self.date_due = date_due
        else:
            self.date_due = False
        return res

    @api.onchange('fiscal_position_id')
    def _compute_tax_id(self):
        """
        Trigger the recompute of the taxes if the fiscal position is changed on the Invoice
        """
        for invoice in self:
            invoice.invoice_line_ids._compute_tax_id()

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

    @api.multi
    def _compute_tax_id(self):
        for line in self:
            """Function to reset Taxes based on Fiscal position of the partner
            """
            fpos = line.invoice_id.fiscal_position_id or line.invoice_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            if line.invoice_id.type in ('in_invoice', 'in_refund'):
                taxes = line.product_id.supplier_taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            else:
                taxes = line.product_id.taxes_id.filtered(lambda r: not line.company_id or r.company_id == line.company_id)
            if taxes:
                line.invoice_line_tax_ids = fpos.map_tax(taxes, line.product_id, line.invoice_id.partner_id) if fpos else taxes
