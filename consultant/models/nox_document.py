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

class NoxDocument(models.Model):
    _name = "nox.document.url"
    _description = "NOX terms & conditions document link"

    name = fields.Char('Name', default="NOX terms & conditions document")
    url = fields.Char('Document URL')

    @api.model_cr
    def init(self):
        """Add rule to prevent deletion of record(s) from nox_document_url table
        """
        try:
            self._cr.execute("CREATE RULE nox_document_url_del_protect AS ON DELETE TO nox_document_url DO INSTEAD NOTHING;")
        except Exception, e:
            _logger.error("Rule to prevent deletion of record(s) from nox_document_url already exists.")
            pass
