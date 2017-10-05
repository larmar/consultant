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

from datetime import datetime

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_create_draft_po(self):
        for order in self:
            #Validate missing Vendor or vendor price on product:
            for line in order.order_line:
                vendor_price = order.validate_product_for_vendor(line.product_id)
                if vendor_price != order.nox_cost_hourly_rate:
                    raise ValidationError(_('Unit price in PO Order line cannot be different from Cost hourly rate in SO!\n\Product: %s'%(order.nox_product1.name)))

        return super(SaleOrder, self).action_create_draft_po()

    @api.multi
    def validate_product_for_vendor(self, product):
        if not product.seller_ids:
            raise ValidationError(_('Missing Vendor!\n\nProduct: %s'%(product.name)))
        
        for vendor in product.seller_ids:
            if not vendor.price:
                raise ValidationError(_('Missing Vendor Price!\n\nProduct: %s\nVendor: %s'%(product.name, vendor.name.name)))
            return vendor.price
        
        return True