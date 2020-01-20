#See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    enable_datev_checks = fields.Boolean('Perform Datev Checks', default=True)

