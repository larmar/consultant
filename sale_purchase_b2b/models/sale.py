# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo import SUPERUSER_ID

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class Sale(models.Model):
    _inherit = "sale.order"

    purchase_line_ids = fields.One2many('purchase.order.line', 'sale_id', 'Purchase Orders')
    purchase_line_check = fields.Boolean(compute="_purchase_line_check", strign="Has Purchase Lines?", store=True)

    @api.depends('purchase_line_ids')
    def _purchase_line_check(self):
        for sale in self:
            if sale.purchase_line_ids:
                sale.purchase_line_check = True
            else:
                sale.purchase_line_check = False

    @api.multi
    def action_create_draft_po(self):
        """Create Purchase Order from Sales Order
        """
        purchase_vals, purchase_line_vals = {}, []
        for sale in self:
            #purchase order :
            fiscal_position_id = self.env['account.fiscal.position'].with_context(company_id=self.create_uid.company_id.id).get_fiscal_position(sale.partner_id.id)
            payment_term_id = sale.partner_id.property_supplier_payment_term_id.id
            currency_id = sale.partner_id.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id

            #get vendor from first sale order line products Vendors setting
            flag, vendor_id, vendor_product_id = True, False, False
            vendor_price = 0.0
            for line in sale.order_line:
                if flag and line.product_id:
                    for seller in line.product_id.seller_ids:
                        vendor_product_id = line.product_id.id
                        vendor_id = seller.name.id
                        vendor_price = seller.price
                        break
                flag = False
            
            #purchase order lines :
            for line in sale.order_line:
                taxes = []
                for tax in line.product_id.supplier_taxes_id:
                    taxes.append(tax.id)

                price_unit = line.product_id and line.product_id.standard_price or 0.0
                if line.product_id and line.product_id.id == vendor_product_id:
                    price_unit = vendor_price

                line_vals = {
                    'name': line.name,
                    'product_id': line.product_id and line.product_id.id or False,
                    'product_qty': line.product_uom_qty,
                    'price_unit': price_unit,
                    'account_analytic_id': sale.related_project_id and sale.related_project_id.id or False,
                    'product_uom': line.product_id.uom_po_id.id or line.product_id.uom_id.id,
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'taxes_id': [[6, 0, taxes]],
                    'sale_id': sale.id,
                    'state': 'draft',
                }
                purchase_line_vals.append(line_vals)

            purchase_vals = {
                'default_partner_id': vendor_id,
                'default_project_id': sale.related_project_id and sale.related_project_id.id or False,
                'default_fiscal_position_id': fiscal_position_id,
                'default_payment_term_id': payment_term_id,
                'default_currency_id': currency_id,
                'default_order_line': purchase_line_vals,
                'default_sale_id': sale.id,
                'default_origin': sale.name,
                }
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id('purchase.purchase_order_form')
            return {
                'name': 'Request for Quotation',
                'type': 'ir.actions.act_window',   
                'res_model': 'purchase.order',
                'view_type': 'form',
                'view_id': form_view_id or False,
                'view_mode': 'form',
                'context': purchase_vals,
                'target': 'current',
                }

        