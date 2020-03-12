#See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.exceptions import UserError

from functools import partial, reduce
from collections import namedtuple
from itertools import chain
from operator import add
from zipfile import ZipFile
import base64
import logging
import os
import shutil
import re
import PyPDF2
import io

_logger = logging.getLogger(__name__)


class export_ecofi(models.TransientModel):
    _inherit = 'export.ecofi'

    export_mode = fields.Selection(selection_add=[('datev_xml', 'DATEV XML')])
    export_xml_mode = fields.Selection([('standard', 'Standard'), ('extended', 'Extended')],
        string='XML-Export Methode',
        help='Export Methode: Standard: without Accounts, Extended: with Accounts',
        default=lambda self: self.env.user.company_id.export_xml_mode
    )
    xml_errors = fields.Text('Export Errors')


    @api.model
    def get_invoice_pdf(self, inv):
        """
        Return the PDF report
        for a given invoice
        """
        module_xml_invoice = self.env['ir.module.module'].search([('name', '=', 'facturx')])
        if module_xml_invoice.state == 'installed':
            raise UserError(_('The Module Import Vendor Bills From XML (account_facturx) is installed. With this module installed, the DATEV-XML-Export will not work. Please uninstall it!'))
        datas = False
        content = False
        Report = namedtuple('Report', ['content', 'filetype'])
        if inv.type in ['in_invoice', 'in_refund']:
            datas = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.invoice'),
            ('res_id', '=', inv.id)])
        if inv.type in ['out_invoice', 'out_refund']:
            datas = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.invoice'),
            ('res_id', '=', inv.id)])
        if datas:
            content, filetype = self.merge_pdf(datas, inv)
        else:
            content, filetype = self.env.ref('account.account_invoices').render_qweb_pdf([inv.id])
        reportm = Report._make((content, filetype))
        return reportm

    @api.model
    def merge_pdf(self, datas, inv):
        """
        concentrate pdfs if the number of the attachemnts is > 1
        otherwise use odoo standard for reading the pdf
        """
        if len(datas) > 1:
            merger = PyPDF2.PdfFileMerger(strict=False)
            myio = io.BytesIO()
            for pdf in datas:
                attach = pdf._file_read(pdf.store_fname)
                content = base64.b64decode(attach)
                content = io.BytesIO(content)
                try:
                    merger.append(content, import_bookmarks=False)
                except:
                    raise UserError(_('Export stopped! \n Invoice %s can not exported, because the PDF has no EOF-Marker. \n Please repair it and start the export again.' % inv.number))
            merger.write(myio)
            merger.close()
            content, filetype = myio.getvalue(), 'pdf'
        else:
            attach = datas._file_read(datas.store_fname)
            content, filetype = base64.b64decode(attach), 'pdf'
        return content, filetype

    @api.model
    def get_invoice_xml(self, inv, vorlauf_id):
        """
        Return the XML Export
        for a given invoice
        """
        valid_xml = self.env['export.datev.invoice'].get_validated_xml(inv, vorlauf_id, self.export_xml_mode)
        return valid_xml

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
        if not self.export_xml_customer_invoices and not self.export_xml_vendor_invoices:
            raise UserError(_('Please select one kind of Invoices!'))
        types = []
        if self.export_xml_customer_invoices:
            types.append('out_invoice')
            types.append('out_refund')
        if self.export_xml_vendor_invoices:
            types.append('in_invoice')
            types.append('in_refund')
        return self.env['account.invoice'].search([
            ('vorlauf_id', '=', False),
            ('state', 'in', ('open', 'paid')),
            ('amount_total', '!=', 0),
            ('date_invoice', '>=', self.date_from),
            ('date_invoice', '<=', self.date_to),
            ('type', 'in', types)
        ])

    @api.model
    def get_export_dir_path(self):
        path = '/tmp/odoo/datev_xml_export'
        if not os.path.exists(path) or not os.path.isdir(path):
            os.makedirs(path, exist_ok=True)
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
        if not xml:
            xml = False
        if xml:
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
            written_doc, self.vorlauf_id, timestamp)

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
            return dir_path + '/' + doc.pdf_path, dir_path + '/' + doc.xml_path

        written_docs = []
        inv_info_xml_path = None
        for id, name, xml_path, pdf_path in docs:
            inv = self.env['account.invoice'].browse(id)
            xp = xml_path.replace(dir_path + '/', '')
            pp = pdf_path.replace(dir_path + '/', '')
            written_docs.append(
                WrittenDoc._make((inv, name, xp, pp)))
            _logger.info(_('%s has been exported' % name))
            _logger.info(xml_path)
            _logger.info(pdf_path)
            export_info_xml = self.get_export_invoice_info_xml(
                written_docs, timestamp)
            inv_info_xml_path = self.write_export_invoice_info(
                dir_path, export_info_xml, timestamp)
        return filter(None, chain(
            (inv_info_xml_path,),
            *map(get_doc_paths, written_docs)))

    def make_zip_file(self, export_path, doc_paths, timestamp):
        zip_path = os.path.join(export_path, timestamp + '.zip')
        with ZipFile(zip_path, 'w') as f:
            for path in doc_paths:
                f.write(path, os.path.basename(path))

        datas_file = open(zip_path, 'rb')
        datas_content = datas_file.read()

        document = self.env['ir.attachment'].create({
            'name': '%s.zip' % self.vorlauf_id.name,
            'datas_fname': '%s.zip' % self.vorlauf_id.name,
            'res_model': 'ecofi',
            'res_id': self.vorlauf_id.id,
            'type': 'binary',
            'datas': base64.b64encode(datas_content),
        })

        self.vorlauf_id.write({
            'ecofi_document_ids': [(6, 0, document.ids)]
        })

        if os.path.exists(zip_path):
            os.remove(zip_path)

        return document

    @api.model
    def make_export_invoice(self):
        def clean_inv_number(inv):
            """
            Return a cleaned invoice
            number consisting only of
            alphanumeric characters
            """
            return ''.join(re.findall(r'\w+', inv.number or ''))
        
        user = self.env['res.users'].browse(self._uid)
        if not user.company_id.tax_accountant_id or not user.company_id.client_id:
            raise UserError(_('Plese set a Tax Accountant ID or Client ID under Settings -> Users & Comapnies -> Companies.'))

        export_time = fields.Datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        export_path = self.get_export_dir_path()
        invoices = self.get_invoices()
        if not invoices:
            raise UserError(_('There are no invoices to export in the selected date range.'))
        self.vorlauf_id = self.env['ecofi'].create_vorlauf_xml(self.date_from, self.date_to)
        inv_xmls = []
        for inv in invoices:
            inv_xmls.append(self.get_invoice_xml(inv, self.vorlauf_id))
        inv_pdfs = map(self.get_invoice_pdf, invoices)
        inv_numbers = invoices.mapped(clean_inv_number)
        inv_ids = invoices.ids
        inv_docs = filter(all, zip(inv_ids, inv_numbers, inv_xmls, inv_pdfs))
        dir_path = self.create_dir(export_path, export_time)
        docs = map(partial(self.write_export_invoice, dir_path), inv_docs)
        doc_paths = self.write_docs(docs, export_time, dir_path)
        if doc_paths:
            self.make_zip_file(export_path, doc_paths, export_time)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        if self.vorlauf_id:
            self.set_vorlauf_to_invoice(invoices)
        if self.vorlauf_id.invoice_error_ids:
            self.remove_vorlauf_to_invoice(self.vorlauf_id.invoice_error_ids)
        return self.vorlauf_id.id

    @api.model
    def make_export_cash(self):
        pass

    @api.model
    def set_vorlauf_to_invoice(self, invoices):
        invoices.write({
            'vorlauf_id': self.vorlauf_id.id
        })
        for invoice in invoices:
            invoice.move_id.write({
                'vorlauf_id': self.vorlauf_id.id
            })

    @api.model
    def remove_vorlauf_to_invoice(self, invoices):
        invoices.write({
            'vorlauf_id': False
        })
        for invoice in invoices:
            invoice.move_id.write({
                'vorlauf_id': False
            })