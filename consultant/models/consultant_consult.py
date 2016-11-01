# -*- coding: utf-8 -*-
from openerp import _, api, models, fields
from lxml import etree
from openerp.osv.orm import setup_modifiers

class consultant_consult(models.Model):
    _name = 'consultant.consult'
    _description = "Consultants"
    _inherit = ['mail.thread', 'ir.needaction_mixin', 'utm.mixin']

    name = fields.Char(String='Name')
    linkedin = fields.Char('Linkedin')
    availible = fields.Date('Next availible')
    industry_ids = fields.Many2many('consultant.industry', string='Industry')
    role_ids = fields.Many2many('consultant.role', string='Role')
    customer_ids = fields.Many2many('res.partner', string='Customer Ref', domain="['|', ('customer','=',True), ('supplier','=',True)]")
    user_id = fields.Many2one('res.users', 'Related User')
    competence_ids = fields.Many2many('consultant.competence', string='IT Competence')
    certificate_ids = fields.Many2many('consultant.certificate', string='Certifications')
    priority = fields.Selection([('0','Very Low'),('1','Low'),('2','Normal'),('3','High'),('4','Very High')])
    stage_id = fields.Many2one('consultant.stage', 'Stage', track_visibility='onchange')
    state = fields.Char(related="stage_id.name", string='State')
    partner_id = fields.Many2one('res.partner', 'Vendor')
    color = fields.Integer('Color Index')
    #opportunity_id = fields.Many2one('crm.lead', 'Opportunity', domain="[('type','=','opportunity')]")
    opportunity_ids = fields.Many2many('crm.lead', 'consultant_consult_opportunity_rel', 'consultant_id', 'opportunity_id', 'Opportunities')
  
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """ This function Adds "Remove Active Opportunity" button if Consultant view is loaded from active Opportunity.
        """
        res = super(consultant_consult, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        context = self._context
        if view_type == 'form':
            if 'active_model' in context and context['active_model'] == 'crm.lead' and 'active_id' in context:
                context = context
                dlink_button = etree.Element('button')
                dlink_button.set('string', 'Remove Active Opportunity')
                dlink_button.set('name', 'action_delink_active_opportunity')
                dlink_button.set('type', 'object')
                dlink_button.set('class', 'oe_highlight')
                node = doc.xpath("//field[@name='state']")
                node[0].addnext(dlink_button)
                res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def action_delink_active_opportunity(self):
        context = self._context
        for consultant in self:
            if context and 'active_model' in context and context['active_model'] == 'crm.lead':
                opportunity_id = context['active_id']
                if opportunity_id:
                    self._cr.execute(""" delete from consultant_consult_opportunity_rel where 
                                            opportunity_id=%s and 
                                            consultant_id=%s;"""%(opportunity_id, consultant.id))

class consultant_industry(models.Model):
    _name = 'consultant.industry'
    _description = "Consultant Industry"
    
    name = fields.Char('Name')

class consultant_role(models.Model):
    _name = 'consultant.role'
    _description = "Consultant Role"

    name = fields.Char('Name')

class consultant_competence(models.Model):
    _name = 'consultant.competence'
    _description = "Consultant Competence"

    name = fields.Char('Name')

class consultant_certificate(models.Model):
    _name = 'consultant.certificate'
    _description = "Consultant Certificate"
    
    name = fields.Char('Name')

class consultant_stage(models.Model):
    _name = "consultant.stage"
    _description = "Consultant Stages"

    name = fields.Char('Stage Name', required=True)
    fold = fields.Boolean('Show As Folded', default=False)
    sequence = fields.Integer('Sequence', default=1)
