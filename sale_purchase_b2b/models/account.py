# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('account_analytic_id')
    def _onchange_account_analytic_id(self):
    	if self.invoice_id.origin:
    		purchase_id = self.env['purchase.order'].search([('name','=',self.invoice_id.origin)])
    		account_analytic_id = False
    		if purchase_id and purchase_id.sale_id:
    			for line in purchase_id.order_line:
    				account_analytic_id = line.account_analytic_id and line.account_analytic_id.id or False
    				break
    			self.account_analytic_id = account_analytic_id