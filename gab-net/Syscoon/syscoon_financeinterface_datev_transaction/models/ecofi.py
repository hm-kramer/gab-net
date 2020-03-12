# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api
from odoo.tools import ustr

class ecofi(models.Model):
    _inherit = 'ecofi'
    
    @api.multi
    def field_config(self, move, line, errorcount, partnererror, thislog, thismovename, faelligkeit, datevdict, belegdatum_format=False):
        
        errorcount, partnererror, thislog, thismovename, datevdict, group = super(ecofi, self).field_config(move, line, errorcount, partnererror, thislog, thismovename, faelligkeit, datevdict, belegdatum_format)

        if line.invoice_id:
            inv_lines = self.env['account.invoice.line'].search([('invoice_id', '=', line.invoice_id.id)])
            sale_ids = []
            for line in inv_lines:
                if line.sale_line_ids:
                    for sl in line.sale_line_ids:
                        if not sl.order_id in sale_ids:
                            sale_ids.append(sl.order_id)
            if sale_ids and len(sale_ids) == 1:
                datevdict['Auftragsnummer'] = ustr(sale_ids[0].payment_tx_id.acquirer_reference)
        
        return errorcount, partnererror, thislog, thismovename, datevdict, group