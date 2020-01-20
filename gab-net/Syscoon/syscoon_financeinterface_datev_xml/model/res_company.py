#See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    export_xml_mode = fields.Selection([('standard', 'Standard'), ('extended', 'Extended')],
        string='XML-Export Methode',
        help='Export Methode: Standard: without Accounts, Extended: with Accounts',
        default='standard'
    )