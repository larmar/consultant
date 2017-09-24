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
