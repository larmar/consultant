# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"

    nox_commission_payment = fields.Boolean('Commission Payment?', copy=False)
    nox_commission_payment_vendor = fields.Many2one('res.partner', 'Pay To', copy=False, domain="[('supplier','=',True)]")
    nox_commission_payment_amount = fields.Float('Amount Per Hour', copy=False)
    has_commission_order = fields.Boolean('Has Commission Order?', copy=False)
    commission_order_lines = fields.One2many('purchase.order.line', 'commission_sale_id', 'Commission Order Lines', copy=False)

    @api.model_cr
    def init(self):
        """drop required constraint from purchase_line_warn column to allow creation of Commission product from data file.
        """
        try:
            self._cr.execute("""alter table product_template alter column purchase_line_warn drop not null;""")
        except Exception:
            pass

    @api.model
    def default_get(self, fields):
        """Set default values on NOX Commission fields if Quotation is created from Opportunity
        """
        context = self._context
        res = super(SaleOrder, self).default_get(fields)
        opportunity_id = context.get('default_opportunity_id', False)
        if opportunity_id:
            Opportunity = self.env['crm.lead'].browse([opportunity_id])
            
            res.update({
            		'nox_commission_payment': Opportunity.nox_commission_payment,
            		'nox_commission_payment_vendor': Opportunity.nox_commission_payment_vendor and Opportunity.nox_commission_payment_vendor.id or False,
            		'nox_commission_payment_amount': Opportunity.nox_commission_payment_amount,
                })
        return res

    @api.depends('commission_order_lines')
    def _commission_order_line_check(self):
        for sale in self:
            if sale.commission_order_lines:
                sale.has_commission_order = True
            else:
                sale.has_commission_order = False

    @api.multi
    def action_create_commission_order(self):
        for sale in self:
            if not sale.nox_commission_payment_vendor:
                raise ValidationError(_('Missing Vendor!\n\nPlease select Pay To (Vendor) to Create Commission Order.'))
            if not sale.nox_commission_payment_amount or sale.nox_commission_payment_amount == 0:
                raise ValidationError(_('Missing Price!\n\nPlease enter valid Amount Per Hour to Create Commission Order.'))
            
            purchase_vals, purchase_line_vals = {}, []
        
            #purchase order :
            fiscal_position_id = self.env['account.fiscal.position'].with_context(company_id=self.create_uid.company_id.id).get_fiscal_position(sale.nox_commission_payment_vendor.id)
            payment_term_id = sale.nox_commission_payment_vendor.property_supplier_payment_term_id.id
            currency_id = sale.nox_commission_payment_vendor.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id
            
            vendor_price = sale.nox_commission_payment_amount or 0.0            

            #get quantity from related PO's Vendor Bills (PO created from sale_purchase_b2b app functionality
            related_purchase_ids, qty = [], 0.0
            for line in sale.purchase_line_ids:
                related_purchase_ids.append(line.order_id)
            related_purchase_ids = list(set(related_purchase_ids))

            for po in related_purchase_ids:
                for po_inv in po.invoice_ids:
                    for inv_line in po_inv.invoice_line_ids:
                        qty += inv_line.quantity

            #purchase order lines :

            commission_order_products = self.env['product.product'].search([('product_tmpl_id.is_commission_product', '=', True)])
            for product_id in commission_order_products:
                taxes = []
                for tax in product_id.supplier_taxes_id:
                    taxes.append(tax.id)

                line_vals = {
                    'name': product_id.name,
                    'product_id': product_id.id or False,
                    'product_qty': qty,
                    'price_unit': vendor_price,
                    'account_analytic_id': sale.related_project_id and sale.related_project_id.id or False,
                    'product_uom': product_id.uom_po_id.id or product_id.uom_id.id,
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'taxes_id': [[6, 0, taxes]],
                    'state': 'draft',
                    'commission_sale_id': sale.id,
                }
                purchase_line_vals.append(line_vals)

            purchase_vals = {
                'default_partner_id': sale.nox_commission_payment_vendor.id,
                'default_project_id': sale.related_project_id and sale.related_project_id.id or False,
                'default_fiscal_position_id': fiscal_position_id,
                'default_payment_term_id': payment_term_id,
                'default_currency_id': currency_id,
                'default_order_line': purchase_line_vals,
                'default_commission_sale_id': sale.id,
                'default_origin': sale.name,
                'commission_order': True,
                }
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id('purchase.purchase_order_form')
            return {
                'name': 'Commission Order',
                'type': 'ir.actions.act_window',   
                'res_model': 'purchase.order',
                'view_type': 'form',
                'view_id': form_view_id or False,
                'view_mode': 'form',
                'context': purchase_vals,
                'target': 'current',
                }
