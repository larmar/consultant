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

from odoo.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

class ConsultantConsult(models.Model):
    _inherit = "consultant.consult"

    @api.multi
    def create_order_line_product(self):
        """This function creates and links a Product with Sales Order line
        """
        context = self.env.context or {}
        sales_hourly_rate, cost_hourly_rate = 0, 0
        if context.get('sales_hourly_rate', 0):
        	sales_hourly_rate = context['sales_hourly_rate']
        if context.get('cost_hourly_rate', 0):
        	cost_hourly_rate = context['cost_hourly_rate']

        Consultant = self
        User = self.env['res.users'].browse([self._uid])

        vendor_id = Consultant.partner_id and Consultant.partner_id.id or False
        consultant_name = Consultant.name
        
        consultant_product = self.env['product.product'].with_context(show_consultant_product_template=True).search([('consultant_id', '=', Consultant.id)], order="name desc", limit=1)
        consultant_product_no = '1'
        if consultant_product:
            consultant_prod_name = consultant_product.name.split(' ')[-1]
            if consultant_prod_name:
                consultant_product_no = str(int(consultant_prod_name) + 1)

        # Create product
        Product = self.env['product.product'].create({
                                                'name': ' '.join([consultant_name, consultant_product_no]),
                                                'sale_ok': True,
                                                'purchase_ok': True,
                                                'type': 'service',
                                                'list_price': sales_hourly_rate,
                                                'standard_price': 0.0,
                                                
                                                'can_be_expensed': True,
                                                'invoice_policy': 'delivery',
                                                'expense_policy': 'sales_price',
                                                'track_service': 'manual',
                                                'consultant_product': True,
                                                'consultant_id': Consultant.id,

                                            })

        # Update UOM, Purchase UOM and Internal Category of Product
        update_vals = {}
        hour_uom = self.env['ir.model.data'].xmlid_to_res_id('product.product_uom_hour')
        if hour_uom:
            update_vals = {'uom_id': hour_uom, 'uom_po_id': hour_uom}

        categ_id = self.env['product.category'].search([('name', '=', 'Consultancy')])
        if categ_id:
            categ_id = categ_id[0].id
        else:
            categ_id = self.env['ir.model.data'].xmlid_to_res_id('product.product_category_1')
        if categ_id:
            update_vals['categ_id'] = categ_id

        # Set Default Sales tax & Purchase tax as Vendor tax on Product:
        company_id = User.company_id.id
        sales_tax = self.env['ir.model.data'].xmlid_to_res_id('l10n_se.' + str(company_id) + '_sale_tax_25_services')
        if sales_tax:
            update_vals['taxes_id'] = [[6, 0, [sales_tax]]]
        
        purchase_tax = self.env['ir.model.data'].xmlid_to_res_id('l10n_se.' + str(company_id) + '_purchase_tax_25_services')
        if purchase_tax:
            update_vals['supplier_taxes_id'] = [[6, 0, [purchase_tax]]]
        
        Product.write(update_vals)

        # Set Vendor on Product
        if vendor_id:
            self.env['product.supplierinfo'].create({'name': vendor_id, 'product_tmpl_id': Product.product_tmpl_id.id, 'price': cost_hourly_rate})

        return Product
