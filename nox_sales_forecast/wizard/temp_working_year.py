# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError

from datetime import datetime

class TempWorkingYear(models.TransientModel):
    _name = "temp.working.year"

    year = fields.Integer('Year', size=4, required=True)

    @api.multi
    def action_generate_working_year_months(self):
        year = datetime.now().year
        from_year = year - 2
        to_year = year + 20
        for rec in self:
            if len(str(rec.year)) != 4:
                raise ValidationError(("Invalid Year!"))

            if rec.year > to_year or rec.year < from_year:
                raise ValidationError(("Validation Error!\n\nYou can only generate working months between year %s and %s."%(from_year, to_year)))

            return self.env['date.month.year'].generate_year_months(rec.year)
            