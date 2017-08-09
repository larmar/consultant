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
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """Set default order lines with Consultants Product (from Opportunity)
        """
        res = super(SaleOrder, self).onchange_partner_id()
        context = self.env.context
        if 'active_model' in context and context['active_model'] == 'crm.lead' and context.get('default_opportunity_id', False):
            Opportunity = self.env['crm.lead'].browse([context['default_opportunity_id']])
            consultants, products, order_lines = [], [], []
            temp = [consultants.append(consultant) for consultant in Opportunity.consultant_ids]
            for consultant in consultants:
                if consultant.product_id:
                    products.append(consultant.product_id)
            for product in products:
                taxes = []
                temp = [taxes.append(tax.id) for tax in product.taxes_id]
                name = product.name_get()[0][1]
                if product.description_sale:
                    name += '\n' + product.description_sale
                line_data = {
                    'product_id': product.id,
                    'product_uom': product.uom_id and product.uom_id.id or False,
                    'price_unit': product.lst_price,
                    'product_uom_qty': 1,
                    'tax_id': [[6, 0, taxes]],
                    'name': name,
                }
                order_lines.append(line_data)
            if order_lines:
                self.update({'order_line': order_lines})
