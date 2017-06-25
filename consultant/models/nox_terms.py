# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class NoxTerms(models.Model):
    _name = "nox.terms"
    _description = "NOX terms & conditions"

    name = fields.Char('Name', default="NOX Terms & Conditions")
    description = fields.Html("Terms & Conditions")

    @api.model_cr
    def init(self):
        """Add rule to prevent deletion of record(s) from nox_terms table
        """
        try:
            self._cr.execute("CREATE RULE nox_terms_del_protect AS ON DELETE TO nox_terms DO INSTEAD NOTHING;")
        except Exception, e:
            _logger.error("Rule to prevent deletion of record(s) from nox_terms already exists.")
            pass
