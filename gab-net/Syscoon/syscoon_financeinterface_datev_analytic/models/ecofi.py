# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models, api

class ecofi(models.Model):
    _inherit = 'ecofi'

    @api.multi
    def field_config(self, move, line, errorcount, partnererror, thislog, thismovename, faelligkeit, datevdict):
        datevdict['KOST1 - Kostenstelle'] = line.analytic_account_id.code
        datevdict['KOST2 - Kostenstelle'] = line.analytic_tag_ids[0].name
        res = super(ecofi, self).field_config(move, line, errorcount, partnererror, thislog, thismovename, faelligkeit, datevdict)
        return res