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
            force_so_lines = self.env.context.get("force_so_lines")
            
            domain = [('so_line', 'in', self.ids)]

            data = self.env['account.analytic.line'].search_read(domain, fields=['so_line', 'unit_amount', 'product_uom_id', 'amount'])
            # If the unlinked analytic line was the last one on the SO line, the qty was not updated.
            if force_so_lines:
                for line in force_so_lines:
                    lines.setdefault(line, 0.0)

            for d in data:
                if not d['product_uom_id']:
                    continue
                line = self.browse(d['so_line'][0])
                lines.setdefault(line, 0.0)
                uom = self.env['product.uom'].browse(d['product_uom_id'][0])
                if line.product_uom.category_id == uom.category_id:
                    qty = uom._compute_quantity(d['unit_amount'], line.product_uom)
                else:
                    qty = d['unit_amount']
                
                if d['amount'] > 0:
                    qty = -qty
                
                lines[line] += qty

            for line, qty in lines.items():
                line.qty_delivered = qty
        else:
            return super(SaleOrderLine, self)._compute_analytic(domain=domain)
