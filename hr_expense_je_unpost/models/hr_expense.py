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

    #redefine state field: rename status "Posted" to "Audited"
    state = fields.Selection([('submit', 'Submitted'),
                              ('approve', 'Approved'),
                              ('post', 'Audited'),
                              ('done', 'Paid'),
                              ('cancel', 'Refused')
                              ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='submit', required=True,
        help='Expense Report State')

class HR_Expense(models.Model):
    _inherit = "hr.expense"

    @api.multi
    def action_move_create(self):
        """Mark expense Journal entry as Unposted
        """
        for expense in self:
            super(HR_Expense, expense).action_move_create()
            expense.sheet_id.account_move_id.write({'state': 'draft'})
            