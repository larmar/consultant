# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class crm_lead(models.Model):
    _inherit = "crm.lead"

    @api.depends('consultant_ids')
    def _consultant_count(self):
        count = 0
        for rec in self:
            for consultant in rec.consultant_ids:
                count += 1
            rec.consultant_count = count

    consultant_ids = fields.Many2many('consultant.consult', 'consultant_consult_opportunity_rel', 'opportunity_id', 'consultant_id', 'Consultants')
    consultant_count = fields.Integer(compute='_consultant_count', string='# Consultants', copy=False, default=0)

    #consultant profile search fields:
    industry_ids = fields.Many2many('consultant.industry', string='Industry')
    role_ids = fields.Many2many('consultant.role', string='Role')
    certificate_ids = fields.Many2many('consultant.certificate', string='Certifications')
    competence_ids = fields.Many2many('consultant.competence', string='IT Competence')

    @api.multi
    def action_open_consultants(self):
        """
        Open Consultants related to current opportunity.
        :return dict: dictionary value Consultants view
        """
        res = self.env['ir.actions.act_window'].for_xml_id('consultant', 'action_consultant_consult')
        
        self._cr.execute(""" select consultant_id from consultant_consult_opportunity_rel
                                where opportunity_id=%s """%(self.id))
        result = self._cr.fetchall()
        consultants = []
        for r in result:
            r = r[0]
            consultants.append(r)
        res['domain'] = [['id', 'in', consultants]]
        return res

    @api.multi
    def action_search_consultants(self):
        """Search Consultants by Industry | Role | Competence | Certificate & show in list view
        """
        res = self.env['ir.actions.act_window'].for_xml_id('consultant', 'action_consultant_consult')
        consultants = []
        industries, roles, competences, certificates = [], [], [], []
        for oppr in self:
            for industry in oppr.industry_ids:
                industries.append(industry.id)
            if industries:
                industries = ', '.join(str(ind) for ind in industries)
                oppr._cr.execute(""" select consultant_consult_id from consultant_consult_consultant_industry_rel \
                                        where consultant_industry_id in (%s)"""%(industries))
                result = self._cr.fetchall()
                for r in result:
                    r = r[0]
                    consultants.append(r)

            for role in oppr.role_ids:
                roles.append(role.id)
            if roles:
                roles = ', '.join(str(rl) for rl in roles)
                oppr._cr.execute("""select consultant_consult_id from consultant_consult_consultant_role_rel \
                                        where consultant_role_id in (%s)"""%(roles))
                result = self._cr.fetchall()
                for r in result:
                    r = r[0]
                    consultants.append(r)

            for competence in oppr.competence_ids:
                competences.append(competence.id)
            if competences:
                competences = ', '.join(str(cmpt) for cmpt in competences)
                oppr._cr.execute(""" select consultant_consult_id from consultant_competence_consultant_consult_rel \
                                         where consultant_competence_id in (%s)"""%(competences))
                result = self._cr.fetchall()
                for r in result:
                    r = r[0]
                    consultants.append(r)

            for certificate in oppr.certificate_ids:
                certificates.append(certificate.id)
            if certificates:
                certificates = ', '.join(str(cert) for cert in certificates)
                oppr._cr.execute(""" select consultant_consult_id from consultant_certificate_consultant_consult_rel \
                                         where consultant_certificate_id in (%s)"""%(certificates))
                result = self._cr.fetchall()
                for r in result:
                    r = r[0]
                    consultants.append(r)            

            consultants = list(set(consultants))

        res['domain'] = [['id', 'in', consultants]]
        return res