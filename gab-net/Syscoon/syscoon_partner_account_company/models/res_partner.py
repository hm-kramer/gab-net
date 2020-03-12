# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_number = fields.Char(string='Customer Number / DATEV-Debitor', company_dependent=True)
    supplier_number = fields.Char(string='Supplier Number / DATEV-Creditor', company_dependent=True)

    @api.model
    def create_accounts(self, ids, context={}):
        auto_account = self.env['ecoservice.partner.auto.account.company']
        partners = self.browse(ids)
        receivable = False#
        payable = False
        ctx = context
        for partner in partners:
            if partner.customer_number:
                receivable = partner.customer_number
            if partner.supplier_number:
                payable = partner.supplier_number
            receivable, payable, receivable_id, payalbe_id = auto_account.get_accounts(partners, receivable, payable, ctx)
            config_id = auto_account.search([('company_id', '=', self.env.user.company_id.id)])
            if config_id.add_number_to_partner_ref and receivable:
                partner.write({
                    'customer_number': receivable,
                    'ref': receivable,
                })
            if config_id.add_number_to_partner_ref and payable:
                partner.write({
                    'supplier_number': payable,
                })
        return receivable, payable, receivable_id, payalbe_id
