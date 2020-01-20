# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.
{
    'name': 'Finanzinterface - Automatic Configuration SKR03',
    'version': '12.0.2.0.2',
    'author': 'syscoon GmbH',
    'license': 'OPL-1',
    'category': 'Accounting',
    'website': 'https://syscoon.com',
    'summary': ' Automatic Configuration for SKR03',
    'depends': [
        'base',
        'account',
        'syscoon_financeinterface_datev',
    ],
    'data': [
        'views/res_company.xml',
    ],
    'installable': True,
    'application': False,
}
