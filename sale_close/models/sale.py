# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    #redefine field to change Locked to Closed for done stage
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Closed'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def default_get(self, fields):
        context = self.env.context or {}
        if context.get('active_model', False) and context['active_model'] == 'sale.order':
            if self.env['sale.order'].browse(context['active_ids'])[0].state == 'done':
                raise ValidationError('Access Denied!\n\nYou cannot create Invoice for Closed Sales Order.')
        return super(SaleAdvancePaymentInv, self).default_get(fields)