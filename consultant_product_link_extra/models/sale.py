# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime, timedelta, date as dt

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def write(self, vals):
        """Override function from parent app: consultant_product_link to include extra products product2_id & product3_id.
        Validate Order End Date & Status to update related Consultant(s) stage 
            1. If Order is ongoing; Set consultant stage as "On Nox Contract"
            2. Otherwise; set consultant stage as "Sale Ready"
        """
        if not vals:
            vals = {}

        res = super(SaleOrder, self).write(vals)

        #get all consultants related to Sales Order:
        sol_products, consultants = [], []
        for line in self.order_line:
            if line.product_id:
                sol_products.append(line.product_id.id)
        for product in sol_products:
            consultant_id = self.env['consultant.consult'].search(['|','|',('product_id','=',product),('product2_id','=',product),('product3_id','=',product)])
            if consultant_id:
                consultants.append(consultant_id)
        consultants = list(set(consultants))

        #update consultant(s) stage by validating all his related Sale Orders:
        for consultant in consultants:
            consultant.auto_set_consultant_stage()

        return res