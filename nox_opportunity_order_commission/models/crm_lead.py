# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = "crm.lead"

    nox_commission_payment = fields.Boolean('Commission Payment?', copy=False)
    nox_commission_payment_vendor = fields.Many2one('res.partner', 'Pay To', copy=False, domain="[('supplier','=',True)]")
    nox_commission_payment_amount = fields.Float('Amount Per Hour', copy=False)

    