# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class HRExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    @api.multi
    def action_sheet_move_create(self):
        """Set posted Journal Entries to Unposted
        """
        res = super(HRExpenseSheet, self).action_sheet_move_create()
        for expense in self:
            expense.account_move_id.write({'state': 'draft'})
        return res

    #redefine state field: rename status "Posted" to "Audited"
    state = fields.Selection([('submit', 'Submitted'),
                              ('approve', 'Approved'),
                              ('post', 'Audited'),
                              ('done', 'Paid'),
                              ('cancel', 'Refused')
                              ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='submit', required=True,
        help='Expense Report State')