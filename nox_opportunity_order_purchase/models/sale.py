# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def create_purchase_order(self, order_id, vals):
        """Override function defined in sale_purchase_b2b app; to set Start Date & End Date from Sales Order when Purchase Order is created from SO
        """
        purchase_id = super(SaleOrder, self).create_purchase_order(order_id, vals)
        purchase_id.write({
                    'nox_is_startdate': order_id.nox_is_startdate,
                    'nox_is_enddate': order_id.nox_is_enddate,
                    })
        return purchase_id

    @api.multi
    def write(self, vals):
        """Update Start Date | End Date on related Purchase Orders
        """
        if not vals: vals = {}

        for sale in self:
            nox_is_startdate, nox_is_enddate = '', ''
            if vals.get('nox_is_startdate', ''):
                nox_is_startdate = vals['nox_is_startdate']
            if vals.get('nox_is_enddate', ''):
                nox_is_enddate = vals['nox_is_enddate']

            po_vals = {}
            if nox_is_startdate:
                po_vals['nox_is_startdate'] = nox_is_startdate
            if nox_is_enddate:
                po_vals['nox_is_enddate'] = nox_is_enddate

            if po_vals:
                po_ids = []
                temp = [po_ids.append(pol.order_id) for pol in sale.purchase_line_ids]
                po_ids = list(set(po_ids))
                for po in po_ids:
                    po.write(po_vals)

        return super(SaleOrder, self).write(vals)

    @api.one
    def recompute_so_delivered_qty(self):
        for sale in self:
            product_list, po_ids = {}, []
            for line in sale.order_line:
                if line.product_id.id not in product_list:
                    product_list[line.product_id.id] = 0
            temp = [po_ids.append(pol.order_id) for pol in sale.purchase_line_ids]
            for po in po_ids:
                for bill in po.invoice_ids:
                    if bill.state in ('open', 'paid'):
                        for line in bill.invoice_line_ids:
                            if line.product_id.id in product_list.keys():
                                qty = line.quantity
                                if bill.type == 'in_refund':
                                    qty = -line.quantity
                                product_list[line.product_id.id] += qty
            #update delivered qty:
            for line2 in sale.order_line:
                line2.write({'qty_delivered': product_list[line.product_id.id]})
        return True

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _compute_analytic(self, domain=None):
        """Update Delivered Quantity in Sales Order line when Vendor Bill related to PO related to SO is Validated.
            - Compute Delivered quantity by deducting Refund Vendor Bill quantity
        """
        lines = {}
        context = self.env.context or {}
        if context.get('type', '') == 'in_invoice':
            # reset delivered quantity:
            self.order_id.recompute_so_delivered_qty()
        else:
            return super(SaleOrderLine, self)._compute_analytic(domain=domain)
