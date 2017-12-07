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
        """Create Purchase Order(s) from Sales Order; by Vendors
        """
        purchase_vals, purchase_ids = {}, []
        for sale in self:
            #purchase order :
            fiscal_position_id = self.env['account.fiscal.position'].with_context(company_id=self.create_uid.company_id.id).get_fiscal_position(sale.partner_id.id)
            payment_term_id = sale.partner_id.property_supplier_payment_term_id.id
            currency_id = sale.partner_id.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id

            #create PO by Vendor:
            lines_by_vendor = {}
            for line in sale.order_line:
                for seller in line.product_id.seller_ids:
                    lines_by_vendor[seller.name.id] = []
                    break

            for line in sale.order_line:
                taxes = []
                for tax in line.product_id.supplier_taxes_id:
                    taxes.append(tax.id)

                #TODO: recheck if product line with product which has no Vendors defined to include in any PO
                #if line.product_id and and not line.product_id.seller_ids:
                #    lines_by_vendor[line_val].append([line.product_id, line.product_id.uom_po_id.id or line.product_id.uom_id.id, line.name, line.product_uom_qty, 0, taxes])

                for seller in line.product_id.seller_ids:
                    lines_by_vendor[seller.name.id].append([line.product_id, line.product_id.uom_po_id.id or line.product_id.uom_id.id, line.name, line.product_uom_qty, seller.price, taxes])
                    break

            for vendor in lines_by_vendor:
                purchase_vals = {
                    'partner_id': vendor,
                    'project_id': sale.related_project_id and sale.related_project_id.id or False,
                    'fiscal_position_id': fiscal_position_id,
                    'payment_term_id': payment_term_id,
                    'currency_id': currency_id,
                    'sale_id': sale.id,
                    'origin': sale.name,
                    }
                
                purchase_id = self.create_purchase_order(sale, purchase_vals)
                purchase_ids.append(purchase_id.id)

                for line in lines_by_vendor[vendor]:
                    line_vals = {
                        'product_id': line[0] and line[0].id or False,
                        'product_uom': line[1],
                        'name': line[2],
                        'product_qty': line[3],
                        'price_unit': line[4],
                        'account_analytic_id': sale.related_project_id and sale.related_project_id.id or False,
                        'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'taxes_id': [[6, 0, line[5]]],
                        'sale_id': sale.id,
                        'state': 'draft',
                        'order_id': purchase_id.id
                    }
                    purchase_line_id = self.env['purchase.order.line'].create(line_vals)

            res_id, domain = False, []

            if len(purchase_ids) == 1:
                view_mode = 'form'
                res_id = purchase_ids[0]
            elif purchase_ids:
                view_mode = 'tree,form'
                domain = [['id','in',purchase_ids]]

            return {
                'name': 'Request for Quotation',
                'type': 'ir.actions.act_window',   
                'res_model': 'purchase.order',
                'view_type': 'form',
                'view_mode': view_mode,
                'res_id': res_id,
                'domain': domain,
                'target': 'current',
                }

        
    @api.multi
    def create_purchase_order(self, order_id, vals):
        return self.env['purchase.order'].create(vals)

    @api.multi
    def action_done(self):
        """Close Related Purchase Orders
        """
        for sale in self:
            po_ids = []
            temp = [po_ids.append(pol.order_id) for pol in sale.purchase_line_ids]
            po_ids = list(set(po_ids))
            for po in po_ids:
                if po.state != 'cancel':
                    po.button_done()
        return super(Sale, self).action_done()
