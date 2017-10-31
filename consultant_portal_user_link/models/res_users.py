# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        """Update Related User on Consultants
        """
        context = self.env.context or {}
        User = super(ResUsers, self).create(vals)

        if context.get('check_consultant_user', False):
            Consultants = self.env['consultant.consult'].search([('contact_id.email', '=', User.email)])
            for consultant in Consultants:
                consultant.write({'user_id': User.id})
        return User
