# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

{
    'name': 'Partner Debitoren- / Kreditorenkonto Automatik',
    'version': '12.0.1.0.2',
    'author': 'ecoservice, syscoon GmbH',
    'license': 'OPL-1',
    'category': 'Accounting',
    'website': 'https://syscoon.com',
    'depends': [
        'syscoon_partner_account_company',
        'sale',
        'purchase',
    ],
    'description': """If a partner is created a new debit and credit account will be created automatically.""",
    'data': [
        'views/partner_auto_account.xml',
    ],
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [],
    'active': False,
    'installable': True
}
