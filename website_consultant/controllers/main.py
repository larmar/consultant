# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016 Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request

from odoo.addons.website_portal.controllers.main import website_account


class website_account(website_account):

    @http.route()
    def account(self, **kw):
        """ Add consultant profiles to main account page """
        response = super(website_account, self).account(**kw)
        partner = request.env.user.partner_id

        Consultant = request.env['consultant.consult']
        profiles_count = Consultant.sudo().search_count([
            ('contact_id', '=', partner.id)
        ])

        response.qcontext.update({
            'profiles_count': profiles_count,
        })
        return response

    @http.route(['/my/consultants', '/my/consultants/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_consultants(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Consultant = request.env['consultant.consult']

        domain = [('contact_id', '=', partner.id)]

        archive_groups = self._get_archive_groups('consultant.consult', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        profiles_count = Consultant.search_count(domain)
        # make pager
        pager = request.website.pager(
            url="/my/consultants",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=profiles_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        consultants = Consultant.search(domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'consultants': consultants,
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/consultants',
        })
        return request.render("website_consultant.portal_my_consultants", values)

    @http.route(['/my/consultants/<int:consultant>'], type='http', auth="user", website=True)
    def consultants_followup(self, consultant=None, **kw):
        consultant = request.env['consultant.consult'].browse([consultant])
        try:
            consultant.check_access_rights('read')
            consultant.check_access_rule('read')
        except AccessError:
            return request.render("website.403")
        return request.render("website_consultant.consultants_followup", {
            'consultant': consultant.sudo(),
        })

    def details_form_validate(self, data):
        error, error_message = super(website_account, self).details_form_validate(data)
        return error, error_message
