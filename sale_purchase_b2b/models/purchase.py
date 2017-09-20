# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    project_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    sale_id = fields.Many2one('sale.order', 'Sales Order')

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sale_id = fields.Many2one('sale.order', 'Sales Order')

    @api.onchange('sale_id')
    def _onchange_sale_id(self):
        """Set Sales order reference on PO lines 
        """
        if self.order_id and self.order_id.sale_id:
            self.sale_id = self.order_id.sale_id
            
    @api.multi
    def action_open_po(self):
        for pol in self:
            name = 'Request for Quotation'
            if pol.order_id.state not in ('draft', 'sent'):
                name = 'Purchase Order'
            
            return {
                'name': name,
                'type': 'ir.actions.act_window',   
                'res_model': 'purchase.order',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': pol.order_id.id,
                'target': 'current',
                }
