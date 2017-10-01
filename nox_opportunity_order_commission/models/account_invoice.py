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

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    def _prepare_invoice_line_from_po_line(self, line):
        """Compute Vendor Bill's quantity (vendor bill related to Commission Order only) from Vendor bills related to 
        purchase orders and these purchase orders related to same Sales Order as Commission Order is related to.
        """
        data = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        context = self.env.context or {}
        if context.get('active_model', '') == 'purchase.order':
            purchase = self.env['purchase.order'].browse(context.get('active_ids', []))
            if purchase and purchase.commission_sale_id:
                po_ids, qty = [], 0.0
                for commission_sale_id in purchase.commission_sale_id:
                    for po_rel in commission_sale_id.purchase_line_ids:
                        po_ids.append(po_rel.order_id)
                    po_ids = list(set(po_ids))
                for po in po_ids:
                    for bill in po.invoice_ids:
                        if bill.state in ('open', 'paid'):
                            for bill_line in bill.invoice_line_ids:
                                qty += bill_line.quantity

                data['quantity'] = qty

        return data