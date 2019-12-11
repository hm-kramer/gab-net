# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models, api


autoaccounts = {
    'l10n_de_skr04.chart_skr04_1181': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_1186': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_3260': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_3272': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4125': {'datev_steuer': ['l10n_de_skr04.tax_eu_sale_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': True},
    'l10n_de_skr04.chart_skr04_4136': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4186': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4300': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4310': {'datev_steuer': ['l10n_de_skr04.tax_ust_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4315': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4320': {'datev_steuer': ['l10n_de_skr04.tax_free_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4336': {'datev_steuer': ['l10n_de_skr04.tax_eu_sale_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': True},
    'l10n_de_skr04.chart_skr04_4400': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4566': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4569': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4576': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4579': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4610': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4620': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4630': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4640': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4645': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4646': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4650': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4660': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4670': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4680': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4710': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4720': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4724': {'datev_steuer': ['l10n_de_skr04.tax_free_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4725': {'datev_steuer': ['l10n_de_skr04.tax_ust_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4726': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4727': {'datev_steuer': ['l10n_de_skr04.tax_eu_sale_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': True},
    'l10n_de_skr04.chart_skr04_4731': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4736': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4741': {'datev_steuer': ['l10n_de_skr04.tax_free_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4743': {'datev_steuer': ['l10n_de_skr04.tax_free_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4745': {'datev_steuer': ['l10n_de_skr04.tax_eu_sale_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': True},
    'l10n_de_skr04.chart_skr04_4746': {'datev_steuer': ['l10n_de_skr04.tax_ust_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': True},
    'l10n_de_skr04.chart_skr04_4748': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': True},
    'l10n_de_skr04.chart_skr04_4750': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4760': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},       
    'l10n_de_skr04.chart_skr04_4780': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4790': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4836': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4845': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4862': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4941': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4945': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4947': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4948': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_4948': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5110': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5130': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5160': {'datev_steuer': ['l10n_de_skr04.tax_eu_7_purchase_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5162': {'datev_steuer': ['l10n_de_skr04.tax_eu_19_purchase_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5191': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5192': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5300': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5400': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5420': {'datev_steuer': ['l10n_de_skr04.tax_eu_7_purchase_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5425': {'datev_steuer': ['l10n_de_skr04.tax_eu_19_purchase_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5430': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5435': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5710': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5714': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5715': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5717': {'datev_steuer': ['l10n_de_skr04.tax_eu_7_purchase_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5718': {'datev_steuer': ['l10n_de_skr04.tax_eu_19_purchase_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5720': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5724': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5725': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5731': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5734': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5736': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5738': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5741': {'datev_steuer': ['l10n_de_skr04.tax_eu_19_purchase_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5741': {'datev_steuer': ['l10n_de_skr04.tax_eu_7_purchase_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5750': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5754': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5755': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5760': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5780': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5784': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5785': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5790': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5906': {'datev_steuer': ['l10n_de_skr04.tax_vst_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_5908': {'datev_steuer': ['l10n_de_skr04.tax_vst_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_6281': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_6286': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_6885': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_6931': {'datev_steuer': ['l10n_de_skr04.tax_ust_7_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_6932': {'datev_steuer': ['l10n_de_skr04.tax_free_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_6932': {'datev_steuer': ['l10n_de_skr04.tax_ust_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_6936': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
    'l10n_de_skr04.chart_skr04_6938': {'datev_steuer': ['l10n_de_skr04.tax_ust_19_eu_skr04'], 'automatic': True, 'datev_steuer_erforderlich': True, 'ustuebergabe': False},
}


class AccountAccount(models.Model):
    _inherit = 'account.account'

    def _set_account_autoaccount(self, company_id):
        for key, values in autoaccounts.items():
            try:
                template_id = self.env.ref(key)
                account_id = self.env['account.account'].search([('name', '=', template_id.name), ('company_id', '=', company_id)])
                for aid in account_id:
                    if aid and not aid.automatic:
                        tax_keys = []
                        if values['datev_steuer']:
                            for val in values['datev_steuer']:
                                tax_templ_id = self.env.ref(val)
                                tax_id = self.env['account.tax'].search([('name', '=', tax_templ_id.name), ('company_id', '=', company_id)])
                                if tax_id:
                                    tax_keys.append(tax_id.id)
                        aid.update({
                            'ustuebergabe': values['ustuebergabe'],
                            'automatic': values['automatic'],
                            'datev_steuer': [(6, 0, tax_keys)],
                            'datev_steuer_erforderlich': values['datev_steuer_erforderlich'],
                        })
            except:
                continue