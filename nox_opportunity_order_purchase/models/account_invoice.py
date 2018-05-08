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
            
            temp = [sale_ids.append(line.purchase_line_id.sale_id) for line in invoice.invoice_line_ids if line.purchase_line_id and line.purchase_line_id.sale_id]
                
            #get sale order reference from customer invoices to recompute delivered quantity
            invoice_lines = []
            temp = [invoice_lines.append(str(l.id)) for l in invoice.invoice_line_ids]

            order_ids, order_line_ids = [], []
            if invoice_lines:
                self._cr.execute("select order_line_id from sale_order_line_invoice_rel \
                                where invoice_line_id in (%s)"%(', '.join(invoice_lines)))
                result = self._cr.fetchall()
                temp = [order_line_ids.append(res[0]) for res in result]
                if order_line_ids:
                    lines = self.env['sale.order.line'].search_read([('id','in',order_line_ids)], fields=['order_id'])
                    temp = [order_ids.append(sale_line['order_id'][0]) for sale_line in lines]
                    for sale_order in order_ids:
                        sale_ids.append(self.env['sale.order'].browse([sale_order]))

            #get sale order reference from origin to recompute invoiced quantity
            so_refs = self.env['sale.order'].search([('name','=',invoice.origin)])
            for so_ref in so_refs:
                sale_ids.append(so_ref)

            sale_ids = list(set(sale_ids))
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
                vals['origin'] = invoice.origin
        res = super(AccountInvoice, self).create(vals)
        return res
