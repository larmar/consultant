# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, api
from odoo.tools import email_split

def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''

class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    @api.multi
    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
            Redefined to set the context to update Related User on matched Consultants.
        """
        company_id = self.env.context.get('company_id')
        return self.env['res.users'].with_context(no_reset_password=True, check_consultant_user=True).create({
            'email': extract_email(self.email),
            'login': extract_email(self.email),
            'partner_id': self.partner_id.id,
            'company_id': company_id,
            'company_ids': [(6, 0, [company_id])],
            'groups_id': [(6, 0, [])],
        })
