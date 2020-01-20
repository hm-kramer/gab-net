# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models, api, fields, _
from odoo.exceptions import Warning
from functools import partial, reduce
from collections import namedtuple
from itertools import chain
from operator import add
import logging
import os
import re
import zipfile


_logger = logging.getLogger(__name__)


class AccountDATEVExport(models.TransientModel):
    _name = 'account.datev.export'

    type = fields.Selection(
        selection=[('invoice', 'Invoices'),],
        string='Type', default='invoice')
    done = fields.Boolean()
    date_from = fields.Date('Date from')
    date_to = fields.Date('Date to')

    @api.model
    def get_invoice_pdf(self, inv):
        """
        Return the PDF report
        for a given invoice
        """
        datas = False
        content = False
        Report = namedtuple('Report', ['content', 'filetype'])
        if inv.type in ['in_invoice', 'in_refund']:
            datas = self.env['ir.attachment'].search([
            ('datas_fname', 'like', inv.reference),
            ('res_model', '=', 'account.invoice'),
            ('res_id', '=', inv.id)], limit=1)
        if datas:
            attach = datas._file_read(datas.store_fname)
            content, filetype = attach.decode('base64'), 'pdf'
        else:
            content, filetype = self.env.ref('account.account_invoices').render_qweb_pdf([inv.id])
        return Report._make((content, filetype))

    @api.model
    def get_invoice_xml(self, inv):
        """
        Return the XML Export
        for a given invoice
        """
        return self.env['export.datev.invoice'].get_validated_xml(inv)

    @api.model
    def get_cash_xml(self, cash):
        """
        Return the XML Export
        for a given cash statement
        """
        pass

    @api.model
    def get_invoices(self):
        """
        Returns the invoices that
        need to be exported
        """
        return self.env['account.invoice'].search([
            ('datev_export', '=', False),
            ('state', 'in', ('open', 'paid')),
            ('amount_total', '!=', 0),
            ('date_invoice', '>=', self.date_from),
            ('date_invoice', '<=', self.date_to)
        ])

    @api.model
    def get_export_dir_path(self):
        path = self.env['ir.config_parameter'].get_param(
            'account.invoice.export.path')
        if not path or not os.path.exists(path) or not os.path.isdir(path):
            raise Warning(
                _("The directory path '%s' doesn't exist. "
                  "You can set a different path to the directory "
                  "in ir.config_parameter "
                  "under the key 'account.invoice.export.path'" % path))
        return path

    @api.model
    def write_export_invoice(self, dir_path, inv_doc):
        """
        Either both files are written or niether.
        """
        id, name, xml, report = inv_doc

        xml_path = os.path.join(dir_path, name + '.xml')
        pdf_path = os.path.join(dir_path, '.'.join([name, report.filetype]))
        try:
            with open(xml_path, 'w') as f:
                xml = xml.decode(encoding='utf-8', errors='strict')
                f.write(xml)
            with open(pdf_path, 'wb') as f:
                f.write(report.content)
            return (id, name, xml_path, pdf_path)
        except Exception:
            _logger.error(
                _("An error occured while saving %s export in %s"
                  % (name, dir_path)))
            if os.path.exists(xml_path):
                os.remove(xml_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            raise

    @api.model
    def write_export_invoice_info(self, dir_path, xml, timestamp):
        xml_path = os.path.join(dir_path, 'document.xml')
        try:
            with open(xml_path, 'w') as f:
                f.write(xml.decode("utf-8"))
            return xml_path
        except Exception:
            _logger.error(
                _("An error occured while saving %s export in %s"
                  % (timestamp, dir_path)))
            if os.path.exists(xml_path):
                os.remove(xml_path)
            raise

    @api.model
    def get_export_invoice_info_xml(self, written_doc, timestamp):
        return self.env['export.datev.invoice.info'].get_validated_xml(
            written_doc, False, timestamp)

    @api.model
    def create_dir(self, parent, timestamp):
        dir_name = ('datev_export_invoice_%s'
                    % timestamp)
        dir_path = os.path.join(parent, dir_name)
        os.mkdir(dir_path)
        return dir_path

    @api.model
    def write_docs(self, docs, timestamp, dir_path):
        """
        Consumes the docs generator and additionally
        writes an xml file with info of the made exports
        """
        WrittenDoc = namedtuple(
            'WrittenDoc', ['inv', 'name', 'xml_path', 'pdf_path'])

        def join_recs(list_of_recs):
            return reduce(add, list_of_recs)

        def get_inv(tupl):
            return tupl[0]

        def clean_tstamp(tstamp):
            return tstamp.replace('T', ' ')

        def get_doc_paths(doc):
            return doc.pdf_path, doc.xml_path

        written_docs = []
        inv_info_xml_path = None
        for id, name, xml_path, pdf_path in docs:
            inv = self.env['account.invoice'].browse(id)
            written_docs.append(
                WrittenDoc._make((inv, name, xml_path, pdf_path)))
            _logger.info(_('%s has been exported' % name))
            _logger.info(xml_path)
            _logger.info(pdf_path)
            export_info_xml = self.get_export_invoice_info_xml(
                written_docs, timestamp)
            inv_info_xml_path = self.write_export_invoice_info(
                dir_path, export_info_xml, timestamp)
            join_recs(map(get_inv, written_docs)).write({
                'datev_export': True,
                'datev_export_date': clean_tstamp(timestamp),
            })
        return filter(None, chain(
            (inv_info_xml_path,),
            *map(get_doc_paths, written_docs)))

    def make_zip_file(self, export_path, doc_paths, timestamp):
        zip_path = os.path.join(export_path, timestamp + '.zip')
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as f:
                for path in doc_paths:
                    f.write(path, os.path.basename(path))
        except Exception:
            _logger.error(
                _("An error occured while making "
                  "a zip archive for %s export in %s"
                  % (timestamp, export_path)))
            _logger.error(_("Files that weren't zipped: %s" % doc_paths))
            if os.path.exists(zip_path):
                os.remove(zip_path)

    @api.model
    def make_export_invoice(self):
        def clean_inv_number(inv):
            """
            Return a cleaned invoice
            number consisting only of
            alphanumeric characters
            """
            return ''.join(re.findall(r'\w+', inv.number or ''))

        export_time = 'T'.join(fields.Datetime.now().split(' '))
        export_path = self.get_export_dir_path()
        invoices = self.get_invoices()
        inv_xmls = map(self.get_invoice_xml, invoices)
        inv_pdfs = map(self.get_invoice_pdf, invoices)
        inv_numbers = invoices.mapped(clean_inv_number)
        inv_ids = invoices.ids
        inv_docs = filter(all, zip(inv_ids, inv_numbers, inv_xmls, inv_pdfs))
        dir_path = self.create_dir(export_path, export_time)
        docs = map(
            partial(self.write_export_invoice, dir_path), inv_docs)
        doc_paths = self.write_docs(docs, export_time, dir_path)
        if doc_paths:
            self.make_zip_file(export_path, doc_paths, export_time)
        return True

    @api.model
    def make_export_cash(self):
        pass

#    @api.multi
#    def make_export_wizard(self):
#        self.done = True
#        wizard_view_id = self.env.ref(
#            'syscoon_financeinterface_datev_xml.view_account_datev_export').id
#        if self.type == 'invoice':
#            self.make_export_invoice()
#        else:
#            pass
#        return {
#            'name': _('Account DATEV Export'),
#            'view_type': 'form',
#            'view_mode': 'form',
#            'res_model': 'account.datev.export',
#            'res_id': self.id,
#            'view_id': wizard_view_id,
#            'type': 'ir.actions.act_window',
#            'target': 'new',
#        }

    @api.multi
    def make_export_wizard(self, date_from, date_to):
        self.write({
            'done': True,
            'date_from': date_from,
            'date_to': date_to,
        })
        wizard_view_id = self.env.ref(
            'syscoon_financeinterface_datev_xml.view_account_datev_export').id
        if self.type == 'invoice':
            self.make_export_invoice()
        else:
            pass
        return {
            'name': _('Account DATEV Export'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.datev.export',
            'res_id': self.id,
            'view_id': wizard_view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }