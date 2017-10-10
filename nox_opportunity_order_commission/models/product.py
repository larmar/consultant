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

class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_commission_product = fields.Boolean('Is Commission Product', readonly=True)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def default_get(self, fields):
        """Set default fields for Commission Product.
        """
        vals = {}
        res = super(ProductProduct, self).default_get(fields)
        context = self._context
        if isinstance(context, dict) and context.get('is_commission_product', False):
            imd = self.env['ir.model.data']
            uom_houlry = imd.xmlid_to_res_id('product.product_uom_hour')
            if uom_houlry:
                vals = {'uom_id': uom_houlry, 'uom_po_id': uom_houlry}
            
            commission_categ = imd.xmlid_to_res_id('nox_opportunity_order_commission.product_category_commission')
            if commission_categ:
                vals['categ_id'] = commission_categ
            vals['invoice_policy'] = 'delivery'

        if vals:
            res.update(vals)
        return res

    @api.model
    def create(self, vals):
        context = self.env.context
        if context and context.get('is_commission_product', 0):
            raise ValidationError(_('Access Denied.\n\nCommission Product already exists! Please contact your System Administrator.'))

        return super(ProductProduct, self).create(vals)

    @api.multi
    def unlink(self):
        for product in self:
            if product.is_commission_product:
                raise ValidationError(_('Access Denied.\n\nYou cannot delete a Commission Product! Please contact your System Administrator.'))
        return super(ProductProduct, self).unlink()

