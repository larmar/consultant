# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class ConsultantTestTagUpdate(models.TransientModel):
    _name = "consultant.test.tag.update"
    _description = "Consultant - Test Tags Update"

    test_tag_ids = fields.Many2many('consultant.test.tag', string='Test Tags')
    consultant_ids = fields.Many2many('consultant.consult', string='Consultants')

    @api.model
    def default_get(self, fields):
        res = super(ConsultantTestTagUpdate, self).default_get(fields)
        context = self.env.context or {}
        if 'active_model' in context and context['active_model'] == 'consultant.test.tag':
            res.update({'test_tag_ids': [[6, 0, context['active_ids']]]})
        else:
            all_test_tags = []
            test_tags = self.env['consultant.test.tag'].search_read([('id','>',0)], fields=['id'])
            temp = [all_test_tags.append(tag['id']) for tag in test_tags]
            res.update({'test_tag_ids': [[6, 0, all_test_tags]]})
        return res

    @api.multi
    def action_update_tags(self):
        consultants, tags = [], []
        temp = [tags.append(tag.id) for tag in self.test_tag_ids]
        temp = [consultants.append(consultant) for consultant in self.consultant_ids]
        for consultant in consultants:
            consultant.write({'test_tag_ids': [[6, 0, tags]]})
        return True