from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class NoxAlert(models.Model):
    _name = "nox.alert"
    _description = "NOX alert & information"

    # Title of the module
    name = fields.Char('Name', default="NOX alert & information")

    # Alert/Information on my/consultants
    yourProfilesTitle = fields.Char('yourProfilesTitle', default="Your profiles alert.")
    yourProfilesMessage = fields.Text(translate=True)

    # Alert/Information on my/consultants/[userId]
    profileTitle = fields.Char('profilesAlertTitle', default="Profile alert.")
    profileMessage = fields.Text(translate=True)

    @api.model_cr
    def init(self):
        """Add rule to prevent deletion of record(s) from nox_terms table
        """
        try:
            self._cr.execute("CREATE RULE nox_alert_del_protect AS ON DELETE TO nox_alert DO INSTEAD NOTHING;")
        except Exception, e:
            _logger.error("Rule to prevent deletion of record(s) from nox_alert already exists.")
            pass

    @api.multi
    def write(self, vals):
        """Set Nox Alert Update field to False whenever Alert are updated/changed.
        """
        if 'yourProfilesMessage' in vals:
            users = self.env['res.users'].search([('id','>',0)])
            users.write({'nox_alert_read': False})
        return super(NoxAlert, self).write(vals)