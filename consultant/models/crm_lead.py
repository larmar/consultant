#-*- coding:utf-8 -*-

from openerp.osv import osv, fields

class crm_lead(osv.osv):
    _inherit = "crm.lead"

    def _consultant_count(self, cr, uid, ids, field_name, arg, context=None):
        Consultants = self.pool['consultant.consult']
        return {
            opp_id: Consultants.search_count(cr,uid, [('opportunity_id', '=', opp_id)], context=context)
            for opp_id in ids
        }

    _columns = {
        #'consultant_ids': fields.many2many('consultant.consult', 'crm_lead_consultant_consult_rel', 'opportunity_id', 'consultant_id', 'Consultants'),
        'consultant_count': fields.function(_consultant_count, string='# Consultants', type='integer'),
    }

    def action_open_consultants(self, cr, uid, ids, context=None):
        """
        Open Consultants related to current opportunity.
        :return dict: dictionary value Consultants view
        """
        opportunity = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'consultant', 'action_consultant_consult', context)
        res['context'] = {
            'search_default_opportunity_id': opportunity.id or False,
            'default_opportunity_id': opportunity.id or False,
        }
        return res