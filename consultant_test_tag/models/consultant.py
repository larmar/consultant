# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ConsultantConsult(models.Model):
    _inherit = "consultant.consult"

    test_tag_ids = fields.Many2many('consultant.test.tag', 'consultant_consult_test_tag_rel', 'consultant_id', 'test_tag_id', 'Test Tags')
    

class ConsultantTestTag(models.Model):
    _name = "consultant.test.tag"
    _description = "Consultant - Test Tags"

    name = fields.Char('Tag', required=True)
    index_number = fields.Char('Index Number', size=1, default='5')
    search_text = fields.Char('Search Text')

    @api.constrains('index_number')
    def check_index_number(self):
        if ord(self.index_number) not in (49, 50, 51, 52, 53, 54, 55, 56, 57):
            raise ValidationError('Invalid Index Number!\n\nIndex number can only be number between 1-9.')


class consultant_industry(models.Model):
    _inherit = 'consultant.industry'

    index_number = fields.Char('Index Number', size=1, default='5')

    @api.constrains('index_number')
    def check_index_number(self):
        if ord(self.index_number) not in (49, 50, 51, 52, 53, 54, 55, 56, 57):
            raise ValidationError('Invalid Index Number!\n\nIndex number can only be number between 1-9.')


class consultant_role(models.Model):
    _inherit = 'consultant.role'

    index_number = fields.Char('Index Number', size=1, default='5')

    @api.constrains('index_number')
    def check_index_number(self):
        if ord(self.index_number) not in (49, 50, 51, 52, 53, 54, 55, 56, 57):
            raise ValidationError('Invalid Index Number!\n\nIndex number can only be number between 1-9.')


class consultant_competence(models.Model):
    _inherit = 'consultant.competence'

    index_number = fields.Char('Index Number', size=1, default='5')

    @api.constrains('index_number')
    def check_index_number(self):
        if ord(self.index_number) not in (49, 50, 51, 52, 53, 54, 55, 56, 57):
            raise ValidationError('Invalid Index Number!\n\nIndex number can only be number between 1-9.')


class consultant_region(models.Model):
    _inherit = "consultant.region"

    index_number = fields.Char('Index Number', size=1, default='5')

    @api.constrains('index_number')
    def check_index_number(self):
        if ord(self.index_number) not in (49, 50, 51, 52, 53, 54, 55, 56, 57):
            raise ValidationError('Invalid Index Number!\n\nIndex number can only be number between 1-9.')

