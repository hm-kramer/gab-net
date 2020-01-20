

from lxml import etree

delivery_date, inv_number, inv_type, inv, booking_text = False, False, False, False, False

attr_qname = etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'schemaLocation')
nsmap = {
            None: 'http://xml.datev.de/bedi/tps/document/v05.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }

root = etree.Element(
    'invoice', 
    {
        attr_qname: 'http://xml.datev.de/bedi/tps/document/v05.0 document_v050.xsd',
        'version': '5.0',
        'generatingSystem': 'Odoo 12'
    },
    nsmap = nsmap,
)

root.set('generator_info', 'Odoo V12')
root.set('generating_system', 'Odoo-ERP Software')
root.set('description', 'DATEV XML Rechnungsexport')
root.set('version', '3.0')

invoice_info = etree.SubElement(root, 'invoice_info')
invoice_info.set('invoice_id', inv_number[0:12])
if delivery_date:
    invoice_info.set('delivery_date', delivery_date)
if inv_type:
    invoice_info.set('inv_type', inv_type)
if inv.date_invoice:
    invoice_info.set('inv_type', inv.date_invoice)

if booking_text:
    accounting_info = etree.SubElement(root, 'accounting_info')
    accounting_info.set('booking_text', booking_text)


print(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='iso-8859-1').decode())