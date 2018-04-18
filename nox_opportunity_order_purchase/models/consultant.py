# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api


class Consultant(models.Model):
    _inherit = "consultant.consult"

    @api.multi
    def create_nonstandard_product(self):
        """This function creates and links a Product with PO/Vendor Bills
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
        
        # Create product_tmpl_id
        Product = self.env['product.product'].create({
                                                'name': context['name'],
                                                'sale_ok': True,
                                                'purchase_ok': True,
                                                'type': 'service',
                                                'list_price': sales_hourly_rate,
                                                'standard_price': 0.0,
                                                
                                                'can_be_expensed': True,
                                                'invoice_policy': 'delivery',
                                                'expense_policy': 'sales_price',
                                                'track_service': 'manual',
                                                'consultant_product': False,
                                                'non_standard_product': True,
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
