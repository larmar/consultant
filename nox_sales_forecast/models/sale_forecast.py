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
from odoo.addons.nox_sales_forecast.models.date_month_year import MONTHS

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for sale in self:
            if sale.related_project_id and sale.state == 'sale':
                sale.related_project_id.compute_forecast(sale)
        return res
