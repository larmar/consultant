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

    @api.multi
    def compute_total_opportunities(self):
        for consultant in self:
            consultant.total_opportunities = len(consultant.opportunity_ids)

    name = fields.Char(String='Name', track_visibility='onchange')
    linkedin = fields.Char('Linkedin')
    available = fields.Date('Next available', track_visibility='onchange')
    industry_ids = fields.Many2many('consultant.industry', string='Industry/Customers')
    role_ids = fields.Many2many('consultant.role', string='Roles')
    customer_ids = fields.Many2many('res.partner', string='Customer Ref', domain="['|', ('customer','=',True), ('supplier','=',True)]")
    competence_ids = fields.Many2many('consultant.competence', string='IT Competence')
    certificate_ids = fields.Many2many('consultant.certificate', string='Certifications')
    region_ids = fields.Many2many('consultant.region', string='Regions')
    priority = fields.Selection([('0','Very Low'),('1','Low'),('2','Normal'),('3','High'),('4','Very High')], track_visibility='onchange')
    stage_id = fields.Many2one('consultant.stage', 'Stage')
    state = fields.Char(related="stage_id.name", string='Status', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', 'Vendor', track_visibility='onchange')
    color = fields.Integer('Color Index')
    #opportunity_id = fields.Many2one('crm.lead', 'Opportunity', domain="[('type','=','opportunity')]")
    opportunity_ids = fields.Many2many('crm.lead', 'consultant_consult_opportunity_rel', 'consultant_id', 'opportunity_id', 'Opportunities')
    contact_id = fields.Many2one('res.partner', 'Business Contact', track_visibility='onchange')
    consultant_contact_id = fields.Many2one('res.partner', 'Consultant Contact', track_visibility='onchange')
    contact_no = fields.Char(related="contact_id.mobile", string="Telephone")
    category_ids = fields.Many2many('res.partner.category', 'res_partner_category_consultant_rel', 'consultant_id', 'category_id', 'Tags')

    main_role_ids = fields.Many2many('consultant.role.main', 'consultant_consult_role_main_rel', 'consultant_id', 'main_role_id', 'Main Roles')
    main_competence_ids = fields.Many2many('consultant.competence.main', 'consultant_consult_competence_main_rel', 'consultant_id', 'main_competence_id', 'Main Competence')
    future_role_ids = fields.Many2many('consultant.role.future', 'consultant_consult_role_future_rel', 'consultant_id', 'future_role_id', 'Future Roles')
    web_profile_viewed = fields.Boolean('Web profile viewed')
    web_profile_edited = fields.Boolean('Web profile edited')
    user_id = fields.Many2one('res.users', 'Related User')
    active = fields.Boolean(default=True)

    total_opportunities = fields.Integer(compute='compute_total_opportunities', string='Related Opportunities', store=False)

    _sql_constraints = [('consultant_name_unique', 'unique(name)', 'Consultant already exists.')]    

    @api.model_cr
    def init(self):
        """Create Index to ignore case for checking Unique Consultant Name
        """
        try:
            self._cr.execute("CREATE UNIQUE INDEX unique_name_idx on consultant_consult (LOWER(name));")
            _logger.info("Unique Constraint Index successfully created")
        except Exception, e:
            error = "ERROR CREATING CONSTRAINT!\n\nCONSULTANTS WITH DUPLICATE NAMES EXISTS.\n\nError Details:\n%s"%(e)
            _logger.warn(error)
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
        context = self._context
        if context and isinstance(context, dict):
            if 'active_model' in context and context['active_model'] == 'crm.lead':
                res.update(opportunity_ids = [[6, 0, [context.get('active_id', False)]]])
        stage = self.env['ir.model.data'].xmlid_to_res_id('consultant.consultant_stage_draft') or False
        if stage:
            res.update(stage_id = stage)
        return res

    @api.model
    def create(self, vals):
        #keep only 5 main roles:
        if 'main_role_ids' in vals and vals['main_role_ids']:
            vals['main_role_ids'] = [[6, False, vals['main_role_ids'][0][2][-5:] ]]
        #keep only 3 future roles:
        if 'future_role_ids' in vals and vals['future_role_ids']:
            vals['future_role_ids'] = [[6, False, vals['future_role_ids'][0][2][-3:] ]]
        #keep only 10 main competences:
        if 'main_competence_ids' in vals and vals['main_competence_ids']:
            vals['main_competence_ids'] = [[6, False, vals['main_competence_ids'][0][2][-10:] ]]

        res = super(consultant_consult, self).create(vals)

        #update followers: Add Contact to Followers list
        if 'contact_id' in vals and vals['contact_id']:
            followers = []
            user_partner = self.env['res.users'].browse(self._uid).partner_id.id
            followers.append([user_partner, vals['contact_id']])
            res.message_subscribe(partner_ids=followers[0])
        return res

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
                self.message_subscribe(partner_ids=[vals['contact_id']])

        #keep only 5 main roles:
        if 'main_role_ids' in vals and vals['main_role_ids']:
            vals['main_role_ids'] = [[6, False, vals['main_role_ids'][0][2][-5:] ]]
        #keep only 3 future roles:
        if 'future_role_ids' in vals and vals['future_role_ids']:
            vals['future_role_ids'] = [[6, False, vals['future_role_ids'][0][2][-3:] ]]
        #keep only 10 main competences:
        if 'main_competence_ids' in vals and vals['main_competence_ids']:
            vals['main_competence_ids'] = [[6, False, vals['main_competence_ids'][0][2][-10:] ]]
        
        return super(consultant_consult, self).write(vals)

    @api.onchange('main_role_ids')
    def onchange_roles(self):
        if len(self.main_role_ids) > 5:
            warning = {
                'title': 'Maximum Selection Exceeded.',
                'message': 'You can only select up to 5 Main Roles. Options selected more than 5 will be removed.'
            }
            roles = []
            for role in self.main_role_ids:
                roles.append(role.id)
            roles = roles[-5:]
            self.update({'main_role_ids': [[6, 0, roles]]})
            return {'warning': warning}

    @api.onchange('main_competence_ids')
    def onchange_competences(self):
        if len(self.main_competence_ids) > 10:
            competences = []
            for competence in self.main_competence_ids:
                roles.append(competence.id)
            competences = competences[-10:]
            self.main_competence_ids = [[6, 0, competences]]

            warning = {
                'title': 'Maximum Selection Exceeded.',
                'message': 'You can only select up to 10 Main Competences. Options selected more than 10 will be removed.'
            }
            return {'warning': warning}

    @api.onchange('future_role_ids')
    def onchange_future_roles(self):
        if len(self.future_role_ids) > 3:
            roles = []
            for role in self.future_role_ids:
                roles.append(role.id)
            roles = roles[-3:]
            self.future_role_ids = [[6, 0, roles]]

            warning = {
                'title': 'Maximum Selection Exceeded.',
                'message': 'You can only select up to 3 Future Roles. Options selected more than 3 will be removed.'
            }
            return {'warning': warning}

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

    @api.multi
    def action_open_opportunities(self):
        """Open list of Opportunities related to Consutant
        Auto link consultant if new opportunity is created from Opportunity list navigated through consultant.
        """
        action = self.env.ref('crm.crm_lead_opportunities').read()[0]
        opportunity_ids = []
        temp = [opportunity_ids.append(o.id) for o in self.opportunity_ids]
        action['domain'] = [['id', 'in', opportunity_ids]]
        action['context'] = {'consultant_link_id': self.id}
        return action

# Industry

class consultant_industry(models.Model):
    _name = 'consultant.industry'
    _description = "Consultant Industry"
    
    name = fields.Char('Name')

# Roles

class consultant_role(models.Model):
    _name = 'consultant.role'
    _description = "Consultant Role"

    name = fields.Char('Name')

# Main Roles

class consultant_role_main(models.Model):
    _name = 'consultant.role.main'
    _description = "Consultant Main Roles"

    name = fields.Char('Name')

# Future Roles

class consultant_role_future(models.Model):
    _name = 'consultant.role.future'
    _description = "Consultant Future Roles"

    name = fields.Char('Name')

# Competence

class consultant_competence(models.Model):
    _name = 'consultant.competence'
    _description = "Consultant Competence"

    name = fields.Char('Name')

# Main Competences

class consultant_competence_main(models.Model):
    _name = 'consultant.competence.main'
    _description = "Consultant Main Competence"

    name = fields.Char('Name')

# Certificates

class consultant_certificate(models.Model):
    _name = 'consultant.certificate'
    _description = "Consultant Certificate"
    
    name = fields.Char('Name')

# Stages 

class consultant_stage(models.Model):
    _name = "consultant.stage"
    _description = "Consultant Stages"

    name = fields.Char('Stage Name', required=True)
    fold = fields.Boolean('Show As Folded', default=False)
    sequence = fields.Integer('Sequence', default=1)

# Regions

class consultant_region(models.Model):
    _name = "consultant.region"
    _description = "Consultant Regions"

    name = fields.Char('Region Name')
