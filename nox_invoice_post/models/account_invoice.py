# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    nox_invoice_posted = fields.Boolean('Invoice Posted')

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if vals.get('nox_invoice_posted', False):
            res.message_post(body=_('Invoice has been Posted to Customer.'))
        return res

    @api.multi
    def write(self, vals):
        nox_invoice_posted = self.nox_invoice_posted
        res = super(AccountInvoice, self).write(vals)
        if 'nox_invoice_posted' in vals and vals['nox_invoice_posted'] != nox_invoice_posted and vals['nox_invoice_posted'] is True:
            self.message_post(body=_('Invoice has been Posted to Customer.'))
        return res
