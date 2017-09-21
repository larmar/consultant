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

    @api.multi
    def create_purchase_order(self, order_id, vals):
        """Override function defined in sale_purchase_b2b app; to set Start Date & End Date from Sales Order when Purchase Order is created from SO
        """
        purchase_id = super(SaleOrder, self).create_purchase_order(order_id, vals)
        purchase_id.write({
                    'nox_is_startdate': order_id.nox_is_startdate,
                    'nox_is_enddate': order_id.nox_is_enddate,
                    })
        return purchase_id
