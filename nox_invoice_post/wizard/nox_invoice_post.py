# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class NoxInvoicePost(models.TransientModel):
    _name = "nox.invoice.post"
    _description = "Mark Customer Invoice(s) as Posted"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        invoice_ids = self.env.context.get('active_ids', [])
        if invoice_ids:
            flag = False
            for invoice in self.env['account.invoice'].browse(invoice_ids):
                if invoice.type != 'out_invoice':
                    flag = True
            if flag:
                raise UserError('Only Customer Invoice(s) can be marked as Posted.')
        return super(NoxInvoicePost, self).fields_view_get(view_id, view_type, toolbar, submenu)

    @api.multi
    def action_mark_posted(self):
        invoice_ids = self.env.context.get('active_ids', [])
        if invoice_ids:
            return self.env['account.invoice'].browse(invoice_ids).write({'nox_invoice_posted': True})
        return True