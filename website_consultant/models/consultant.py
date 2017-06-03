# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-Today Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class Consultant(models.Model):
    _inherit = "consultant.consult"

    @api.multi
    def portal_get_main_roles(self, tag=0):
        result = 0
        tag = int(tag)
        if tag != 0:
            roles = []
            for role in self.main_role_ids:
                roles.append(role.id)
            if len(roles) >= tag:
                result = roles[tag-1]
        return result

    @api.multi
    def portal_get_main_competence(self, tag=0):
        result = 0
        tag = int(tag)
        if tag != 0:
            competences = []
            for c in self.main_competence_ids:
                competences.append(c.id)
            if len(competences) >= tag:
                result = competences[tag-1]
        return result

    @api.multi
    def portal_get_future_roles(self, tag=0):
        result = 0
        tag = int(tag)
        if tag != 0:
            roles = []
            for role in self.future_role_ids:
                roles.append(role.id)
            if len(roles) >= tag:
                result = roles[tag-1]
        return result