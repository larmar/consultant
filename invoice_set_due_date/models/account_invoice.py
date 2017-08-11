# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, api, fields

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    #due_date_lock = fields.Boolean()

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        if not self.date_due:
            return super(AccountInvoice, self)._onchange_payment_term_date_invoice()

        date_invoice = self.date_invoice
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if not self.payment_term_id:
            # When no payment term defined
            self.date_due = self.date_due or self.date_invoice

    @api.multi
    def action_date_assign(self):
        """Do Nothing: Avoid overwriting Due Date based on Payment Term
        """
        return True