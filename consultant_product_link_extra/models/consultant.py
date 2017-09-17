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

    product2_id = fields.Many2one('product.product', 'Related Product 2', readonly=True, copy=False)
    product3_id = fields.Many2one('product.product', 'Related Product 3', readonly=True, copy=False)


    @api.multi
    def action_link_product2(self):
        for Consultant in self:
            if not Consultant.product2_id:
                Product2 = Consultant.create_consultant_product(Consultant)
                Consultant.write({'product2_id': Product2.id})
                _logger.info("Related Product 2 has been linked with Consultant. Id: %s | Consultant: %s"%(Consultant.id, Consultant.name))

    @api.multi
    def action_link_product3(self):
        for Consultant in self:
            if not Consultant.product3_id:
                Product3 = Consultant.create_consultant_product(Consultant)
                Consultant.write({'product3_id': Product3.id})
                _logger.info("Related Product 3 has been linked with Consultant. Id: %s | Consultant: %s"%(Consultant.id, Consultant.name))