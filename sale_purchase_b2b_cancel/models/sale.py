# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_cancel(self):
        """Cancel Related Purchase Orders 
        """
        for sale in self:
            poids = []
            for po in sale.purchase_line_ids:
                poids.append(po.order_id)
            poids = list(set(poids))

            for po in poids:
                try:
                    po.button_cancel()
                except Exception, e:
                    warning = e and e[0]
                    warning += '\n(Purchase Order: %s)' % (po.name)
                    raise UserError(_(warning))

        return super(SaleOrder, self).action_cancel()
        