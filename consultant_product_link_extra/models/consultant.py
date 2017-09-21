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

    product2_id = fields.Many2one('product.product', 'Related Product 2', readonly=True, copy=False)
    product3_id = fields.Many2one('product.product', 'Related Product 3', readonly=True, copy=False)

    @api.multi
    def _get_orders(self):
        for consultant in self:
            if consultant.product_id:
                sale_line_ids = self.env['sale.order.line'].search(['|','|',
                                                                ('product_id', '=', consultant.product_id.id), 
                                                                ('product_id', '=', consultant.product2_id.id), 
                                                                ('product_id', '=', consultant.product3_id.id)])
                sale_order_ids = []
                temp = [sale_order_ids.append(line.order_id.id) for line in sale_line_ids]
                consultant.sale_order_ids = sale_order_ids
                #auto set consultant stage based on related Sales Order's expiration date
                if sale_order_ids:
                    consultant.auto_set_consultant_stage()

                purchase_line_ids = self.env['purchase.order.line'].search(['|','|',
                                                                ('product_id', '=', consultant.product_id.id), 
                                                                ('product_id', '=', consultant.product2_id.id), 
                                                                ('product_id', '=', consultant.product3_id.id)])
                purchase_order_ids = []
                temp = [purchase_order_ids.append(line.order_id.id) for line in purchase_line_ids]
                consultant.purchase_order_ids = purchase_order_ids

    @api.multi
    def action_link_product2(self):
        for Consultant in self:
            if not Consultant.product2_id:
                Product2 = Consultant.create_consultant_product(Consultant)
                Consultant.write({'product2_id': Product2.id})
                _logger.info("Related Product 2 has been linked with Consultant. Id: %s | Consultant: %s"%(Consultant.id, Consultant.name))

    @api.multi
    def action_link_product3(self):
        for Consultant in self:
            if not Consultant.product3_id:
                Product3 = Consultant.create_consultant_product(Consultant)
                Consultant.write({'product3_id': Product3.id})
                _logger.info("Related Product 3 has been linked with Consultant. Id: %s | Consultant: %s"%(Consultant.id, Consultant.name))