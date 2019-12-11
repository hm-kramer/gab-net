# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        res = super(AccountInvoice, self).create(vals)
        if res['partner_id']:
            partner = res['partner_id']
            if partner.parent_id:
                partner = partner.parent_id
            if partner.customer and res['type'] in ['out_invoice', 'out_refund']:
                partner_default_id = str(partner['property_account_receivable_id'].id)
                default_property_id = self.env['ir.property'].search(['&', (
                    'name', '=', 'property_account_receivable_id'), ('res_id', '=', None)])
                if default_property_id:
                    property_id = str(default_property_id['value_reference'].split(',')[1])
                    if property_id == partner_default_id:
                        ctx = dict(self._context)
                        ctx['type'] = 'receivable'
                        receivable, payable, receivable_id, payalbe_id = self.env['res.partner'].create_accounts(partner.id, ctx)
                        if receivable_id:
                            res['account_id'] = receivable_id
            if partner.supplier and res['type'] in ['in_invoice', 'in_refund']:
                partner_default_id = str(partner['property_account_payable_id'].id)
                default_property_id = self.env['ir.property'].search(['&', (
                    'name', '=', 'property_account_payable_id'), ('res_id', '=', None), ('company_id', '=', self.env.user.company_id.id)])
                if default_property_id:
                    property_id = str(default_property_id[0]['value_reference'].split(',')[1])
                    if property_id == partner_default_id:
                        ctx = dict(self._context)
                        ctx['type'] = 'payable'
                        receivable, payable, receivable_id, payalbe_id = self.env['res.partner'].create_accounts(partner.id, ctx)
                        if payalbe_id:
                            res['account_id'] = payalbe_id
        return res