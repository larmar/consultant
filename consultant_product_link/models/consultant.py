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

class ConsultantConsult(models.Model):
    _inherit = "consultant.consult"

    product_id = fields.Many2one('product.product', 'Related Product')

    @api.multi
    def action_link_product(self):
        for consultant in self:
            if consultant.product_id:
                raise ValidationError(_('Consultant %s already has Linked Product.')%(consultant.name))
            product_id = self.env['product.product'].create({
                                                        'name': consultant.name,
                                                        'type': 'consu',
                                                    })
            consultant.write({'product_id': product_id.id})