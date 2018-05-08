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
        """Compute accumulated Delivered Quantity in Sales Order lines with Consultant Product from related PO > Vendor Bills
        """
        for sale in self:
            product_list, po_ids, expense_product_list = {}, [], {}
            for line in sale.order_line:
                # check for consultant (standard) product & non-standard product
                if line.product_id and line.product_id.consultant_product or line.product_id.non_standard_product and line.product_id.id not in product_list:
                    product_list[line.product_id.id] = 0
                # check for expense product (by comparing product and unit price from sale order in vendor bill):
                elif line.product_id and not line.product_id.consultant_product and not line.product_id.non_standard_product:
                    expense_product_key = '-'.join([str(line.product_id.id), str(line.price_unit)])
                    if expense_product_key not in expense_product_list:
                        expense_product_list[expense_product_key] = 0
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
            lines_freeze = []
            for line2 in sale.order_line:
                if line2.product_id.id not in lines_freeze and line2.product_id.id in product_list.keys():
                    line2.with_context(allow_write=True).write({'qty_delivered': product_list[line2.product_id.id]})
                    lines_freeze.append(line2.product_id.id)
        
        	# check for expense product (by comparing product and unit price from sale order in vendor bill): update delivered qty
            for po in po_ids:
                for bill in po.invoice_ids:
                    if bill.state in ('open', 'paid'):
                        for line in bill.invoice_line_ids:
                            product_key = '-'.join([str(line.product_id.id), str(line.price_unit)])
                            if product_key in expense_product_list.keys():
                                qty = line.quantity
                                if bill.type == 'in_refund':
                                    qty = -line.quantity
                                expense_product_list[product_key] += qty

            #update delivered qty for expense product
            lines_freeze = []
            for line3 in sale.order_line:
                line_pkey = '-'.join([str(line3.product_id.id), str(line3.price_unit)])
                if line_pkey not in lines_freeze and line_pkey in expense_product_list.keys():
                    line3.with_context(allow_write=True).write({'qty_delivered': expense_product_list[line_pkey]})
                    lines_freeze.append(line_pkey)	

            # # update quantity on validating refund bill:
            # product_list, po_ids = {}, []
            # for line in sale.order_line:
            #     if line.product_id and not line.product_id.consultant_product and line.product_id.id not in product_list:
            #         product_list[str(line.product_id.id) + '_' + str(line.price_unit)] = 0
            
            # temp = [po_ids.append(pol.order_id) for pol in sale.purchase_line_ids]
            # for po in po_ids:
            #     for bill in po.invoice_ids:
            #         if bill.state in ('open', 'paid') and bill.type in ('in_invoice', 'in_refund'):
            #             for line in bill.invoice_line_ids:
            #                 linekey = str(line.product_id.id) + '_' + str(line.price_unit)
            #                 if linekey in product_list.keys():
            #                     qty = line.quantity
            #                     if bill.type == 'in_refund':
            #                         qty = -line.quantity
            #                     product_list[linekey] += qty
            
            # #update delivered qty:
            # for line2 in sale.order_line:
            #     linekey = str(line2.product_id.id) + '_' + str(line2.price_unit)
            #     if line2.product_id and not line2.product_id.consultant_product and linekey in product_list.keys():
            #         line2.write({'qty_delivered': product_list[linekey]})
        return True

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def create(self, vals):
        """Remove PO number from order line description for non-standard product; line created automatically from Vendor Bill
        """
        if not vals:
            vals = {}

        product_id = vals.get('product_id', False)
        if product_id:
            product_name = self.env['product.product'].browse([product_id])[0].name

        description = vals.get('name', '')
        desc = description.split(':')
        if len(desc) > 1:
            newdesc = desc[1:].pop().strip()
            if newdesc == product_name:
                vals['name'] = product_name

        return super(SaleOrderLine, self).create(vals)


    @api.multi
    def write(self, vals):
        """Re-compute Delivered Quantity if its attempted to update using odoo default
        """
        res = super(SaleOrderLine, self).write(vals)
        if not vals: vals = {}
        if vals.get('qty_delivered', '') and 'allow_write' not in self.env.context:
            order_id = self.order_id or False
            if order_id:
                order_id.recompute_so_delivered_qty()
        return res
