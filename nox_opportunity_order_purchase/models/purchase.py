# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    nox_contract_signed = fields.Boolean('Contract Signed', copy=False)
    nox_is_startdate = fields.Date("Start Date", copy=False)
    nox_is_enddate = fields.Date("End Date", copy=False)

    nox_sale_partner_id = fields.Many2one(related="sale_id.partner_id", string="Customer", store=False)
    nox_sale_consultants = fields.Char(related="sale_id.consultant_names", string="Consultants", store=False)

    @api.model
    def default_get(self, fields):
        """Set Start Date & End Date from Sales Order when Purchase Order is created from SO
        """
        res = super(PurchaseOrder, self).default_get(fields)

        context = self._context
        if isinstance(context, dict) and context.get('active_model', False) == 'sale.order':
            Sale = self.env['sale.order'].browse(context['active_ids'])
            if Sale:
                res.update({
                    'nox_is_startdate': Sale.nox_is_startdate,
                    'nox_is_enddate': Sale.nox_is_enddate,
                })
        return res