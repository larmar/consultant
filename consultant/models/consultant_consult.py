# -*- coding: utf-8 -*-
from openerp import _, api, models, fields

class consultant_consult(models.Model):
    _name = 'consultant.consult'
    _description = "Consultants"
    _inherit = ['mail.thread']
    
    name = fields.Char(String='Name')
    linkedin = fields.Char('Linkedin')
    availible = fields.Date('Next availible')
    industry_ids = fields.Many2many('consultant.industry', string='Industry')
    role_ids = fields.Many2many('consultant.role', string='Role')
    customer_ids = fields.Many2many('res.partner', string='Customer Ref')
    user_id = fields.Many2one('res.users', 'Related User')
    competence_ids = fields.Many2many('consultant.competence', string='IT Competence')
    certificate_ids = fields.Many2many('consultant.certificate', string='Certifications')
    priority = fields.Selection([('0','Very Low'),('1','Low'),('2','Normal'),('3','High'),('4','Very High')])
    state = fields.Selection([('draft','Qualification'),('open','Open'),('progress','Interviewed'),('done','Approved')], 'State')
    partner_id = fields.Many2one('res.partner', 'Vendor')
  

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
