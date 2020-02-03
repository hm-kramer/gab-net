# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.
{
    'name': 'Finanzinterface - Datev XML Export',
    'version': '12.0.1.0.20',
    'author': 'syscoon GmbH',
    'license': 'OPL-1',
    'category': 'Accounting',
    'website': 'https://syscoon.com',
    'summary': 'Create XML exports that can be imported in DATEV',
    'external_dependencies': {
        'python': ['PyPDF2']
    },
    'depends': [
        'analytic',
        'sale',
        'syscoon_financeinterface',
    ],
    'data': [
        'views/ecofi_view.xml',
        'views/res_company.xml',
        'wizard/export_ecofi_buchungssaetze.xml',
    ],
    'installable': True,
    'application': False,
}
