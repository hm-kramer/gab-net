#See LICENSE file for full copyright and licensing details.

{
    'name': 'Finanzinterface - DATEV Account Export',
    'description': """Exporting account data in DATEV CSV format""",
    'version': '12.0.2.0.8',
    'author': 'syscoon GmbH',
    'license': 'OPL-1',
    'category': 'Accounting',
    'website': 'https://syscoon.com',
    'depends': [
        'base',
        'account',
        'syscoon_financeinterface_datev',
    ],
    'data': [
        'views/datev_export_view.xml',
        'views/partner_view.xml',
        'views/account_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
