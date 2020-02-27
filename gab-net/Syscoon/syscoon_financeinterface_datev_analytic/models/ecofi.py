# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models, api

class ecofi(models.Model):
    _inherit = 'ecofi'

    @api.multi
    def field_config(self, move, line, errorcount, partnererror, thislog, thismovename, faelligkeit, datevdict, kost1, kost2):
        if line.analytic_account_id:
            kost1 = line.analytic_account_id.code
            datevdict['KOST1 - Kostenstelle'] = kost1
        if line.analytic_tag_ids:
            kost2 = line.analytic_tag_ids[0].name
            datevdict['KOST2 - Kostenstelle'] = kost2
        res = super(ecofi, self).field_config(move, line, errorcount, partnererror, thislog, thismovename, faelligkeit, datevdict, kost1, kost2)
        return res