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
    