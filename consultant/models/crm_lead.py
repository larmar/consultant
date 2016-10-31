#-*- coding:utf-8 -*-

from openerp.osv import osv, fields

class crm_lead(osv.osv):
    _inherit = "crm.lead"

    def _consultant_count(self, cr, uid, ids, field_name, arg, context=None):
        count = 0
        for rec in self.browse(cr, uid, ids):
            for consultant in rec.consultant_ids:
                count += 1
        return {ids[0]: count}

    _columns = {
        'consultant_ids': fields.many2many('consultant.consult', 'consultant_consult_opportunity_rel', 'opportunity_id', 'consultant_id', 'Consultants'),
        'consultant_count': fields.function(_consultant_count, string='# Consultants', type='integer'),
    }

    def action_open_consultants(self, cr, uid, ids, context=None):
        """
        Open Consultants related to current opportunity.
        :return dict: dictionary value Consultants view
        """
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'consultant', 'action_consultant_consult', context)
        
        cr.execute(""" select consultant_id from consultant_consult_opportunity_rel
                                where opportunity_id=%s """%(ids[0]))
        result = cr.fetchall()
        consultants = []
        for r in result:
            r = r[0]
            consultants.append(r)
        res['domain'] = [['id', 'in', consultants]]
        return res