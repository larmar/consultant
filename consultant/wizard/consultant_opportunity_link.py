#-*- coding:utf-8 -*-

from openerp import models, fields, api

class consultant_opportunity_link(models.TransientModel):
    _name = "consultant.opportunity.link"
    _description = "Consultant Opportunity Link"

    consultant_ids = fields.Many2many('consultant.consult', 'temp_consultant_rel', 'temp_id', 'consultant_id', 'Selected Consultants')
    opportunity_id = fields.Many2one('crm.lead', 'Opportunity', domain="[('type','=','opportunity')]")

    @api.model
    def default_get(self, fields):
        context = self._context
        res = super(consultant_opportunity_link, self).default_get(fields)
        res.update(consultant_ids=[[6,0,context.get('active_ids')]])
        return res

    @api.multi
    def action_assign(self):
        for rec in self:
            opportunity_id = rec.opportunity_id.id
            consultants = []
            for consultant in rec.consultant_ids:
                self._cr.execute("""select consultant_id from consultant_consult_opportunity_rel
    									where consultant_id=%s and opportunity_id=%s"""%(consultant.id, opportunity_id))
                result = self._cr.fetchone()
                print"########### result " ,result
                if not result:
                    self._cr.execute(""" insert into consultant_consult_opportunity_rel(consultant_id, opportunity_id)
                                            values(%s, %s)"""%(consultant.id, opportunity_id))
    			#consultant.write({'opportunity_ids': [[4, 0, [rec.opportunity_id.id]]]})