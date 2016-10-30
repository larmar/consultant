# -*- coding: utf-8 -*-
from openerp import _, api, models, fields

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
