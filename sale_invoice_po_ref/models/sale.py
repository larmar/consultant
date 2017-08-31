# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_po_ref = fields.Char('Customer PO Number')
    