# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.


import os

from odoo import models, api
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader

jenv = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__))))


class DATEVInvoiceExport(models.AbstractModel):
    _name = 'export.datev.invoice.info'
    _inherit = 'export.datev'
    _schema = 'document_v030.xsd'

    @api.model
    def inv_type(self, inv):
        return 'Outgoing' if 'out' in inv.type else 'Incoming'

    @api.model
    def get_keywords(self, inv):
        return ', '.join(
            filter(None, [inv.partner_id.name, inv.partner_id.ref]))

    @api.model
    def get_error_msg(self, doc, *args):
        return "Failed to make export info xml"

    @api.model
    def named(self, tupl):
        Doc = namedtuple('Doc', [
            'xml_path', 'pdf_path', 'inv_name',
            'partner_name', 'partner_ref',
            'type', 'keywords',
        ])
        inv, name, xml_path, pdf_path = tupl
        return Doc._make((xml_path,
                          pdf_path,
                          name,
                          inv.partner_id.name,
                          inv.partner_id.ref,
                          self.inv_type(inv),
                          self.get_keywords(inv),
                          ))

    @api.model
    def get_main_company(self):
        return self.env.user.company_id

    @api.model
    def get_xml(self, docs, export_mode, timestamp):
        template = jenv.get_template('invoice_info.xml')
        company = self.get_main_company()
        return template.render({
            'timestamp': timestamp,
            'docs': map(self.named, docs),
            'consultant_number': company.tax_accountant_id,
            'client_number': company.client_id,
        })
