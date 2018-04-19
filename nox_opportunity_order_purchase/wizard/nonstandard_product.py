# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime

class nonstandard_product_create(models.TransientModel):
    _name = "nonstandard.product.create"

    name = fields.Char('Product Name', required=True)

    @api.multi
    def action_create_nonstandard_product(self):
        context = self.env.context or {}
        for rec in self:
            consultant = context.get('consultant', False)
            sales_hourly_rate = context.get('sales_hourly_rate', 0)
            cost_hourly_rate = context.get('cost_hourly_rate', 0)
            account_analytic_id = context.get('account_analytic_id', False)
            taxes = context.get('taxes', [])

            if consultant:
                Consultant = self.env['consultant.consult'].browse([consultant])
                consultant_product = self.env['product.product'].with_context(show_consultant_product_template=True).search(
                                        [('consultant_id', '=', Consultant.id), ('non_standard_product', '=', False)], 
                                        order="name desc", limit=1)
                name = u' '.join([consultant_product.name, rec.name]).encode('utf-8')
                nonstandard_product = Consultant.with_context(name=name, 
                                                                sales_hourly_rate=sales_hourly_rate, 
                                                                cost_hourly_rate=cost_hourly_rate,).create_nonstandard_product()
                if context.get('active_model', '') == 'purchase.order':
                    #add product in PO
                    self.env['purchase.order.line'].create({
                            'order_id': context['po'],
                            'product_id': nonstandard_product.id,
                            'name': nonstandard_product.name,
                            'date_planned': datetime.now(),
                            'company_id': self.env.user.company_id.id,
                            'product_qty': 1,
                            'price_unit': cost_hourly_rate or 1,
                            'product_uom': nonstandard_product.uom_po_id.id,
                            'account_analytic_id': account_analytic_id,
                            'taxes_id': [[6, 0, taxes]],
                        })
