# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def get_product_price_by_invoice_policy(self, bill_price):
    	"""Return product unit price based on product invoicing setting
    	"""
        invoice_policy = 'cost'
        if self.can_be_expensed:
            if self.expense_policy == 'no':
                return invoice_policy
            elif self.expense_policy == 'sales_price': 
                invoice_policy = 'sale'
        elif self.invoice_policy == 'order':
            invoice_policy = 'sale'

        if invoice_policy == 'sale':
            return self.lst_price
        else:
            return bill_price
