# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class consultant_opportunity_link(models.TransientModel):
    _name = "consultant.opportunity.unlink"
    _description = "Consultant Opportunity Remove"

    opportunity_ids = fields.Many2many('crm.lead', 'temp_consultant_opportunity_rel', 'temp_id', 'opportunity_id', 'Selected Opportunities')
    consultant_id = fields.Many2one('consultant.consult', 'Consultant')

    @api.model
    def default_get(self, fields):
        context = self.env.context
        res = super(consultant_opportunity_link, self).default_get(fields)
        res.update(opportunity_ids=[[6,0,context.get('active_ids')]])
        
        #update consultant:
        consultants = []

        for oppr in self.env['crm.lead'].browse(context.get('active_ids', [])):
        	consultants.append(oppr.consultant_unlink_id.id)

        consultants = list(set(consultants))
        if len(consultants) > 1:
            raise ValidationError('Access Denied!\n\nThis operation is only allowed from Consultant Card > Opportunities List.')
        
        res.update({'consultant_id': consultants.pop()})

        return res

    @api.multi
    def action_unlink(self):
        for rec in self:
            """Remove selected Opportunities from Consultant card
            """
            consultant_id = rec.consultant_id.id
            consultant_oportunities = []
            temp = [consultant_oportunities.append(oppr.id) for oppr in rec.consultant_id.opportunity_ids]

            opportunity_to_unlink = []
            temp = [opportunity_to_unlink.append(op.id) for op in rec.opportunity_ids]
            temp = [consultant_oportunities.remove(item) for item in opportunity_to_unlink if item in consultant_oportunities]

            rec.consultant_id.write({'opportunity_ids': [[6, 0, consultant_oportunities]]})