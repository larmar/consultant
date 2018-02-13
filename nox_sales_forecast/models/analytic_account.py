# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.osv.orm import setup_modifiers

from datetime import datetime
from odoo.addons.nox_sales_forecast.models.date_month_year import MONTHS

from lxml import etree

class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    forecast_analytic_line_ids = fields.One2many('account.analytic.line', 'forecast_analytic_account_id', 'Cost/Revenue Forecast')

    @api.one
    def compute_forecast(self, sale_id):
        for sale in sale_id:
            if sale.state == 'sale':
                years, months = [], []
                start_month, end_month, end_year, end_month = False, False, False, False
                if sale.nox_is_startdate:
                    dt = datetime.strptime(sale.nox_is_startdate, "%Y-%m-%d").date()
                    start_year, start_month = dt.year, dt.month
                    years.append(start_year)
                if sale.nox_is_enddate:
                    dt = datetime.strptime(sale.nox_is_enddate, "%Y-%m-%d").date()
                    end_year, end_month = dt.year, dt.month
                    for y in range(start_year, end_year+1):
                        years.append(y)
                years = list(set(years))

                month_years = []
                for year in years:
                    if year != start_year:
                        start_month = 1

                    if year != end_year:
                        while (start_month < 13):
                            month_years.append([start_month, year])
                            start_month += 1
                    else:
                        while (start_month < end_month+1):
                            month_years.append([start_month, year])
                            start_month += 1

                if month_years:
                    self.generate_forecast_analytics(month_years, sale)
            else:
                unlink_ids = self.env['account.analytic.line'].search([('forecast_type','in',('Cost', 'Revenue')), 
                            ('sale_id','=',sale.id)])
                unlink_ids.unlink()
        return True

    @api.multi
    def generate_forecast_analytics(self, month_years, sale):
        sales_hourly_rate = sale.nox_sales_hourly_rate
        cost_hourly_rate = sale.nox_cost_hourly_rate

        forecast_analytic_ids = []

        for res in month_years:
            date_month = self.env['date.month.year'].search([('month','=',res[0]), ('year','=',res[1])])
            for date_month_id in date_month:
                working_month_id = self.env['date.month.working.hours'].search([('month_year_id','=',date_month_id.id)])
                
                month_year_id = date_month_id.id
                
                month = str(date_month_id.month)
                if len(month) == 1:
                      month = '0'+month
                date = '-'.join([str(date_month_id.year), month, '01'])
                date = datetime.strptime(date, '%Y-%m-%d')

                quantity = working_month_id and working_month_id.working_hours or 0

                for ttype in ['Cost', 'Revenue']:
                    name = ' '.join(['Forecast', ttype, str(res[1]), MONTHS[res[0]]])
                    analytic_forecast_id = self.env['account.analytic.line'].search([('forecast_type','=',ttype), 
                                                                              ('month_year_id','=',month_year_id),
                                                                              ('sale_id','=',sale.id)])
                    if not analytic_forecast_id:
                        amount = sales_hourly_rate * quantity * (sale.nox_ftepercent / 100)
                        if ttype == 'Cost':
                            amount = -(cost_hourly_rate * quantity * (sale.nox_ftepercent / 100))
                        
                        vals = {
                            'name': name,
                            'month_year_id': month_year_id,
                            'unit_amount': quantity,
                            'amount': amount,
                            'forecast_analytic_account_id': sale.related_project_id.id,
                            'account_id': sale.related_project_id.id,
                            'forecast_type': ttype,
                            'sale_id': sale.id,
                            'partner_id': sale.partner_id.id,
                            'date': date,
                        }
                        line_id = self.env['account.analytic.line'].create(vals)
                        forecast_analytic_ids.append(line_id.id)
                    else:
                        amount = sales_hourly_rate * quantity * (sale.nox_ftepercent / 100)
                        if ttype == 'Cost':
                            amount = -(cost_hourly_rate * quantity * (sale.nox_ftepercent / 100)) 

                        analytic_forecast_id.write({'unit_amount': quantity, 'amount': amount, 'date': date})
                        forecast_analytic_ids.append(analytic_forecast_id.id)
        
        #delete non-related analytic lines:
        forecast_analytic_ids = list(set(forecast_analytic_ids))
        unlink_ids = self.env['account.analytic.line'].search([('forecast_type','in',('Cost', 'Revenue')), 
                            ('sale_id','=',sale.id),
                            ('id', 'not in', forecast_analytic_ids)])
        unlink_ids.unlink()
        return True

    @api.multi
    def action_open_analytic_forecast(self):
        if self.forecast_analytic_line_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Cost/Revenue Forecast',
                'res_model': 'account.analytic.line',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'domain': [('id','in',[x.id for x in self.forecast_analytic_line_ids])],
                'target': 'current',
                'context': {'forecast_analytics': True},
            }

class AnalyticAccountLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context or {}
        res = super(AnalyticAccountLine, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if context.get('forecast_analytics', False) and view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='amount']"):
                node.set('string', "Forecast Amount")
                setup_modifiers(node, res['fields']['amount'])
                res['arch'] = etree.tostring(doc)
            for node in doc.xpath("//field[@name='general_account_id']"):
                node.set('invisible', "1")
                setup_modifiers(node, res['fields']['general_account_id'])
                res['arch'] = etree.tostring(doc)
            for node in doc.xpath("//field[@name='move_id']"):
                node.set('invisible', "1")
                setup_modifiers(node, res['fields']['move_id'])
                res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Filter Sales Forecast analytic accounting 
        """
        context = self.env.context or {}

        if 'default_forecast_analytic_account_id' in context:
            if not args:
                [['forecast_analytic_account_id', '=', False]]
            else:
                args.append(['forecast_analytic_account_id', '=', False])
        return super(AnalyticAccountLine, self).search(args, offset, limit, order, count)

    forecast_analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    forecast_type = fields.Selection([('Cost', 'Cost'), ('Revenue', 'Revenue')], 'Forecast Type')
    month_year_id = fields.Many2one('date.month.year', 'Month')
    sale_id = fields.Many2one('sale.order', 'Sales Order')
    team_id = fields.Many2one(related='sale_id.team_id', store=True)
    sale_user_id = fields.Many2one(related="sale_id.user_id", store=True)
    