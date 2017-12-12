# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from email.utils import formataddr

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
            reply_to, user_signature = '', ''
            if self.env.uid:
                user_id = self.env['res.users'].browse([self.env.uid])[0]
                reply_to = formataddr((user_id.name, user_id.email))
                user_signature = user_id.signature
            vals = {
                'model': 'consultant.consult',
                'template_id': False,
                'composition_mode': 'mass_mail',
                'subject': '',
                'body': '',
                'partner_ids': [[6, 0, partners]],
                'message_type': 'email',
                'no_auto_thread': True,
                'reply_to': reply_to,
                'body': '<br/><br/> ' + user_signature
                }
            res.update(vals)
        return res

    @api.multi
    def render_message(self, res_ids):
        """Overrite function to fix bug of partner_ids key not found when email is sent through a template
        """
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, (int, long)):
            multi_mode = False
            res_ids = [res_ids]

        subjects = self.render_template(self.subject, self.model, res_ids)
        bodies = self.render_template(self.body, self.model, res_ids, post_process=True)
        emails_from = self.render_template(self.email_from, self.model, res_ids)
        replies_to = self.render_template(self.reply_to, self.model, res_ids)
        default_recipients = {}
        if not self.partner_ids:
            default_recipients = self.env['mail.thread'].message_get_default_recipients(res_model=self.model, res_ids=res_ids)

        results = dict.fromkeys(res_ids, False)
        for res_id in res_ids:
            results[res_id] = {
                'subject': subjects[res_id],
                'body': bodies[res_id],
                'email_from': emails_from[res_id],
                'reply_to': replies_to[res_id],
            }
            results[res_id].update(default_recipients.get(res_id, dict()))

        # generate template-based values
        if self.template_id:
            template_values = self.generate_email_for_composer(
                self.template_id.id, res_ids,
                fields=['email_to', 'partner_to', 'email_cc', 'attachment_ids', 'mail_server_id'])
        else:
            template_values = {}

        for res_id in res_ids:
            if template_values.get(res_id):
                # recipients are managed by the template
                ##customization:
                if 'partner_ids' in results[res_id]:
                    results[res_id].pop('partner_ids')
                if 'email_to' in results[res_id]:
                    results[res_id].pop('email_to')
                if 'email_cc' in results[res_id]:
                    results[res_id].pop('email_cc')
                # remove attachments from template values as they should not be rendered
                template_values[res_id].pop('attachment_ids', None)
            else:
                template_values[res_id] = dict()
            # update template values by composer values
            template_values[res_id].update(results[res_id])

        return multi_mode and template_values or template_values[res_ids[0]]
