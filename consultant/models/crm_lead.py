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
    industry_ids = fields.Many2many('consultant.industry', string='Industry/Customers')
    role_ids = fields.Many2many('consultant.role', string='Role')
    certificate_ids = fields.Many2many('consultant.certificate', string='Certifications')
    competence_ids = fields.Many2many('consultant.competence', string='Competence')
    main_role_ids = fields.Many2many('consultant.role.main', string='Main Role')
    main_competence_ids = fields.Many2many('consultant.competence.main', string='Main Competence')

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
        industries, roles, competences, certificates, mroles, mcompetences = [], [], [], [], [], []
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
            for role in oppr.main_role_ids:
                mroles.append(role.id)
            for competence in oppr.main_competence_ids:
                mcompetences.append(competence.id)
        	
            consultants = self.env['consultant.consult'].search([('id','>',0)])        	
            for consultant in consultants:
                f1, f2, f3, f4, f5, f6 = False, False, False, False, False, False
                if not industries: f1 = True
                if not roles: f2 = True
                if not competences: f3 = True
                if not certificates: f4 = True
                if not mroles: f5 = True
                if not mcompetences: f6 = True

                for c_industry in consultant.industry_ids:
                    if c_industry.id in industries:
                        f1 = True

                for c_role in consultant.role_ids:
                    if c_role.id in roles:
                        f2 = True

                for c_competence in consultant.competence_ids:
                    if c_competence.id in competences:
                        f3 = True

                for c_certificate in consultant.certificate_ids:
                    if c_certificate.id in certificates:
                        f4 = True

                for c_role in consultant.main_role_ids:
                    if c_role.id in mroles:
                        f5 = True

                for c_competence in consultant.main_competence_ids:
                    if c_competence.id in mcompetences:
                        f6 = True

                if all([f1, f2, f3, f4, f5, f6]):
                    result.append(consultant.id)
        res['domain'] = [['id', 'in', result]]
        return res