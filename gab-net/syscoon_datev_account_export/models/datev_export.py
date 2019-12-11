# -*- coding: utf-8 -*-

##############################################################################
#
#    odoo (formerly known as OpenERP), Open Source Business Applications
#    Copyright (C) 2012-now Josef Kaser (<http://www.pragmasoft.de>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
import csv
import datetime
from io import StringIO

from odoo.tools import ustr
from odoo import fields, models


class DatevExport(models.TransientModel):
    _name = 'datev.export'
    _description = 'DATEV Account Export'

    name = fields.Char('File Name', readonly=True)
    data = fields.Binary('File', readonly=True)
    date = fields.Date('Export Date')
    state = fields.Selection([('choose', 'choose'), ('get', 'get')])
    filter = fields.Selection([('all', 'Alle'), ('new', 'Nur neue')], 'Welche wollen Sie exportieren?')
    kind = fields.Selection([('rewe', 'DATEV Kanzlei Rewe'), ('duo', 'DATEV Unternehmen Online')], required=True, string='Art')

    defaults = {
        'state': 'choose',
        'name': 'DTVF.csv',
        'filter': 'new'
    }

    def generate_header(self):
        """ Method that creates the Datev CSV Header
        """
        user = self.env.user
        berater_nr = user.company_id.tax_accountant_id
        mandanten_nr = user.company_id.client_id
        current_date = datetime.datetime.now()

        if self.date:
            fiscal_year = str(self.date)[0:4]
        else:
            fiscal_year = current_date.year

        buchung = []

        buchung.append(ustr("EXTF"))  # DATEVFormat-KZ
        buchung.append(ustr("700"))  # Versionsnummer
        buchung.append(ustr("16"))  # Datenkategorie
        buchung.append(ustr("Debitoren/Kreditoren"))  # Formatname
        buchung.append(ustr("5"))  # Formatversion
        now = datetime.datetime.now()
        buchung.append(ustr(now.strftime("%Y%m%d%H%M%S") + "000"))  # Erzeugt am
        buchung.append(ustr(""));  # Importiert
        buchung.append(ustr("OE"))  # Herkunft
        buchung.append(ustr(""))  # Exportiert von
        buchung.append(ustr(""))  # Importiert von
        buchung.append(ustr(berater_nr))  # Berater
        buchung.append(ustr(mandanten_nr))  # Mandant
        buchung.append(ustr(str(fiscal_year) + '0101'))  # WJ-Beginn
        buchung.append(ustr("4"))  # Sachkontenlänge
        # ab hier nur für Buchungstapel relevant. Gefüllt werden müssen sie aber immer.
        buchung.append(ustr(""))  # von
        buchung.append(ustr(""))  # bis
        buchung.append(ustr(""))  # Bezeichnung

        buchung.append(ustr(""))
        buchung.append(ustr(""))
        buchung.append(ustr(""))

        buchung.append(ustr(""))
        buchung.append(ustr(""))
        buchung.append(ustr(""))

        buchung.append(ustr(""))
        buchung.append(ustr(""))
        buchung.append(ustr(""))

        buchung.append(ustr(""))
        buchung.append(ustr(""))
        buchung.append(ustr(""))
        buchung.append(ustr(""))
        buchung.append(ustr(""))

        return buchung

    def stamm_header_datev(self):
        """ Method that creates the Datev CSV Headerline
        """
        line = []
        line.append(ustr("Konto"))
        line.append(ustr("Name (Adressattyp Unternehmen))"))
        line.append(ustr("Unternehmensgegenstand"))
        line.append(ustr("Name (Adressattyp natürl. Person))"))
        line.append(ustr("Vorname (Adressattyp natürl. Person))"))
        line.append(ustr("Name (Adressattyp keine Angabe))"))
        line.append(ustr("Adressattyp"))
        line.append(ustr("Kurzbezeichnung"))
        line.append(ustr("EU-Land"))
        line.append(ustr("EU-UStID"))
        line.append(ustr("Anrede"))
        line.append(ustr("Titel/Akad. Grad"))
        line.append(ustr("Adelstitel"))
        line.append(ustr("Namensvorsatz"))
        line.append(ustr("Adressart"))
        line.append(ustr("Straße"))
        line.append(ustr("Postfach"))
        line.append(ustr("Postleitzahl"))
        line.append(ustr("Ort"))
        line.append(ustr("Land"))
        line.append(ustr("Versandzusatz"))
        line.append(ustr("Adresszusatz"))
        line.append(ustr("Abweichende Anrede"))
        line.append(ustr("Abw. Zustellbezeichnung 1"))
        line.append(ustr("Abw. Zustellbezeichnung 2"))
        line.append(ustr("Kennz. Korrespondenzadresse"))
        line.append(ustr("Adresse Gültig von"))
        line.append(ustr("Adresse Gültig bis"))
        line.append(ustr("Telefon"))
        line.append(ustr("Bemerkung (Telefon))"))
        line.append(ustr("Telefon GL"))
        line.append(ustr("Bemerkung (Telefon GL))"))
        line.append(ustr("E-Mail"))
        line.append(ustr("Bemerkung (E-Mail))"))
        line.append(ustr("Internet"))
        line.append(ustr("Bemerkung (Internet))"))
        line.append(ustr("Fax"))
        line.append(ustr("Bemerkung (Fax))"))
        line.append(ustr("Sonstige"))
        line.append(ustr("Bemerkung (Sonstige))"))
        line.append(ustr("Bankleitzahl 1"))
        line.append(ustr("Bankbezeichnung 1"))
        line.append(ustr("Bank-Kontonummer 1"))
        line.append(ustr("Länderkennzeichen 1"))
        line.append(ustr("IBAN-Nr. 1"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 1"))
        line.append(ustr("Abw. Kontoinhaber 1"))
        line.append(ustr("Kennz. Hauptbankverb. 1"))
        line.append(ustr("Bankverb 1 Gültig von"))
        line.append(ustr("Bankverb 1 Gültig bis"))
        line.append(ustr("Bankleitzahl 2"))
        line.append(ustr("Bankbezeichnung 2"))
        line.append(ustr("Bank-Kontonummer 2"))
        line.append(ustr("Länderkennzeichen 2"))
        line.append(ustr("IBAN-Nr. 2"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 2"))
        line.append(ustr("Abw. Kontoinhaber 2"))
        line.append(ustr("Kennz. Hauptbankverb. 2"))
        line.append(ustr("Bankverb 2 Gültig von"))
        line.append(ustr("Bankverb 2 Gültig bis"))
        line.append(ustr("Bankleitzahl 3"))
        line.append(ustr("Bankbezeichnung 3"))
        line.append(ustr("Bank-Kontonummer 3"))
        line.append(ustr("Länderkennzeichen 3"))
        line.append(ustr("IBAN-Nr. 3"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 3"))
        line.append(ustr("Abw. Kontoinhaber 3"))
        line.append(ustr("Kennz. Hauptbankverb. 3"))
        line.append(ustr("Bankverb 3 Gültig von"))
        line.append(ustr("Bankverb 3 Gültig bis"))
        line.append(ustr("Bankleitzahl 4"))
        line.append(ustr("Bankbezeichnung 4"))
        line.append(ustr("Bank-Kontonummer 4"))
        line.append(ustr("Länderkennzeichen 4"))
        line.append(ustr("IBAN-Nr. 4"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 4"))
        line.append(ustr("Abw. Kontoinhaber 4"))
        line.append(ustr("Kennz. Hauptbankverb. 4"))
        line.append(ustr("Bankverb 4 Gültig von"))
        line.append(ustr("Bankverb 4 Gültig bis"))
        line.append(ustr("Bankleitzahl 5"))
        line.append(ustr("Bankbezeichnung 5"))
        line.append(ustr("Bank-Kontonummer 5"))
        line.append(ustr("Länderkennzeichen 5"))
        line.append(ustr("IBAN-Nr. 5"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 5"))
        line.append(ustr("Abw. Kontoinhaber 5"))
        line.append(ustr("Kennz. Hauptbankverb. 5"))
        line.append(ustr("Bankverb 5 Gültig von"))
        line.append(ustr("Bankverb 5 Gültig bis"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("Briefanrede"))
        line.append(ustr("Grußformel"))
        line.append(ustr("Kunden-/Lief.-Nr."))
        line.append(ustr("Steuernummer"))
        line.append(ustr("Sprache"))
        line.append(ustr("Ansprechpartner"))
        line.append(ustr("Vertreter"))
        line.append(ustr("Sachbearbeiter"))
        line.append(ustr("Diverse-Konto"))
        line.append(ustr("Ausgabeziel"))
        line.append(ustr("Währungssteuerung"))
        line.append(ustr("Kreditlimit (Debitor))"))
        line.append(ustr("Zahlungsbedingung"))
        line.append(ustr("Fälligkeit in Tagen (Debitor))"))
        line.append(ustr("Skonto in Prozent (Debitor))"))
        line.append(ustr("Kreditoren-Ziel 1 Tg."))
        line.append(ustr("Kreditoren-Skonto 1 %"))
        line.append(ustr("Kreditoren-Ziel 2 Tg."))
        line.append(ustr("Kreditoren-Skonto 2 %"))
        line.append(ustr("Kreditoren-Ziel 3 Brutto Tg."))
        line.append(ustr("Kreditoren-Ziel 4 Tg."))
        line.append(ustr("Kreditoren-Skonto 4 %"))
        line.append(ustr("Kreditoren-Ziel 5 Tg."))
        line.append(ustr("Kreditoren-Skonto 5 %"))
        line.append(ustr("Mahnung"))
        line.append(ustr("Kontoauszug"))
        line.append(ustr("Mahntext 1"))
        line.append(ustr("Mahntext 2"))
        line.append(ustr("Mahntext 3"))
        line.append(ustr("Kontoauszugstext"))
        line.append(ustr("Mahnlimit Betrag"))
        line.append(ustr("Mahnlimit %"))
        line.append(ustr("Zinsberechnung"))
        line.append(ustr("Mahnzinssatz 1"))
        line.append(ustr("Mahnzinssatz 2"))
        line.append(ustr("Mahnzinssatz 3"))
        line.append(ustr("Lastschrift"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("Mandantenbank"))
        line.append(ustr("Zahlungsträger"))
        line.append(ustr("Indiv. Feld 1"))
        line.append(ustr("Indiv. Feld 2"))
        line.append(ustr("Indiv. Feld 3"))
        line.append(ustr("Indiv. Feld 4"))
        line.append(ustr("Indiv. Feld 5"))
        line.append(ustr("Indiv. Feld 6"))
        line.append(ustr("Indiv. Feld 7"))
        line.append(ustr("Indiv. Feld 8"))
        line.append(ustr("Indiv. Feld 9"))
        line.append(ustr("Indiv. Feld 10"))
        line.append(ustr("Indiv. Feld 11"))
        line.append(ustr("Indiv. Feld 12"))
        line.append(ustr("Indiv. Feld 13"))
        line.append(ustr("Indiv. Feld 14"))
        line.append(ustr("Indiv. Feld 15"))
        line.append(ustr("Abweichende Anrede (Rechnungsadresse))"))
        line.append(ustr("Adressart (Rechnungsadresse))"))
        line.append(ustr("Straße (Rechnungsadresse))"))
        line.append(ustr("Postfach (Rechnungsadresse))"))
        line.append(ustr("Postleitzahl (Rechnungsadresse))"))
        line.append(ustr("Ort (Rechnungsadresse))"))
        line.append(ustr("Land (Rechnungsadresse))"))
        line.append(ustr("Versandzusatz (Rechnungsadresse))"))
        line.append(ustr("Adresszusatz (Rechnungsadresse))"))
        line.append(ustr("Abw. Zustellbezeichnung 1 (Rechnungsadresse))"))
        line.append(ustr("Abw. Zustellbezeichnung 2 (Rechnungsadresse))"))
        line.append(ustr("Adresse Gültig von (Rechnungsadresse))"))
        line.append(ustr("Adresse Gültig bis (Rechnungsadresse))"))
        line.append(ustr("Bankleitzahl 6"))
        line.append(ustr("Bankbezeichnung 6"))
        line.append(ustr("Bank-Kontonummer 6"))
        line.append(ustr("Länderkennzeichen 6"))
        line.append(ustr("IBAN-Nr. 6"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 6"))
        line.append(ustr("Abw. Kontoinhaber 6"))
        line.append(ustr("Kennz. Hauptbankverb. 6"))
        line.append(ustr("Bankverb 6 Gültig von"))
        line.append(ustr("Bankverb 6 Gültig bis"))
        line.append(ustr("Bankleitzahl 7"))
        line.append(ustr("Bankbezeichnung 7"))
        line.append(ustr("Bank-Kontonummer 7"))
        line.append(ustr("Länderkennzeichen 7"))
        line.append(ustr("IBAN-Nr. 7"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 7"))
        line.append(ustr("Abw. Kontoinhaber 7"))
        line.append(ustr("Kennz. Hauptbankverb. 7"))
        line.append(ustr("Bankverb 7 Gültig von"))
        line.append(ustr("Bankverb 7 Gültig bis"))
        line.append(ustr("Bankleitzahl 8"))
        line.append(ustr("Bankbezeichnung 8"))
        line.append(ustr("Bank-Kontonummer 8"))
        line.append(ustr("Länderkennzeichen 8"))
        line.append(ustr("IBAN-Nr. 8"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 8"))
        line.append(ustr("Abw. Kontoinhaber 8"))
        line.append(ustr("Kennz. Hauptbankverb. 8"))
        line.append(ustr("Bankverb 8 Gültig von"))
        line.append(ustr("Bankverb 8 Gültig bis"))
        line.append(ustr("Bankleitzahl 9"))
        line.append(ustr("Bankbezeichnung 9"))
        line.append(ustr("Bank-Kontonummer 9"))
        line.append(ustr("Länderkennzeichen 9"))
        line.append(ustr("IBAN-Nr. 9"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 9"))
        line.append(ustr("Abw. Kontoinhaber 9"))
        line.append(ustr("Kennz. Hauptbankverb. 9"))
        line.append(ustr("Bankverb 9 Gültig von"))
        line.append(ustr("Bankverb 9 Gültig bis"))
        line.append(ustr("Bankleitzahl 10"))
        line.append(ustr("Bankbezeichnung 10"))
        line.append(ustr("Bank-Kontonummer 10"))
        line.append(ustr("Länderkennzeichen 10"))
        line.append(ustr("IBAN-Nr. 10"))
        line.append(ustr("Leerfeld"))
        line.append(ustr("SWIFT-Code 10"))
        line.append(ustr("Abw. Kontoinhaber 10"))
        line.append(ustr("Kennz. Hauptbankverb. 10"))
        line.append(ustr("Bankverb 10 Gültig von"))
        line.append(ustr("Bankverb 10 Gültig bis"))
        line.append(ustr("Nummer Fremdsystem"))
        line.append(ustr("Insolvent"))
        line.append(ustr("SEPA-Mandatsreferenz 1"))
        line.append(ustr("SEPA-Mandatsreferenz 2"))
        line.append(ustr("SEPA-Mandatsreferenz 3"))
        line.append(ustr("SEPA-Mandatsreferenz 4"))
        line.append(ustr("SEPA-Mandatsreferenz 5"))
        line.append(ustr("SEPA-Mandatsreferenz 6"))
        line.append(ustr("SEPA-Mandatsreferenz 7"))
        line.append(ustr("SEPA-Mandatsreferenz 8"))
        line.append(ustr("SEPA-Mandatsreferenz 9"))
        line.append(ustr("SEPA-Mandatsreferenz 10"))
        line.append(ustr("Verknüpftes OPOS-Konto"))
        line.append(ustr("Mahnsperre bis"))
        line.append(ustr("Lastschriftsperre bis"))
        line.append(ustr("Zahlungssperre bis"))
        line.append(ustr("Gebührenberechnung"))
        line.append(ustr("Mahngebühr 1"))
        line.append(ustr("Mahngebühr 2"))
        line.append(ustr("Mahngebühr 3"))
        line.append(ustr("Pauschalenberechnung"))
        line.append(ustr("Verzugspauschale 1"))
        line.append(ustr("Verzugspauschale 2"))
        line.append(ustr("Verzugspauschale 3"))
        line.append(ustr("Alternativer Suchname"))
        line.append(ustr("Status"))
        line.append(ustr("Anschrift manuell geändert (Korrespondenzadresse))"))
        line.append(ustr("Anschrift individuell (Korrespondenzadresse))"))
        line.append(ustr("Anschrift manuell geändert (Rechnungsadresse))"))
        line.append(ustr("Anschrift individuell (Rechnungsadresse))"))
        line.append(ustr("Fristberechnung bei Debitor"))
        line.append(ustr("Mahnfrist 1"))
        line.append(ustr("Mahnfrist 2"))
        line.append(ustr("Mahnfrist 3"))
        line.append(ustr("Letzte Frist"))
        return line

    def duo_stamm_header_datev(self):
        """ Method that creates the Datev CSV Headerline
        """
        line = []
        line.append(ustr("Name"))
        line.append(ustr("Ort"))
        line.append(ustr("Kontonummer"))
        line.append(ustr("Kundennummer"))
        line.append(ustr("UStIdNr."))
        line.append(ustr("Bankkonto"))
        line.append(ustr("BLZ"))
        line.append(ustr("BankName"))
        line.append(ustr("Länderkennzeichen"))
        line.append(ustr("IBAN"))
        line.append(ustr("BIC"))
        line.append(ustr(" Anrede"))
        line.append(ustr("Adresszusatz"))
        line.append(ustr("Straße"))
        line.append(ustr("PLZ"))
        line.append(ustr("Steuernummer"))
        line.append(ustr("Ansprechpartner"))
        line.append(ustr("Telefonnummer"))
        line.append(ustr("E-Mail"))
        line.append(ustr("Faxnummer"))
        line.append(ustr("Internetadresse"))
        line.append(ustr("Land (2-stellig)"))
        line.append(ustr("UStEG-Land"))
        return line

    def get_users(self, this):
        partner_obj = self.env['res.partner']

        partners = None

        if this.filter == 'all':
            partners = partner_obj.search([('parent_id', '=', False), '|', ('customer_number', '!=', False), ('supplier_number', '!=', False)])
        elif this.filter == 'new':
            partners = partner_obj.search([('datev_exported', '=', False), ('parent_id', '=', False), '|', ('customer_number', '!=', False), ('supplier_number', '!=', False)])

        return partners

    def generate_person_lines(self, this, partner):
        lines = []
        account_ids = []

        if self.kind == 'rewe':
            if this.filter == 'all':
                if partner.customer:
                    if partner.property_account_receivable_id.user_type_id.type.lower() == 'receivable':
                        lines.append(self.generate_columns(partner, partner.property_account_receivable_id.code))
                        account_ids.append(partner.property_account_receivable_id.id)

                if partner.supplier:
                    if partner.property_account_payable_id.user_type_id.type.lower() == 'payable':
                        lines.append(self.generate_columns(partner, partner.property_account_payable_id.code))
                        account_ids.append(partner.property_account_payable_id.id)

            if this.filter == 'new':
                if partner.customer:
                    if partner.property_account_receivable_id.user_type_id.type.lower() == 'receivable' and not partner.property_account_receivable_id.datev_exported:
                        lines.append(self.generate_columns(partner, partner.property_account_receivable_id.code))
                        account_ids.append(partner.property_account_receivable_id.id)

                if partner.supplier:
                    if partner.property_account_payable_id.user_type_id.type.lower() == 'payable' and not partner.property_account_payable_id.datev_exported:
                        lines.append(self.generate_columns(partner, partner.property_account_payable_id.code))
                        account_ids.append(partner.property_account_payable_id.id)

        if self.kind == 'duo':
            if this.filter == 'all':
                if partner.customer:
                    if partner.property_account_receivable_id.user_type_id.type.lower() == 'receivable':
                        lines.append(self.duo_generate_columns(partner, partner.property_account_receivable_id.code))
                        account_ids.append(partner.property_account_receivable_id.id)

                if partner.supplier:
                    if partner.property_account_payable_id.user_type_id.type.lower() == 'payable':
                        lines.append(self.duo_generate_columns(partner, partner.property_account_payable_id.code))
                        account_ids.append(partner.property_account_payable_id.id)

            if this.filter == 'new':
                if partner.customer:
                    if partner.property_account_receivable_id.user_type_id.type.lower() == 'receivable' and not partner.property_account_receivable_id.datev_exported:
                        lines.append(self.duo_generate_columns(partner, partner.property_account_receivable_id.code))
                        account_ids.append(partner.property_account_receivable_id.id)

                if partner.supplier:
                    if partner.property_account_payable_id.user_type_id.type.lower() == 'payable' and not partner.property_account_payable_id.datev_exported:
                        lines.append(self.duo_generate_columns(partner, partner.property_account_payable_id.code))
                        account_ids.append(partner.property_account_payable_id.id)

        return lines, account_ids

    def generate_columns(self, partner, code):

        line = []

        line.append(ustr(code)) #Konto
        if partner.is_company:
            line.append(ustr(partner.name and partner.name or "")) #Name (Adressattyp Unternehmen)
        else:
            line.append(ustr("")) #Name (Adressattyp Unternehmen)
        line.append(ustr("")) #Unternehmensgegenstand
        if not partner.is_company:
            if hasattr(partner, 'lname') and hasattr(partner, 'fname') and partner.lname and partner.fname:
                line.append(ustr(partner.lname and partner.lname or "")) #Name (Adressattyp natürl. Person)
                line.append(ustr(partner.fname and partner.fname or "")) #Vorname (Adressattyp natürl. Person)
            else:
                line.append(ustr(partner.name and partner.name[0:30] or "")) #Name (Adressattyp natürl. Person)
                line.append(ustr("")) #Vorname (Adressattyp natürl. Person)
        else:
            line.append(ustr(""))
            line.append(ustr(""))

        line.append(ustr("")) #Name (Adressattyp keine Angabe)
        line.append(ustr("2" if partner.is_company else "1")) #Adressattyp
        line.append(ustr("")) #Kurzbezeichnung
        line.append(ustr(partner.vat[0:2] if partner.vat else '')) #EU-Land
        line.append(ustr(partner.vat if partner.vat else '')) #EU-UStID
        line.append(ustr(partner.title and partner.title.name or "")) #Anrede
        line.append(ustr("")) #Titel/Akad. Grad
        line.append(ustr("")) #Adelstitel
        line.append(ustr("")) #Namensvorsatz
        line.append(ustr("STR")) #Adressart
        line.append(ustr(partner.street and partner.street or "")) #Straße
        line.append(ustr("")) #Postfach
        line.append(ustr(partner.zip or "")) #Postleitzahl
        line.append(ustr(partner.city and partner.city or "")) #Ort
        line.append(ustr(partner.country_id and partner.country_id.code or "")) #Land
        line.append(ustr("")) #Versandzusatz
        line.append(ustr("")) #Adresszusatz
        line.append(ustr("")) #Abweichende Anrede
        line.append(ustr("")) #Abw. Zustellbezeichnung 1
        line.append(ustr("")) #Abw. Zustellbezeichnung 2
        line.append(ustr("")) #Kennz. Korrespondenzadresse
        line.append(ustr("")) #Adresse Gültig von
        line.append(ustr("")) #Adresse Gültig bis
        line.append(ustr("")) #Telefon
        line.append(ustr("")) #Bemerkung (Telefon)
        line.append(ustr("")) #Telefon GL
        line.append(ustr("")) #Bemerkung (Telefon GL)
        line.append(ustr("")) #E-Mail
        line.append(ustr("")) #Bemerkung (E-Mail)
        line.append(ustr("")) #Internet
        line.append(ustr("")) #Bemerkung (Internet)
        line.append(ustr("")) #Fax
        line.append(ustr("")) #Bemerkung (Fax)
        line.append(ustr("")) #Sonstige
        line.append(ustr("")) #Bemerkung (Sonstige)
        line.append(ustr("")) #Bankleitzahl 1
        line.append(ustr("")) #Bankbezeichnung 1
        line.append(ustr("")) #Bank-Kontonummer 1
        line.append(ustr("")) #Länderkennzeichen 1
        if partner.bank_ids:
            line.append(ustr(partner.bank_ids[0].acc_number)) #IBAN-Nr. 1
            line.append(ustr("")) #Leerfeld
            line.append(ustr(partner.bank_ids[0].bank_bic)) #SWIFT-Code 1
        else: 
            line.append(ustr("")) #IBAN-Nr. 1
            line.append(ustr("")) #Leerfeld
            line.append(ustr("")) #SWIFT-Code 1
        line.append(ustr("")) #Abw. Kontoinhaber 1
        line.append(ustr("")) #Kennz. Hauptbankverb. 1
        line.append(ustr("")) #Bankverb 1 Gültig von
        line.append(ustr("")) #Bankverb 1 Gültig bis
        line.append(ustr("")) #Bankleitzahl 2
        line.append(ustr("")) #Bankbezeichnung 2
        line.append(ustr("")) #Bank-Kontonummer 2
        line.append(ustr("")) #Länderkennzeichen 2
        line.append(ustr("")) #IBAN-Nr. 2
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #SWIFT-Code 2
        line.append(ustr("")) #Abw. Kontoinhaber 2
        line.append(ustr("")) #Kennz. Hauptbankverb. 2
        line.append(ustr("")) #Bankverb 2 Gültig von
        line.append(ustr("")) #Bankverb 2 Gültig bis
        line.append(ustr("")) #Bankleitzahl 3
        line.append(ustr("")) #Bankbezeichnung 3
        line.append(ustr("")) #Bank-Kontonummer 3
        line.append(ustr("")) #Länderkennzeichen 3
        line.append(ustr("")) #IBAN-Nr. 3
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #SWIFT-Code 3
        line.append(ustr("")) #Abw. Kontoinhaber 3
        line.append(ustr("")) #Kennz. Hauptbankverb. 3
        line.append(ustr("")) #Bankverb 3 Gültig von
        line.append(ustr("")) #Bankverb 3 Gültig bis
        line.append(ustr("")) #Bankleitzahl 4
        line.append(ustr("")) #Bankbezeichnung 4
        line.append(ustr("")) #Bank-Kontonummer 4
        line.append(ustr("")) #Länderkennzeichen 4
        line.append(ustr("")) #IBAN-Nr. 4
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #SWIFT-Code 4
        line.append(ustr("")) #Abw. Kontoinhaber 4
        line.append(ustr("")) #Kennz. Hauptbankverb. 4
        line.append(ustr("")) #Bankverb 4 Gültig von
        line.append(ustr("")) #Bankverb 4 Gültig bis
        line.append(ustr("")) #Bankleitzahl 5
        line.append(ustr("")) #Bankbezeichnung 5
        line.append(ustr("")) #Bank-Kontonummer 5
        line.append(ustr("")) #Länderkennzeichen 5
        line.append(ustr("")) #IBAN-Nr. 5
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #SWIFT-Code 5
        line.append(ustr("")) #Abw. Kontoinhaber 5
        line.append(ustr("")) #Kennz. Hauptbankverb. 5
        line.append(ustr("")) #Bankverb 5 Gültig von
        line.append(ustr("")) #Bankverb 5 Gültig bis
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #Briefanrede
        line.append(ustr("")) #Grußformel
        line.append(ustr("")) #Kunden-/Lief.-Nr.
        line.append(ustr("")) #Steuernummer
        line.append(ustr("")) #Sprache
        line.append(ustr("")) #Ansprechpartner
        line.append(ustr("")) #Vertreter
        line.append(ustr("")) #Sachbearbeiter
        line.append(ustr("")) #Diverse-Konto
        line.append(ustr("")) #Ausgabeziel
        line.append(ustr("")) #Währungssteuerung
        line.append(ustr("")) #Kreditlimit (Debitor)
        line.append(ustr("")) #Zahlungsbedingung
        line.append(ustr("")) #Fälligkeit in Tagen (Debitor)
        line.append(ustr("")) #Skonto in Prozent (Debitor)
        line.append(ustr("")) #Kreditoren-Ziel 1 Tg.
        line.append(ustr("")) #Kreditoren-Skonto 1 %
        line.append(ustr("")) #Kreditoren-Ziel 2 Tg.
        line.append(ustr("")) #Kreditoren-Skonto 2 %
        line.append(ustr("")) #Kreditoren-Ziel 3 Brutto Tg.
        line.append(ustr("")) #Kreditoren-Ziel 4 Tg.
        line.append(ustr("")) #Kreditoren-Skonto 4 %
        line.append(ustr("")) #Kreditoren-Ziel 5 Tg.
        line.append(ustr("")) #Kreditoren-Skonto 5 %
        line.append(ustr("")) #Mahnung
        line.append(ustr("")) #Kontoauszug
        line.append(ustr("")) #Mahntext 1
        line.append(ustr("")) #Mahntext 2
        line.append(ustr("")) #Mahntext 3
        line.append(ustr("")) #Kontoauszugstext
        line.append(ustr("")) #Mahnlimit Betrag
        line.append(ustr("")) #Mahnlimit %
        line.append(ustr("")) #Zinsberechnung
        line.append(ustr("")) #Mahnzinssatz 1
        line.append(ustr("")) #Mahnzinssatz 2
        line.append(ustr("")) #Mahnzinssatz 3
        line.append(ustr("")) #Lastschrift
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #Mandantenbank
        line.append(ustr("")) #Zahlungsträger
        line.append(ustr("")) #Indiv. Feld 1
        line.append(ustr("")) #Indiv. Feld 2
        line.append(ustr("")) #Indiv. Feld 3
        line.append(ustr("")) #Indiv. Feld 4
        line.append(ustr("")) #Indiv. Feld 5
        line.append(ustr("")) #Indiv. Feld 6
        line.append(ustr("")) #Indiv. Feld 7
        line.append(ustr("")) #Indiv. Feld 8
        line.append(ustr("")) #Indiv. Feld 9
        line.append(ustr("")) #Indiv. Feld 10
        line.append(ustr("")) #Indiv. Feld 11
        line.append(ustr("")) #Indiv. Feld 12
        line.append(ustr("")) #Indiv. Feld 13
        line.append(ustr("")) #Indiv. Feld 14
        line.append(ustr("")) #Indiv. Feld 15
        line.append(ustr("")) #Abweichende Anrede (Rechnungsadresse)
        line.append(ustr("")) #Adressart (Rechnungsadresse)
        line.append(ustr("")) #Straße (Rechnungsadresse)
        line.append(ustr("")) #Postfach (Rechnungsadresse)
        line.append(ustr("")) #Postleitzahl (Rechnungsadresse)
        line.append(ustr("")) #Ort (Rechnungsadresse)
        line.append(ustr("")) #Land (Rechnungsadresse)
        line.append(ustr("")) #Versandzusatz (Rechnungsadresse)
        line.append(ustr("")) #Adresszusatz (Rechnungsadresse)
        line.append(ustr("")) #Abw. Zustellbezeichnung 1 (Rechnungsadresse)
        line.append(ustr("")) #Abw. Zustellbezeichnung 2 (Rechnungsadresse)
        line.append(ustr("")) #Adresse Gültig von (Rechnungsadresse)
        line.append(ustr("")) #Adresse Gültig bis (Rechnungsadresse)
        line.append(ustr("")) #Bankleitzahl 6
        line.append(ustr("")) #Bankbezeichnung 6
        line.append(ustr("")) #Bank-Kontonummer 6
        line.append(ustr("")) #Länderkennzeichen 6
        line.append(ustr("")) #IBAN-Nr. 6
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #SWIFT-Code 6
        line.append(ustr("")) #Abw. Kontoinhaber 6
        line.append(ustr("")) #Kennz. Hauptbankverb. 6
        line.append(ustr("")) #Bankverb 6 Gültig von
        line.append(ustr("")) #Bankverb 6 Gültig bis
        line.append(ustr("")) #Bankleitzahl 7
        line.append(ustr("")) #Bankbezeichnung 7
        line.append(ustr("")) #Bank-Kontonummer 7
        line.append(ustr("")) #Länderkennzeichen 7
        line.append(ustr("")) #IBAN-Nr. 7
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #SWIFT-Code 7
        line.append(ustr("")) #Abw. Kontoinhaber 7
        line.append(ustr("")) #Kennz. Hauptbankverb. 7
        line.append(ustr("")) #Bankverb 7 Gültig von
        line.append(ustr("")) #Bankverb 7 Gültig bis
        line.append(ustr("")) #Bankleitzahl 8
        line.append(ustr("")) #Bankbezeichnung 8
        line.append(ustr("")) #Bank-Kontonummer 8
        line.append(ustr("")) #Länderkennzeichen 8
        line.append(ustr("")) #IBAN-Nr. 8
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #SWIFT-Code 8
        line.append(ustr("")) #Abw. Kontoinhaber 8
        line.append(ustr("")) #Kennz. Hauptbankverb. 8
        line.append(ustr("")) #Bankverb 8 Gültig von
        line.append(ustr("")) #Bankverb 8 Gültig bis
        line.append(ustr("")) #Bankleitzahl 9
        line.append(ustr("")) #Bankbezeichnung 9
        line.append(ustr("")) #Bank-Kontonummer 9
        line.append(ustr("")) #Länderkennzeichen 9
        line.append(ustr("")) #IBAN-Nr. 9
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #SWIFT-Code 9
        line.append(ustr("")) #Abw. Kontoinhaber 9
        line.append(ustr("")) #Kennz. Hauptbankverb. 9
        line.append(ustr("")) #Bankverb 9 Gültig von
        line.append(ustr("")) #Bankverb 9 Gültig bis
        line.append(ustr("")) #Bankleitzahl 10
        line.append(ustr("")) #Bankbezeichnung 10
        line.append(ustr("")) #Bank-Kontonummer 10
        line.append(ustr("")) #Länderkennzeichen 10
        line.append(ustr("")) #IBAN-Nr. 10
        line.append(ustr("")) #Leerfeld
        line.append(ustr("")) #SWIFT-Code 10
        line.append(ustr("")) #Abw. Kontoinhaber 10
        line.append(ustr("")) #Kennz. Hauptbankverb. 10
        line.append(ustr("")) #Bankverb 10 Gültig von
        line.append(ustr("")) #Bankverb 10 Gültig bis
        line.append(ustr("")) #Nummer Fremdsystem
        line.append(ustr("")) #Insolvent
        line.append(ustr("")) #SEPA-Mandatsreferenz 1
        line.append(ustr("")) #SEPA-Mandatsreferenz 2
        line.append(ustr("")) #SEPA-Mandatsreferenz 3
        line.append(ustr("")) #SEPA-Mandatsreferenz 4
        line.append(ustr("")) #SEPA-Mandatsreferenz 5
        line.append(ustr("")) #SEPA-Mandatsreferenz 6
        line.append(ustr("")) #SEPA-Mandatsreferenz 7
        line.append(ustr("")) #SEPA-Mandatsreferenz 8
        line.append(ustr("")) #SEPA-Mandatsreferenz 9
        line.append(ustr("")) #SEPA-Mandatsreferenz 10
        line.append(ustr("")) #Verknüpftes OPOS-Konto
        line.append(ustr("")) #Mahnsperre bis
        line.append(ustr("")) #Lastschriftsperre bis
        line.append(ustr("")) #Zahlungssperre bis
        line.append(ustr("")) #Gebührenberechnung
        line.append(ustr("")) #Mahngebühr 1
        line.append(ustr("")) #Mahngebühr 2
        line.append(ustr("")) #Mahngebühr 3
        line.append(ustr("")) #Pauschalenberechnung
        line.append(ustr("")) #Verzugspauschale 1
        line.append(ustr("")) #Verzugspauschale 2
        line.append(ustr("")) #Verzugspauschale 3
        line.append(ustr("")) #Alternativer Suchname
        line.append(ustr("")) #Status
        line.append(ustr("")) #Anschrift manuell geändert (Korrespondenzadresse)
        line.append(ustr("")) #Anschrift individuell (Korrespondenzadresse)
        line.append(ustr("")) #Anschrift manuell geändert (Rechnungsadresse)
        line.append(ustr("")) #Anschrift individuell (Rechnungsadresse)
        line.append(ustr("")) #Fristberechnung bei Debitor
        line.append(ustr("")) #Mahnfrist 1
        line.append(ustr("")) #Mahnfrist 2
        line.append(ustr("")) #Mahnfrist 3
        line.append(ustr("")) #Letzte Frist

        return line


    def duo_generate_columns(self, partner, code):
        line = []
        line.append(ustr(partner.name or '')) #Name
        line.append(ustr(partner.city or '')) #Ort
        line.append(ustr(code or '')) #Kontonummer
        line.append(ustr(partner.ref or '')) #Kundennummer
        line.append(ustr(partner.vat and partner.vat[2:] or '')) #UStIdNr.
        line.append(ustr('')) #Bankkonto
        line.append(ustr('')) #BLZ
        line.append(ustr(partner.bank_ids and partner.bank_ids[0].bank_id.name or '')) #BankName
        line.append(ustr('')) #Länderkennzeichen
        line.append(ustr(partner.bank_ids and partner.bank_ids[0].sanitized_acc_number or '')) #IBAN
        line.append(ustr(partner.bank_ids and partner.bank_ids[0].bank_bic or '')) #BIC
        line.append(ustr('')) #Anrede
        line.append(ustr(partner.street2 or '')) #Adresszusatz
        line.append(ustr(partner.street or '')) #Straße"
        line.append(ustr(partner.zip or '')) #PLZ
        line.append(ustr('')) #Steuernummer
        line.append(ustr('')) #Ansprechpartner
        line.append(ustr(partner.phone or '')) #Telefonnummer
        line.append(ustr(partner.email or '')) #E-Mail
        line.append(ustr('')) #Faxnummer
        line.append(ustr(partner.website or '')) #Internetadresse
        line.append(ustr(partner.country_id and partner.country_id.code or '')) #Land (2-stellig)
        line.append(ustr(partner.vat and partner.vat[0:2] or '')) #UStEG-Land
        
        return line

    def generate_csv(self, this):
        partners = self.get_users(this)
        has_data = False
        account_ids = []

        buf = StringIO()
        csvwriter = csv.writer(buf, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

        if self.kind == 'rewe':
            csvwriter.writerow(self.generate_header())
            csvwriter.writerow(self.stamm_header_datev())

            for partner in partners:
                lines, temp_account_ids = self.generate_person_lines(this, partner)

                account_ids.extend(temp_account_ids)

                for line in lines:
                    csvwriter.writerow(line)
                    has_data = True

        if self.kind == 'duo':
            csvwriter.writerow(self.duo_stamm_header_datev())

            for partner in partners:
                lines, temp_account_ids = self.generate_person_lines(this, partner)

                account_ids.extend(temp_account_ids)

                for line in lines:
                    csvwriter.writerow(line)
                    has_data = True

        if not has_data:
            return False

        out = base64.b64encode(buf.getvalue().encode('iso-8859-1', 'ignore'))

        self.env['account.account'].search([('id', 'in', account_ids)]).write({'datev_exported': True})
        # partners.write({'datev_exported': True})

        return out

    def act_getfile(self):
        this = self
        out = self.generate_csv(this)
        now = datetime.datetime.now()
        filename = "DTVF_" + ustr(now.strftime("%Y%m%d%H%M%S")) + ".csv"

        self.update(
            {
                'state': 'get',
                'data': out,
                'name': filename
            }
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'datev.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
