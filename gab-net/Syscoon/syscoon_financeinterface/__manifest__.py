#See LICENSE file for full copyright and licensing details.

{   'name': 'Finanzinterface',
    'version': '12.0.2.0.9',
    'depends': ['base', 'account'],
    'author': 'ecoservice, syscoon GmbH',
    'license': 'OPL-1',
    'website': 'https://syscoon.com',
    'summary': 'Main Modul for export of accounting moves',
    'description': """The main modul account_finance provides the basic methods for the finance interface.""",
    'category': 'Accounting',
    'data': [
        'security/ecofi_security.xml',
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/ecofi_sequence.xml',
        'views/ecofi_view.xml',
        'views/res_company_view.xml',
        'wizard/wizard_view.xml'
    ],
    'active': False,
    'installable': True
}
