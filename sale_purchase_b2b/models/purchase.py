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