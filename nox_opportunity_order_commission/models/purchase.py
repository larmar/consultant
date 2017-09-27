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

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    commission_sale_id = fields.Many2one('sale.order', 'Source Sales Order', copy=False)

    @api.model
    def create(self, vals):
        """Set Commission Order check on Sales Order if this is a Commission Order from SO.
        """
        if self.env.context and 'commission_order' in self.env.context:
            sale_id = self.env.context.get('default_commission_sale_id', False)
            if sale_id:
                self.env['sale.order'].browse([sale_id]).write({'has_commission_order': True})

        return super(PurchaseOrder, self).create(vals)

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    commission_sale_id = fields.Many2one('sale.order', 'Source Sales Order', copy=False)

    @api.multi
    def action_open_commission_order(self):
        for pol in self:
            return {
                'name': 'Commission Order',
                'type': 'ir.actions.act_window',   
                'res_model': 'purchase.order',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': pol.order_id.id,
                'target': 'current',
                }
