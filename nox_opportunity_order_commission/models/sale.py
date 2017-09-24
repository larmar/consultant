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

class SaleOrder(models.Model):
    _inherit = "sale.order"

    nox_commission_payment = fields.Boolean('Commission Payment?', copy=False)
    nox_commission_payment_vendor = fields.Many2one('res.partner', 'Pay To', copy=False, domain="[('supplier','=',True)]")
    nox_commission_payment_amount = fields.Float('Amount Per Hour', copy=False)
    has_commission_order = fields.Boolean('Has Commission Order?', copy=False)

    @api.model_cr
    def init(self):
        """drop required constraint from purchase_line_warn column to allow creation of Commission product from data file.
        """
        try:
            self._cr.execute("""alter table product_template alter column purchase_line_warn drop not null;""")
        except Exception:
            pass

    @api.model
    def default_get(self, fields):
        """Set default values on NOX Commission fields if Quotation is created from Opportunity
        """
        context = self._context
        res = super(SaleOrder, self).default_get(fields)
        opportunity_id = context.get('default_opportunity_id', False)
        if opportunity_id:
            Opportunity = self.env['crm.lead'].browse([opportunity_id])
            
            res.update({
            		'nox_commission_payment': Opportunity.nox_commission_payment,
            		'nox_commission_payment_vendor': Opportunity.nox_commission_payment_vendor and Opportunity.nox_commission_payment_vendor.id or False,
            		'nox_commission_payment_amount': Opportunity.nox_commission_payment_amount,
                })
        return res

    @api.multi
    def action_create_commission_order(self):
        for sale in self:
            if not sale.nox_commission_payment_vendor:
                raise ValidationError(_('Missing Vendor!\n\nPlease select Pay To (Vendor) to Create Commission Order.'))
            if not sale.nox_commission_payment_amount or sale.nox_commission_payment_amount == 0:
                raise ValidationError(_('Missing Price!\n\nPlease enter valid Amount Per Hour to Create Commission Order.'))
            