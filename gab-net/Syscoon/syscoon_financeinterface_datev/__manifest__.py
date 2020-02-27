# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    'name': 'Finanzinterface - Datev ASCII Export',
    'version': '12.0.2.0.13',
    'author': 'ecoservice, syscoon GmbH',
    'license': 'OPL-1',
    'website': 'https://syscoon.com',
    'summary': 'Export of account moves to Datev',
    'description': """The module account_financeinterface_datev provides methods to convert account moves to the Datevformat (Datev Dok.-Nr.: 1036228).""",
    'category': 'Accounting',
    'depends': [
        'syscoon_financeinterface'
    ],
    'data': [
        'views/account_view.xml',
        'data/account_cron.xml',
        'views/res_company_view.xml',
        'views/account_invoice_view.xml',
    ],
    'active': False,
    'installable': True
}
