# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import fields, models, api
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    #redefine field to change Locked to Closed for done stage
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Closed'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def default_get(self, fields):
        """Restrict Vendor bill from Closed PO
        """
        context = self.env.context or {}
        res = super(AccountInvoice, self).default_get(fields)

        if 'type' in res and res['type'] in ('in_invoice', 'in_refund'):
            if context.get('active_model', '') == 'purchase.order' and context.get('active_ids', []):
                po_state = self.env['purchase.order'].browse(context['active_ids'])[0].state
                if po_state and po_state == 'done':
                    raise ValidationError('Access Denied!\n\nYou cannot create Invoice for Closed Purchase Order.')
        return res
        