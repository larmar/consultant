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