# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models, api
from lxml import etree
import logging
import os


_logger = logging.getLogger(__name__)


class DATEVAExport(models.AbstractModel):
    _name = 'export.datev'
    _description = 'Datev XML-Export'

    @api.model
    def get_validated_xml(self, inv, vorlauf_id, export_mode, timestamp=False):
        errors = []
        vnote = ''
        if type(inv) is list:
            inv_id = inv[0][0].id
        else:
            inv_id = inv.id
        schema = etree.parse(
            os.path.join(os.path.dirname(__file__),
                         self._schema))
        
        schema = etree.XMLSchema(schema)
        parser = etree.XMLParser(schema=schema, encoding='utf-8')
        xml = self.get_pretty_xml(inv, timestamp, export_mode)
        try:
            etree.fromstring(xml, parser)
            return xml
        except Exception as e:
            errors.append(self.get_error_msg(inv))
            for arg in e.args:
                errors.append(arg)
            if vorlauf_id.note:
                vnote = vorlauf_id.note
                vnote += '\n'.join(errors)
                vnote += '\n'
            else:
                vnote = '\n'.join(errors)
                vnote += '\n'
            vorlauf_id.write({
                'note': vnote,
                'invoice_error_ids': [(4, inv_id)],
            })
            return

    @api.model
    def get_pretty_xml(self, *args):
        # must escape & gives issue when parsing
        xml = self.get_xml(*args)
        xml = xml.replace(u'&', ' ')
        try:
            parsed_xml = etree.fromstring(xml)
        except Exception as e:
            _logger.error(e.args)
            return
        return etree.tostring(parsed_xml, pretty_print=True, encoding='utf-8', xml_declaration=True)
