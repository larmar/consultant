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
        """Compute Vendor Bill's quantity (vendor bill related to Commission Order only) so that for the same related SO,
        all PO's Vendor bills (validated | paid) quantity is equal to the total quantity in all Commission Order Vendor Bills (validated | paid)
        """
        data = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        context = self.env.context or {}
        so_consultant_product = False
        if context.get('active_model', '') == 'purchase.order':
            def get_total_qty(po_ids, commission_order=False):
                """Get total PO > Invoice > Line > Product qty if Product = SO > Line > Consultant Product
                """
                qty = 0.0
                for po in po_ids:
                    for bill in po.invoice_ids:
                        if bill.state in ('open', 'paid'):
                            for bill_line in bill.invoice_line_ids:
                                #for invoices related to commission orders
                                if commission_order and bill_line.product_id.is_commission_product:
                                    if bill.type == 'in_refund':
                                        qty -= bill_line.quantity
                                    else:
                                        qty += bill_line.quantity
                                #for invoices related to PO's
                                elif bill_line.product_id and bill_line.product_id.id == so_consultant_product:
                                    qty += bill_line.quantity
                return qty

            purchase = self.env['purchase.order'].browse(context.get('active_ids', []))
            if purchase and purchase.commission_sale_id:
                po_ids, po_bill_qty, commission_po_ids, commission_bill_qty, bill_to_qty = [], 0, [], 0, 0
                for commission_sale_id in purchase.commission_sale_id:
                    #get Product related to Consultant from Sales Order; get only first Consultant Product (TODO: for multi consultant SO)
                    for sol in commission_sale_id.order_line:
                        if sol.consultant_line_check or sol.consultant_id:
                            so_consultant_product = sol.product_id.id
                            break

                    for po_rel in commission_sale_id.purchase_line_ids:
                        po_ids.append(po_rel.order_id)
                    po_ids = list(set(po_ids))
                    po_bill_qty = get_total_qty(po_ids)

                    for po_rel in commission_sale_id.commission_order_lines:
                        commission_po_ids.append(po_rel.order_id)
                    commission_po_ids = list(set(commission_po_ids))
                    commission_bill_qty = get_total_qty(commission_po_ids, True)

                    bill_to_qty = po_bill_qty - commission_bill_qty

                data['quantity'] = bill_to_qty

        #set Taxes (if applicable):
        if data and data.get('product_id', False):
            taxes = []
            product = self.env['product.product'].browse(data['product_id'])
            for tax in product.supplier_taxes_id:
                taxes.append(tax.id)
            if taxes:
                data['invoice_line_tax_ids'] = [[6, 0, taxes]]
                
        return data