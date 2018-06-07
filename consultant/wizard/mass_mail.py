# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from email.utils import formataddr

from datetime import datetime, timedelta

class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    @api.model
    def default_get(self, fields):
        res = super(MailComposeMessage, self).default_get(fields)
        context = self.env.context or {}
        if context and isinstance(context, dict) and context.get('consultant_mass_mail', False):
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
        #reset Subject by removing Reference/Description from Subject when compose message wizard opened from Invoice
        if context and context.get('active_model','') == 'account.invoice':
            invoice = self.env['account.invoice'].sudo().browse(context['active_ids'])[0]
            invoice_ref = invoice.number
            company_name = invoice.company_id.name

            subject = res.get('subject', '')
            if invoice_ref and subject:
                result = subject.split(invoice_ref)
                if result and len(result) > 1:
                    subject = result[0]
                    res.update({'subject': subject})
            #reset subject as Company Name + Invoice + (Ref InvoiceNo)
            res.update({'subject': '%s Invoice (Ref %s)'%(company_name, invoice_ref)})
        return res

    @api.multi
    def send_mail_action(self):
        """Create & execute Mass Mail from mail compose wizard
        """
        context = self.env.context or {}
        if 'consultant_mass_mail' in context:
            partners = []
            temp = [partners.append(consultant.contact_id.id) for consultant in self.env['consultant.consult'].browse(context.get('active_ids', False)) if consultant.contact_id]
            partners = str(list(set(partners)))

            attachments = []
            temp = [attachments.append(attach.id) for attach in self.attachment_ids]

            mass_mail_vals = {
                'email_from': self.email_from,
                'name': self.subject,
                'mailing_model': 'res.partner',
                'mailing_domain': "[[u'id', u'in', %s]]" % (partners),
                'body_html': self.body,
                'reply_to': self.reply_to,
                'keep_archives': True,
                'reply_to_mode': 'email',
                'schedule_date': datetime.now() - timedelta(minutes=5),
                'next_departure': datetime.now() - timedelta(minutes=5),
                'attachment_ids': [[6, 0, attachments]],
                'consultant_mass_mail': True,
            }
            mass_mailing_id = self.env['mail.mass_mailing'].create(mass_mail_vals)
            mass_mailing_id.put_in_queue()
            #manually trigger mass mailing function to execute **RUN MANUALLY**
            cron_id = self.env['ir.model.data'].xmlid_to_res_id('mass_mailing.ir_cron_mass_mailing_queue')
            if cron_id:
            	cron = self.env['ir.cron'].sudo().browse([cron_id])
            	cron.with_context(consultant_mass_mail=False).sudo().method_direct_trigger()
        else:
            return super(MailComposeMessage, self).send_mail_action()

    @api.multi
    def get_mail_values(self, res_ids):
        #keep only one res_ids to create single mass mail with all recepients
        context = self.env.context or {}
        if context.get('consultant_mass_mail', False):
            if res_ids and len(res_ids) > 1:
                res_ids = [res_ids[0]]
        return super(MailComposeMessage, self).get_mail_values(res_ids)

    @api.multi
    def render_message(self, res_ids):
        """Overrite function to fix bug of partner_ids key not found when email is sent through a template
        """
        context = self.env.context or {}
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
        
        if context.get('consultant_mass_mail', False):
            #keep only one res_ids to create single mass mail with all recepients
            if res_ids and len(res_ids) > 1:
                res_ids = [res_ids[0]]

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


class MailMassMailing(models.Model):
    _inherit = "mail.mass_mailing"

    consultant_mass_mail = fields.Boolean('Consultant Mails')


class MailMailStats(models.Model):
    _inherit = 'mail.mail.statistics'

    consultant_mass_mail = fields.Boolean('Consultant Mails')

    @api.model
    def create(self, vals):
        """Set Consultant mass mail check 
        """
        if not vals: vals = {}
        if vals.get('mass_mailing_id', False):
            consultant_mass_mail = self.env['mail.mass_mailing'].browse([vals['mass_mailing_id']])[0].consultant_mass_mail
            if consultant_mass_mail:
                vals['consultant_mass_mail'] = True
        return super(MailMailStats, self).create(vals)


class MassMailingReport(models.Model):
    _inherit = 'mail.statistics.report'



