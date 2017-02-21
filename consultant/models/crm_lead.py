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
        industries, roles, competences, certificates = [], [], [], []
        result = []
        for oppr in self:
            for industry in oppr.industry_ids:
                industries.append(industry.id)
            for role in oppr.role_ids:
                roles.append(role.id)
            for competence in oppr.competence_ids:
                competences.append(competence.id)
            for certificate in oppr.certificate_ids:
                certificates.append(certificate.id)
        	
            consultants = self.env['consultant.consult'].search([('id','>',0)])        	
            for consultant in consultants:
                flag = True
                c_industries, c_roles, c_competences, c_certificates = [], [], [], []

                for c_industry in consultant.industry_ids:
                    c_industries.append(c_industry.id)                    
                for s_industry in industries:
                    if s_industry not in c_industries:
                        flag = False
                        break

                for c_role in consultant.role_ids:
                    c_roles.append(c_role.id)
                for s_role in roles:
                    if s_role not in c_roles:
                        flag = False
                        break

                for c_competence in consultant.competence_ids:
                    c_competences.append(c_competence.id)
                for s_competence in competences:
                    if s_competence not in c_competences:
                        flag = False
                        break

                for c_certificate in consultant.certificate_ids:
                    c_certificates.append(c_certificate.id)
                for s_certificate in certificates:
                    if s_certificate not in c_certificates:
                        flag = False
                        break

                if flag is True:
                    result.append(consultant.id)
        res['domain'] = [['id', 'in', result]]
        return res