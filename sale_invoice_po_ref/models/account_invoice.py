# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def get_sale_customer_po_ref(self):
        """Compute Sales Order Id to get Customer PO Number in Invoice report
        """
        for invoice in self:
            #1. search sales order reference from Origin
            if invoice.origin:
                sale_id = invoice.env['sale.order'].search([('name', '=', invoice.origin)])
                if sale_id:
                    return sale_id[0].customer_po_ref

            #2. search sales order reference from sales order line <> invoice line relations 
            po_order_ref = False
            invoice_lines = []
            temp = [invoice_lines.append(line.id) for line in invoice.invoice_line_ids]
            if invoice_lines:
                for inv_line_id in invoice_lines:
                    invoice._cr.execute(""" select order_line_id from sale_order_line_invoice_rel where invoice_line_id = %s"""%(inv_line_id))
                    order_line_id = invoice._cr.fetchone()
                    if order_line_id:
                        po_order_ref = invoice.env['sale.order.line'].search([('id', '=', list(order_line_id)[0])]).order_id.customer_po_ref
                        break
            return po_order_ref