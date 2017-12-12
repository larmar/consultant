# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.addons.consultant_alfresco.models.consultant_alfresco import get_cmis_repo

import logging
_logger = logging.getLogger(__name__)

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
        """Search Consultant documents in Alfresco with selected tags search text;
        update tags if no. of occurances of the search text appears as greater than or equal to Index no set on tag.
        """
        _logger.info('Mass Update Consultant tags functionality has started!')
        _logger.info('Total tags to search for update: %s'%(len(self.test_tag_ids)))
        _logger.info('Total consultants to update: %s'%(len(self.consultant_ids)))
        consultants, tags = [], []

        #Re-test & Valdate Alfresco Connection:
        alfresco_settings = self.env['consultant.alfresco.settings'].search([('id', '>', 0)], limit=1)
        if not alfresco_settings:
            raise ValidationError('Error!\n\nPlease check Alfresco Connection settings or contact your Administrator.')
        repo = get_cmis_repo(alfresco_settings.url, alfresco_settings.login, alfresco_settings.password)
        if not repo:
            raise ValidationError('Failure!\n\nPlease check Alfresco Connection settings or contact your Administrator.')

        temp = [tags.append([tag.id, tag.index_number, tag.search_text]) for tag in self.test_tag_ids]
        temp = [consultants.append(consultant) for consultant in self.consultant_ids]

        consultant_tags_list = {}
        updated_consultant_ids = []
        for consultant in consultants:
            consultant_tags_list[consultant.id] = []
            for tag in tags:
                tag_id, index_number, search_text, search_text_query, search_text_list = tag[0], tag[1], tag[2],tag[2], []
                search_text = search_text.split('OR')
                temp = [search_text_list.append(text.strip()) for text in search_text]

                result = repo.query("select * from cv:curriculumvitae as cv where contains('%s') and \
                                        cv.cv:consultant = '%s'"%(search_text_query, consultant.name))
                doc = result.getResults()
                data, datastring = '', ''
                for d in doc:
                    d.reload()
                    data = d.getContentStream()
                    datastring = data.getvalue()
                    for text in search_text_list:
                        _logger.info('Searching for test tag %s'%(text))
                        count = datastring.count(text.encode('utf-8'))
                        if count >= int(index_number):
                            consultant_tags_list[consultant.id].append(tag_id)
                            break

        #update consultant's test tags
        if consultant_tags_list:
            for consultant_list in consultant_tags_list:
                if consultant_tags_list[consultant_list]:
                    updated_consultant_ids.append(consultant_list)
                    self.env['consultant.consult'].browse([consultant_list]).write({'test_tag_ids': [[6, 0, consultant_tags_list[consultant_list]]]})
        _logger.info("Updated Consultant IDS: %s"%(updated_consultant_ids))
        return True
