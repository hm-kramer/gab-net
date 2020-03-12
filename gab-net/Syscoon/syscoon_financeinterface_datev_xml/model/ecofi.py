#See LICENSE file for full copyright and licensing details.

from odoo import api, models

from datetime import datetime


class ecofi(models.Model):
    _inherit = 'ecofi'

    @api.multi
    def create_vorlauf_xml(self, date_from, date_to):
        vorlaufname = self.env['ir.sequence'].next_by_code('ecofi.vorlauf')
        zeitraum = ''
        if date_from and date_to:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').strftime('%d.%m.%Y')
                date_to = datetime.strptime(date_to, '%Y-%m-%d').strftime('%d.%m.%Y')
            except:
                pass
            zeitraum = str(date_from) + " - " + str(date_to)
        vorlauf_id = self.create({
            'name': str(vorlaufname),
            'zeitraum': zeitraum,
            'export_mode_xml': True,
        })
        return vorlauf_id
