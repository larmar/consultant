# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.model
    def default_get(self, fields):
        res = super(MailComposeMessage, self).default_get(fields)
        context = self._context
        if context and isinstance(context, dict) and 'consultant_mass_mail' in context:
            partners = []
            temp = [partners.append(consultant.contact_id.id) for consultant in self.env['consultant.consult'].browse(context.get('active_ids', False)) if consultant.contact_id]
            partners = list(set(partners))
            vals = {
                'model': 'consultant.consult',
                'template_id': False,
                'composition_mode': 'mass_mail',
                'subject': '',
                'body': '',
                'partner_ids': [[6, 0, partners]],
                'message_type': 'email',
                'no_auto_thread': True,
                }
            res.update(vals)
        return res