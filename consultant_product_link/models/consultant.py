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

import logging
_logger = logging.getLogger(__name__)

class ConsultantConsult(models.Model):
    _inherit = "consultant.consult"

    product_ids = fields.Many2many('product.product', string='Products', compute="_get_products", store=False, copy=False)
    sale_order_ids = fields.Many2many('sale.order', string='Sales Orders', compute="_get_orders", store=False, copy=False, help="Sale Order associated with related Consultant Product.")
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Orders', compute="_get_orders", store=False, copy=False, help="Sale Order associated with related Consultant Product.")

    sale_line_ids = fields.One2many('sale.order.line', 'consultant_id', 'Sale Order Lines', readonly=True)
    sale_order_id = fields.Many2one('sale.order', related='sale_line_ids.order_id', string="Sales Order")
    
    total_sale_orders = fields.Integer(compute='_get_orders', string='Total Sale Orders', store=False)
    total_purchase_orders = fields.Integer(compute='_get_orders', string='Total Purchase Orders', store=False)

    @api.multi
    def create_consultant_product(self, Consultant):
        """This function creates and links a Product with given Consultant Card
        """
        User = self.env['res.users'].browse([self._uid])

        vendor_id = Consultant.partner_id and Consultant.partner_id.id or False
        consultant_name = Consultant.name

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

        return Product


    @api.multi
    def _get_orders(self):
        for consultant in self:
            consultant_products, sale_order_ids, purchase_order_ids = [], [], []

            #search products using with_context to bypass products filtering done in def search
            products = self.env['product.product'].with_context(show_consultant_product_template=True).search_read([('consultant_id', '=', consultant.id)], fields=['id'])
            for prod in products:
                consultant_products.append(prod['id'])

            consultant_orders = self.env['sale.order.line'].search([('product_id', 'in', consultant_products)])
            temp = [sale_order_ids.append(sale.order_id.id) for sale in consultant_orders]
            sale_order_ids = list(set(sale_order_ids))
            consultant.sale_order_ids = sale_order_ids
            consultant.total_sale_orders = len(sale_order_ids)

            consultant_orders = self.env['purchase.order.line'].search([('product_id', 'in', consultant_products)])
            temp = [purchase_order_ids.append(purchase.order_id.id) for purchase in consultant_orders]
            purchase_order_ids = list(set(purchase_order_ids))
            consultant.purchase_order_ids = purchase_order_ids
            consultant.total_purchase_orders = len(purchase_order_ids)

    @api.multi
    def auto_set_consultant_stage(self):
        valid = False
        today = datetime.now().date()
        for consultant in self:
            for order in consultant.sale_order_ids:
                if order.state in ('draft', 'sent', 'sale'):
                    if order.nox_is_enddate:
                        order_end_date = datetime.strptime(order.nox_is_enddate, '%Y-%m-%d').date()
                        if order_end_date >= today:
                            valid = True
                            break
                    else:
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
            stage_id = self.env['consultant.stage'].search([('name', 'ilike', 'offered')], limit=1)
        return stage_id and stage_id.id or False

    @api.multi
    def action_open_sale_orders(self):
        for consultant in self:
            action = consultant.env.ref('sale.action_orders').read()[0]
            order_ids = []
            temp = [order_ids.append(sale.id) for sale in consultant.sale_order_ids]
            action['domain'] = [['id','in',order_ids]]
            action['context'] = {'show_sale': True}
            return action

    @api.multi
    def action_open_purchase_orders(self):
        for consultant in self:
            action = consultant.env.ref('purchase.purchase_form_action').read()[0]
            order_ids = []
            temp = [order_ids.append(po.id) for po in consultant.purchase_order_ids]
            action['domain'] = [['id','in',order_ids]]
            action['context'] = {'show_purchase': False}
            return action