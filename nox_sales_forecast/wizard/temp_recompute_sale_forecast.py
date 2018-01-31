# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError

from datetime import datetime

class TempRecomputeForecast(models.TransientModel):
    _name = "temp.recompute.sale.forecast"

    @api.multi
    def action_recompute_forecast(self):
        """Recompute Sales Forecast for all confirmed Sales Orders
        """
        order_ids = self.env['sale.order'].search([('state','=','sale')])
        for order in order_ids:
        	if order.related_project_id:
				order.related_project_id.compute_forecast(order)
