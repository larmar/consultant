# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import api, models, fields
from odoo.tools.translate import _
from odoo.osv.orm import setup_modifiers

import logging
_logger = logging.getLogger(__name__)

from lxml import etree

class consultant_consult(models.Model):
    _name = 'consultant.consult'
    _description = "Consultants"
    _inherit = ['mail.thread', 'ir.needaction_mixin', 'utm.mixin']

    name = fields.Char(String='Name', track_visibility='onchange')
    linkedin = fields.Char('Linkedin')
    available = fields.Date('Next available', track_visibility='onchange')
    industry_ids = fields.Many2many('consultant.industry', string='Industry')
    role_ids = fields.Many2many('consultant.role', string='Role')
    customer_ids = fields.Many2many('res.partner', string='Customer Ref', domain="['|', ('customer','=',True), ('supplier','=',True)]")
    competence_ids = fields.Many2many('consultant.competence', string='IT Competence')
    certificate_ids = fields.Many2many('consultant.certificate', string='Certifications')
    priority = fields.Selection([('0','Very Low'),('1','Low'),('2','Normal'),('3','High'),('4','Very High')], track_visibility='onchange')
    stage_id = fields.Many2one('consultant.stage', 'Stage')
    state = fields.Char(related="stage_id.name", string='Status', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', 'Vendor', track_visibility='onchange')
    color = fields.Integer('Color Index')
    #opportunity_id = fields.Many2one('crm.lead', 'Opportunity', domain="[('type','=','opportunity')]")
    opportunity_ids = fields.Many2many('crm.lead', 'consultant_consult_opportunity_rel', 'consultant_id', 'opportunity_id', 'Opportunities')
    contact_id = fields.Many2one('res.partner', 'Contact', track_visibility='onchange')
    category_ids = fields.Many2many('res.partner.category', 'res_partner_category_consultant_rel', 'consultant_id', 'category_id', 'Tags')

    _sql_constraints = [('consultant_name_unique', 'unique(name)', 'Consultant already exists.')]    

    @api.model_cr
    def init(self):
        """Create Index to ignore case for checking Unique Consultant Name
        """
        try:
            self._cr.execute("CREATE UNIQUE INDEX unique_name_idx on consultant_consult (LOWER(name));")
            _logger.info("Unique Constraint Index successfully created")
        except Exception, e:
            error = "Error Creating Constraint!\n\nConsultant with Duplicate Names exist.\n\nError Details:\n%s"%(e)
            _logger.error(error)
            pass

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

    @api.model
    def default_get(self, fields):
        res = super(consultant_consult, self).default_get(fields)
        stage = self.env['ir.model.data'].xmlid_to_res_id('consultant.consultant_stage_draft') or False
        if stage:
            res.update(stage_id = stage)
        return res

    @api.model
    def create(self, vals):
        """Add Contact to Followers list
        """
        if 'contact_id' in vals and vals['contact_id']:
            followers = []
            user_partner = self.env['res.users'].browse(self._uid).partner_id.id
            followers.append([user_partner, vals['contact_id']])
            vals['message_follower_ids'] = [[6, 0, followers[0]]]
        return super(consultant_consult, self).create(vals)

    @api.multi
    def write(self, vals):
        """Add Contact to Followers list
        """        
        if 'contact_id' in vals and vals['contact_id']:
            existing_followers = []
            #get all existing followers of the document:
            for consultant in self:
                for follower in consultant.message_follower_ids:
                    existing_followers.append(follower.partner_id.id)
            if vals['contact_id'] not in existing_followers:
                self._cr.execute("insert into mail_followers(res_model, res_id, partner_id)values('%s', %s, %s);"%(self._name, self.id, vals['contact_id']))
        return super(consultant_consult, self).write(vals)

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
