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
    def action_confirm(self):
        """Create & link Analytic Account with name: Sales Order No + / + Product name(s) + / + Customer name
        """
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            analytic_account_name = [order.name]
            for line in order.order_line:
                analytic_account_name.append(line.product_id.name)

            analytic_account_name = ' / '.join(analytic_account_name)

            analytic_account_id = self.env['account.analytic.account'].create({'name': analytic_account_name, 'partner_id': order.partner_id.id})

            order.write({'project_id': analytic_account_id.id})

        return res