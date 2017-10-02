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
        """Validate Order End Date & Status to update related Consultant(s) stage 
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
            consultant_id = False #TODO
            if consultant_id:
                consultants.append(consultant_id)
        consultants = list(set(consultants))

        #update consultant(s) stage by validating all his related Sale Orders:
        for consultant in consultants:
            consultant.auto_set_consultant_stage()

        return res


    @api.model
    def all_consultants_stage_update(self):
        """This function is executed by cron/scheduler to check Sales Order(s) and update Consultant Stage.
        It is executed on every 12 hours.
        """
        sol_products, consultants = [], []
        
        yesterday = dt.today() - timedelta(1)
        orders = self.search([('nox_is_enddate', '=', yesterday)])

        for order in orders:
            for line in order.order_line:
                if line.product_id:
                    sol_products.append(line.product_id.id)

        sol_products = list(set(sol_products))
        for product in sol_products:
            consultant_id = False #TODO
            if consultant_id:
                consultants.append(consultant_id)
        consultants = list(set(consultants))

        #update consultant(s) stage by validating all his related Sale Orders:
        for consultant in consultants:
            consultant.auto_set_consultant_stage()
        return True