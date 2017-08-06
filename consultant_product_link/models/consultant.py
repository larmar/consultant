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

class ConsultantConsult(models.Model):
    _inherit = "consultant.consult"

    product_id = fields.Many2one('product.product', 'Related Product', readonly=True, copy=False)
    sale_order_ids = fields.Many2many('sale.order', string='Sales Orders', compute="_get_orders", store=False, copy=False, help="Sale Order associated with related Consultant Product.")
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Orders', compute="_get_orders", store=False, copy=False, help="Sale Order associated with related Consultant Product.")

    @api.multi
    def action_link_product(self):
        for consultant in self:
            if consultant.product_id:
                raise ValidationError(_('Consultant %s already has Linked Product.')%(consultant.name))
            product_id = self.env['product.product'].create({
                                                        'name': consultant.name,
                                                        'type': 'consu',
                                                    })
            consultant.write({'product_id': product_id.id})

    @api.multi
    def _get_orders(self):
        for consultant in self:
            if consultant.product_id:
                sale_line_ids = self.env['sale.order.line'].search([('product_id', '=', consultant.product_id.id)])
                sale_order_ids = []
                temp = [sale_order_ids.append(line.order_id.id) for line in sale_line_ids]
                consultant.sale_order_ids = sale_order_ids

                purchase_line_ids = self.env['purchase.order.line'].search([('product_id', '=', consultant.product_id.id)])
                purchase_order_ids = []
                temp = [purchase_order_ids.append(line.order_id.id) for line in purchase_line_ids]
                consultant.purchase_order_ids = purchase_order_ids
