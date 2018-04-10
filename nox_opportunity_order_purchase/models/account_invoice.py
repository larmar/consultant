# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, api

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, vals):
        for invoice in self:
            if not vals:
                vals = {}
            res = super(AccountInvoice, invoice).write(vals)
            sale_ids = []
            if vals.get('state', '') and invoice.type in ('in_invoice', 'in_refund'):
                temp = [sale_ids.append(line.purchase_line_id.sale_id) for line in invoice.invoice_line_ids if line.purchase_line_id and line.purchase_line_id.sale_id]
            for sale in sale_ids:
                sale.with_context(invoice_type=invoice.type).recompute_so_delivered_qty()
            return res
                
    @api.model
    def create(self, vals):
        """On Credit Invoice, set Reference/Description with Customer Reference value of sourcing invoice instead of Reason
        """
        context = self.env.context or {}
        if context.get('active_model', '') == 'account.invoice':
            invoice = self.browse(context['active_ids'])[0]
            if invoice.type == 'out_invoice':
                vals['name'] = invoice.name
        return super(AccountInvoice, self).create(vals)