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

import logging
_logger = logging.getLogger(__name__)

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

    @api.multi
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
            po_ids = list(set(po_ids))
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
                            price_unit = line.product_id.get_product_price_by_invoice_policy(line.price_unit)
                            product_key = '-'.join([str(line.product_id.id), str(price_unit)])
                            if product_key in expense_product_list.keys():
                                qty = line.quantity
                                if bill.type == 'in_refund':
                                    qty = -line.quantity
                                expense_product_list[product_key] += qty

            #update delivered qty for expense product
            lines_freeze = []
            for line3 in sale.order_line:
                price_unit = line3.product_id.get_product_price_by_invoice_policy(line3.price_unit)
                line_pkey = '-'.join([str(line3.product_id.id), str(price_unit)])
                if line_pkey not in lines_freeze and line_pkey in expense_product_list.keys():
                    line3.with_context(allow_write=True).write({'qty_delivered': expense_product_list[line_pkey]})
                    lines_freeze.append(line_pkey)	

            # UPDATE INVOICED QUANTITY IN SOL
            product_list, expense_product_list = {}, {}
            for line4 in sale.order_line:
                # check for consultant (standard) product & non-standard product
                if line4.product_id and line4.product_id.consultant_product or line4.product_id.non_standard_product and line4.product_id.id not in product_list:
                    product_list[line4.product_id.id] = 0
                # check for expense product (by comparing product and unit price from sale order in vendor bill):
                elif line4.product_id and not line4.product_id.consultant_product and not line4.product_id.non_standard_product:
                    price_unit = line4.product_id.get_product_price_by_invoice_policy(line4.price_unit)
                    expense_product_key = '-'.join([str(line4.product_id.id), str(price_unit)])
                    if expense_product_key not in expense_product_list:
                        expense_product_list[expense_product_key] = 0
           
            #get sale customer invoices
            for inv in sale.invoice_ids:
                if inv.state in ('open', 'paid'):
                    for il in inv.invoice_line_ids:
                        if il.product_id.id in product_list.keys():
                            qty = 0
                            if inv.type == 'out_invoice':
                                qty = il.quantity
                            if inv.type == 'out_refund':
                                qty = -il.quantity
                            product_list[il.product_id.id] += qty 

            #update invoiced qty:
            lines_freeze = []
            for line5 in sale.order_line:
                if line5.product_id.id not in lines_freeze and line5.product_id.id in product_list.keys():
                    line5.with_context(allow_write=True).write({'qty_invoiced': product_list[line5.product_id.id]})
                    lines_freeze.append(line5.product_id.id)

            #update invoiced qty for expense products
            for inv2 in sale.invoice_ids:
                if inv2.state in ('open', 'paid'):
                    for iline in inv2.invoice_line_ids:
                        price_unit = iline.product_id.get_product_price_by_invoice_policy(iline.price_unit)
                        product_key = '-'.join([str(iline.product_id.id), str(price_unit)])
                        if product_key in expense_product_list.keys():
                            qty = 0
                            if inv2.type == 'out_invoice':
                                qty = iline.quantity
                            if inv2.type == 'out_refund':
                                qty = -iline.quantity
                            expense_product_list[product_key] += qty 
            #update delivered qty for expense product
            lines_freeze = []
            for sline in sale.order_line:
                price_unit = iline.product_id.get_product_price_by_invoice_policy(sline.price_unit)
                line_pkey = '-'.join([str(sline.product_id.id), str(price_unit)])
                if line_pkey not in lines_freeze and line_pkey in expense_product_list.keys():
                    sline.with_context(allow_write=True).write({'qty_invoiced': expense_product_list[line_pkey]})
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

    @api.model
    def cron_update_so_quantities(self):
        _logger.info("Scheduler function to recompute Delivered & Invoiced quantity in Sales Order has started!")
        so_ids = self.search([('state','=','sale')])
        so_ids.recompute_so_delivered_qty()
        result = []
        temp = [result.append(s.id) for s in so_ids]
        _logger.info("Scheduler function successfully executed on Sales Orders %s"%(result))

    @api.multi
    def action_map_lines_by_vendor_bills(self):
        """check if all non-standard/expense products in Sales > PO > Vendor Bills with respect to Unit Price are all linked in Sales Order with correct unit price
        """ 
        for sale in self:
            po_ids = []
            temp = [po_ids.append(pol.order_id) for pol in sale.purchase_line_ids]
            po_ids = list(set(po_ids))

            product_keys = []
            for po in po_ids:
                for bill in po.invoice_ids:
                    if bill.state in ('open', 'paid'):
                        for line in bill.invoice_line_ids:
                            if not line.product_id.consultant_product:
                                key = '^'.join([str(line.product_id.id), str(line.price_unit)])
                                product_keys.append(key)
            product_keys = list(set(product_keys))
            
            sales_tax = self.env['ir.model.data'].xmlid_to_res_id('l10n_se.' + str(self.env.user.company_id) + '_sale_tax_25_services')
            if not sales_tax:
                sales_tax = 0

            for pkey in product_keys:
                vals = pkey.split('^')
                lines_freeze = []

                Product = self.env['product.product'].browse([int(vals[0])])
                price_unit = Product.get_product_price_by_invoice_policy(float(vals[1]))
                line_item = self.env['sale.order.line'].search_read([('product_id','=',int(vals[0])), ('price_unit','=',price_unit), ('order_id','=',sale.id)])
                if not line_item:
                    lineid_item = self.env['sale.order.line'].search([('product_id','=',int(vals[0])), ('order_id','=',sale.id), ('id','not in',lines_freeze)], limit=1) 
                    if lineid_item:
                        lineid_item.write({'price_unit': price_unit})
                        lines_freeze.append(lineid_item.id)
                    else:
                        self.env['sale.order.line'].create({
                                'product_id': int(vals[0]),
                                'name': Product.name,
                                'product_uom': Product.uom_id.id,
                                'price_unit': price_unit,
                                'tax_id': [[6, 0, [sales_tax]]],
                                'order_id': sale.id,
                            })
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
        """Re-compute Delivered/Invoiced Quantity if its attempted to update using odoo default
        """
        res = super(SaleOrderLine, self).write(vals)
        if not vals: vals = {}
        if vals.get('qty_delivered', '') and 'allow_write' not in self.env.context:
            order_id = self.order_id or False
            if order_id:
                order_id.recompute_so_delivered_qty()
        if vals.get('qty_invoiced', '') and 'allow_write' not in self.env.context:
            order_id = self.order_id or False
            if order_id:
                order_id.recompute_so_delivered_qty()
        return res
