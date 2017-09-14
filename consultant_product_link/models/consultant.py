# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

from odoo.tools.translate import _

class ConsultantConsult(models.Model):
    _inherit = "consultant.consult"

    product_id = fields.Many2one('product.product', 'Related Product', readonly=True, copy=False)
    sale_order_ids = fields.Many2many('sale.order', string='Sales Orders', compute="_get_orders", store=False, copy=False, help="Sale Order associated with related Consultant Product.")
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Orders', compute="_get_orders", store=False, copy=False, help="Sale Order associated with related Consultant Product.")

    @api.model
    def create(self, vals):
        User = self.env['res.users'].browse([self._uid])
        if not vals:
            vals = {}

        vendor_id = vals.get('partner_id', False)
        consultant_name = vals.get('name', '')

        # Create product
        Product = self.env['product.product'].create({
                                                'name': consultant_name,
                                                'sale_ok': True,
                                                'purchase_ok': True,
                                                'type': 'service',
                                                'list_price': 0.0,
                                                'standard_price': 0.0,
                                                
                                                'can_be_expensed': True,
                                                'invoice_policy': 'delivery',
                                                'expense_policy': 'sales_price',
                                                'track_service': 'manual',


                                            })
        # Link Product on Consultant
        vals['product_id'] = Product.id

        # Update UOM, Purchase UOM and Internal Category of Product
        update_vals = {}
        hour_uom = self.env['ir.model.data'].xmlid_to_res_id('product.product_uom_hour')
        if hour_uom:
            update_vals = {'uom_id': hour_uom, 'uom_po_id': hour_uom}

        categ_id = self.env['product.category'].search([('name', '=', 'Consultancy')])
        if categ_id:
            categ_id = categ_id[0].id
        else:
            categ_id = self.env['ir.model.data'].xmlid_to_res_id('product.product_category_1')
        if categ_id:
            update_vals['categ_id'] = categ_id

        # Set Default Purchase tax as Vendor tax on Product:
        product_vendor_tax = self.env['ir.values'].get_default('product.template', 'supplier_taxes_id', company_id = User.company_id.id)
        if product_vendor_tax:
            update_vals['supplier_taxes_id'] = [[6, 0, product_vendor_tax]]

        Product.write(update_vals)

        # Set Vendor on Product
        if vendor_id:
            self.env['product.supplierinfo'].create({'name': vendor_id, 'product_tmpl_id': Product.product_tmpl_id.id})

        return super(ConsultantConsult, self).create(vals)

    @api.multi
    def write(self, vals):
        """Update related Product name and/or Vendor
        """
        if not vals: vals = {}

        if 'name' in vals and vals['name']:
            if self.product_id:
                self.product_id.write({'name': vals['name']})
        if 'partner_id' in vals and vals['partner_id']:
            if self.product_id:
                #delete existing Product Vendor(s):
                for Seller in self.product_id.seller_ids:
                    Seller.unlink()
                #create new Product Vendor:
                self.env['product.supplierinfo'].create({'name': vals['partner_id'], 'product_tmpl_id': self.product_id.product_tmpl_id.id})
        return super(ConsultantConsult, self).write(vals)

    @api.multi
    def _get_orders(self):
        for consultant in self:
            if consultant.product_id:
                sale_line_ids = self.env['sale.order.line'].search([('product_id', '=', consultant.product_id.id)])
                sale_order_ids = []
                temp = [sale_order_ids.append(line.order_id.id) for line in sale_line_ids]
                consultant.sale_order_ids = sale_order_ids
                #auto set consultant stage based on related Sales Order's expiration date
                if sale_order_ids:
                    consultant.auto_set_consultant_stage()

                purchase_line_ids = self.env['purchase.order.line'].search([('product_id', '=', consultant.product_id.id)])
                purchase_order_ids = []
                temp = [purchase_order_ids.append(line.order_id.id) for line in purchase_line_ids]
                consultant.purchase_order_ids = purchase_order_ids

    @api.multi
    def auto_set_consultant_stage(self):
        valid = False
        today = datetime.now().date()
        for consultant in self:
            for order in consultant.sale_order_ids:
                if order.validity_date:
                    expiration_date = datetime.strptime(order.validity_date, '%Y-%m-%d').date()
                    if expiration_date >= today:
                        valid = True
                        break

            stage = self.get_consultant_valid_stages(valid)
            if stage:
                consultant.write({'stage_id': stage})

    @api.multi
    def get_consultant_valid_stages(self, valid=False):
        stage_id = False
        if valid:
            #stage_id = self._cr.execute("select id from consultant_stage where name ilike '%%on nox contract%%'")
            stage_id = self.env['consultant.stage'].search([('name', 'ilike', 'on nox contract')], limit=1)
        else:
            stage_id = self.env['consultant.stage'].search([('name', 'ilike', 'sale ready')], limit=1)
        return stage_id and stage_id.id or False