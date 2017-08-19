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

    @api.multi
    def action_date_assign(self):
        """Do Nothing: Avoid overwriting Due Date based on Payment Term
        """
        return True