# -*- coding: iso-8859-1 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from lxml import etree

from odoo import models


class DATEVInvoiceExport(models.AbstractModel):
    _name = 'export.datev.invoice.info.scheme'
    _inherit = 'export.datev'

    def render_invoice_info(self, timestamp, docs, tax_accountant_id, client_id):
        XSI = "http://www.w3.org/2001/XMLSchema-instance"
        attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
        nsmap = {
                    None: "http://xml.datev.de/bedi/tps/document/v05.0",
                    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                }
        root = etree.Element(
            "archive", 
            {
                attr_qname: "http://xml.datev.de/bedi/tps/document/v05.0 document_v050.xsd",
                "version": "5.0",
                "generatingSystem": "Odoo 12"
            },
            nsmap = nsmap,
        )
        header = etree.SubElement(root, 'header')
        date = etree.SubElement(header, 'date')
        date.text = timestamp
        description = etree.SubElement(header, 'description')
        description.text = 'Rechnungen aus Odoo'
        consultantnumber = etree.SubElement(header, 'consultantNumber')
        consultantnumber.text = tax_accountant_id
        clientnumber = etree.SubElement(header, 'clientNumber')
        clientnumber.text = client_id
        content = etree.SubElement(root, 'content')
        for doc in docs:
            document = etree.SubElement(root, 'document')
            description = etree.SubElement(document, 'description')
            description.text = doc.inv_name
            extension = etree.SubElement(document, 'extension', {'{%s}type' % XSI: 'Invoice'}, nsmap={'xsi': XSI})
            extension.set('datafile', doc.xml_path)
            property = etree.SubElement(extension, 'property')
            property.set('key', doc.type)
            extension = etree.SubElement(document, 'extension', {'{%s}type' % XSI: 'File'}, nsmap={'xsi': XSI})
            extension.set('datafile', doc.pdf_path)
        xml_str = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='iso-8859-1').decode()
        print(xml_str)
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="ISO-8859-1")