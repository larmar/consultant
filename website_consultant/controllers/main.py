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
from odoo.addons.website_mail.controllers.main import _message_post_helper


class website_account(website_account):

    @http.route()
    def account(self, **kw):
        """ Add consultant profiles to main account page """
        response = super(website_account, self).account(**kw)
        user = request.env.user

        Consultant = request.env['consultant.consult']
        profiles_count = Consultant.sudo().search_count([
            ('user_id', '=', user.id)
        ])

        response.qcontext.update({
            'profiles_count': profiles_count,
        })
        return response

    @http.route(['/my/consultants', '/my/consultants/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_consultants(self, page=1, date_begin=None, date_end=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        Consultant = request.env['consultant.consult']

        domain = [('user_id', '=', user.id)]

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

        data = kw
        if data:
            consultant_id = data.get('consultant_id', False)
            consultant = False
            if consultant_id: 
                consultant = request.env['consultant.consult'].browse([int(consultant_id)])
            
            #check if user selected Terms & Conditions check box otherwise show warning message:
            if not consultant.user_id.nox_terms_read:
                main_roles = request.env['consultant.role.main'].sudo().search([])
                main_competence = request.env['consultant.competence.main'].sudo().search([])
                future_roles = request.env['consultant.role.future'].sudo().search([])

                nox_terms = request.env['nox.terms'].sudo().search([], limit=1)
                return request.render("website_consultant.consultants_profile_update", {
                    'consultant': consultant.sudo(),
                    'main_roles': main_roles,
                    'future_roles': future_roles,
                    'main_competence': main_competence,
                    'nox_terms': nox_terms and nox_terms.description or '',
                })

            #update consultant profile:
            main_competence, main_roles, future_roles = [], [], []
            for i in range(1, 6):
                competence_str = 'main_competence'+str(i)
                if competence_str in data and data[competence_str]:
                    main_competence.append(int(data[competence_str]))
                
                mrole_str = 'main_role'+str(i)
                if mrole_str in data and data[mrole_str]:
                    main_roles.append(int(data[mrole_str]))
                
                frole_str = 'future_role'+str(i)
                if frole_str in data and data[frole_str]:
                    future_roles.append(int(data[frole_str]))

            vals = {}
            vals['main_competence_ids'] = [[6, 0, main_competence]]
            vals['main_role_ids'] = [[6, 0, main_roles]]
            vals['future_role_ids'] = [[6, 0, future_roles]]
            vals['available'] = data.get('next_available')
            vals['web_approved'] = True
            consultant.write(vals)
            
            #Log message:
            body = _('Web profile was edited by %s'%(user.name))
            _message_post_helper(res_model='consultant.consult', res_id=consultant.id, message=body, token='', token_field='', message_type='notification', subtype="mail.mt_note", partner_ids=consultant.user_id.partner_id.ids)
            
            return request.redirect('/my/consultants/%s'%(str(consultant_id)))
        return request.render("website_consultant.portal_my_consultants", values)

    @http.route(['/my/consultants/<int:consultant>'], type='http', auth="user", website=True)
    def consultants_followup(self, consultant=None, **kw):
        consultant = request.env['consultant.consult'].browse([consultant])
        try:
            consultant.check_access_rights('read')
            consultant.check_access_rule('read')
        except AccessError:
            return request.render("website.403")
        nox_terms = request.env['nox.terms'].sudo().search([], limit=1)
        
        #Log message:
        user = request.env.user
        body = _('Web profile was viewed by %s'%(user.name))
        _message_post_helper(res_model='consultant.consult', res_id=consultant.id, message=body, token='', token_field='', message_type='notification', subtype="mail.mt_note", partner_ids=consultant.user_id.partner_id.ids)
        
        return request.render("website_consultant.consultants_followup", {
            'consultant': consultant.sudo(),
            'nox_terms': nox_terms and nox_terms.description or '',
        })

    @http.route(['/my/consultants/edit/<int:consultant>'], type='http', auth="user", website=True)
    def consultants_profile_update(self, consultant=None, **kw):
        """TODO : to be used for website portal edit mode
        """
        consultant = request.env['consultant.consult'].browse([consultant])
        try:
            consultant.check_access_rights('read')
            consultant.check_access_rule('read')
        except AccessError:
            return request.render("website.403")
        
        main_roles = request.env['consultant.role.main'].sudo().search([])
        main_competence = request.env['consultant.competence.main'].sudo().search([])
        future_roles = request.env['consultant.role.future'].sudo().search([])

        nox_terms = request.env['nox.terms'].sudo().search([], limit=1)
        return request.render("website_consultant.consultants_profile_update", {
            'consultant': consultant.sudo(),
            'main_roles': main_roles,
            'future_roles': future_roles,
            'main_competence': main_competence,
            'nox_terms': nox_terms and nox_terms.description or '',
        })

    def details_form_validate(self, data):
        error, error_message = super(website_account, self).details_form_validate(data)
        return error, error_message

    @http.route(['/website/confirm-web-approved'], type='http', auth="user", website=True)
    def confirmTermsConditions(self):
        """Check if Portal User has accepted NOX's Terms & Conditions
        """
        currentUser = request.env['res.users'].sudo().browse(request.uid)
        currentUser.write({'nox_terms_read': True})
        return request.redirect('/my/consultants')
