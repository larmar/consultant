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

class ProductProduct(models.Model):
    _inherit = "product.product"

    consultant_product = fields.Boolean('Is Consultant Product?', copy=False)
    consultant_id = fields.Many2one('consultant.consult', 'Related Consultant', copy=False, readonly=True)
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """This function is used to filter Consultant Products
        """
        context = self._context
        if not args:
            args = [['consultant_id', '=', False]]
        else:
            args.append(['consultant_id', '=', False])
        return super(ProductProduct, self).search(args, offset, limit, order, count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """This function is used to filter Consultant Products
        """
        context = self._context
        if not args:
            args = [['consultant_id', '=', False]]
        else:
            args.append(['consultant_id', '=', False])
        return super(ProductProduct, self).name_search(name, args, operator, limit)
