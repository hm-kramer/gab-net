# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _
from odoo.tools import ustr

from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_DOWN
import datetime
import logging

_logger = logging.getLogger(__name__)


class ecofi(models.Model):
    _inherit = 'ecofi'

    @api.multi
    def migrate_datev(self):
        _logger.info("Starting Move Migration")
        invoice_ids = self.env['account.invoice'].search()
        counter = 0
        for invoice in self.env['account.invoice'].browse(invoice_ids):
            counter += 1
            _logger.info(_("Migrate Move %s / %s") % (counter, len(invoice_ids)))
            if invoice.move_id:
                self.env['account.move'].write({
                    'ecofi_buchungstext': invoice.ecofi_buchungstext or False,
                })
                move = self.env['account.move'].browse(invoice.move_id.id)
                for invoice_line in invoice.invoice_line_ids:
                    if invoice_line.invoice_line_tax_ids:
                        for move_line in move.line_ids:
                            if move_line.account_id.id == invoice_line.account_id.id:
                                if move_line.debit + move_line.credit == abs(invoice_line.price_subtotal):
                                    self.env['account.move.line'].write({
                                        'ecofi_taxid': invoice_line.invoice_line_tax_ids[0].id
                                    })
        _logger.info(_("Move Migration Finished"))
        return True

    @api.multi
    def field_config(self, move, line, errorcount, partnererror, thislog, thismovename, faelligkeit, datevdict):
        """ Method that generates gets the values for the different Datev columns.
        :param move: account_move
        :param line: account_move_line
        :param errorcount: Errorcount
        :param partnererror: Partnererror
        :param thislog: Log
        :param thismovename: Movename
        :param faelligkeit: Fälligkeit
        """
        group = True
        belegdatum_format = self.env.user.company_id.voucher_date_format
        thisdate = move.date
        if belegdatum_format:
            datum = belegdatum_format.replace('dd', thisdate.strftime('%d'))
            datum = datum.replace('mm', thisdate.strftime('%m'))
            if 'jjjj' in belegdatum_format:
                datum = datum.replace('jjjj', thisdate.strftime('%Y'))
            else:
                datum = datum.replace('jj', thisdate.strftime('%y'))
            datevdict['Belegdatum'] = datum
        else:
            datevdict['Belegdatum'] = ('%s%s%s' % (thisdate[8:10], thisdate[5:7], thisdate[0:4]))
        if move.name:
            datevdict['Belegfeld 1'] = ustr(move.name)
        if move.journal_id.type == 'purchase' and move.ref:
            datevdict['Belegfeld 1'] = ustr(move.ref)
        if line.journal_id.type != 'sale' or line.journal_id.type != 'purchase':
            inv_num = False
            if line.full_reconcile_id:
                for lf in line.full_reconcile_id.reconciled_line_ids:
                    if lf.invoice_id:
                        if lf.invoice_id.number and lf.invoice_id.type in ['out_invoice', 'out_refund']:
                            inv_num = lf.invoice_id.number
                        if lf.invoice_id.reference and lf.invoice_id.type in ['in_invoice', 'in_refund']:
                            inv_num = lf.invoice_id.reference
                group = False
            if inv_num:
                datevdict['Belegfeld 1'] = inv_num
        if not datevdict['Belegfeld 1']:
            datevdict['Belegfeld 1'] = ustr(move.name)
        datevdict['Belegfeld 1'] = ''.join(e for e in datevdict['Belegfeld 1'] if e.isalnum())
        datevdict['Belegfeld 1'] = datevdict['Belegfeld 1'][-36:]
        if faelligkeit:
            datevdict['Belegfeld 2'] = faelligkeit
        datevdict['Kurs'] = self.format_waehrung(line)
        datevdict['Buchungstext'] = 'Buchungstext'
        line_name = ['Buchung']
        if line_name[0] == 'Buchung':
            line_name.append(str(line.name))
            if line.move_id.partner_id:
                line_name.append(str(line.move_id.partner_id.name))
            if len(line_name) > 1:
                line_name.remove('Buchung')
        if line_name:
            datevdict['Buchungstext'] = ', '.join(line_name)

        if line.account_id.ustuebergabe:
            if move.partner_id:
                if move.partner_id.vat:
                    datevdict['EulandUSTID'] = ustr(move.partner_id.vat)
                    if datevdict['EulandUSTID'] == '':
                        errorcount += 1
                        partnererror.append(move.partner_id.id)
                        thislog = thislog + thismovename + _(u'Error: No sales tax identification number stored in the partner!') + '\n'
        return errorcount, partnererror, thislog, thismovename, datevdict, group

    @api.multi
    def format_umsatz(self, lineumsatz):
        """ Returns the formatted amount
        :param lineumsatz: amountC
        :param context: context arguments, like lang, time zone
        :param lineumsatz:
        """
        Umsatz = ''
        Sollhaben = ''
        if lineumsatz < 0:
            Umsatz = str(lineumsatz * -1).replace('.', ',')
            Sollhaben = 'S'
        if lineumsatz > 0:
            Umsatz = str(lineumsatz).replace('.', ',')
            Sollhaben = 'H'
        if lineumsatz == 0:
            Umsatz = str(lineumsatz).replace('.', ',')
            Sollhaben = 'S'

        splitted = Umsatz.split(',')
        if len(splitted[1]) > 2:
            if splitted[1][2] == '5':
                Umsatz = Decimal(float(Umsatz.replace(',', '.'))) + Decimal(0.001)
                Umsatz = Umsatz.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            elif len(splitted[1]) > 3 and splitted[1][2] >= '4' and splitted[1][3] > '4':
                Umsatz = Decimal(float(Umsatz.replace(',', '.'))) + Decimal(0.002)
                Umsatz = Umsatz.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            else:
                Umsatz = Decimal(float(Umsatz.replace(',', '.'))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) 
        else:
            Umsatz = Decimal(float(Umsatz.replace(',', '.'))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        Umsatz = str(self.env.user.company_id.currency_id.round(float(Umsatz))).replace('.', ',')
        return Umsatz, Sollhaben

    @api.multi
    def format_waehrung(self, line):
        """ Formats the currency for the export
        :param line: account_move_line
        """
        if self.env.user:
            waehrung = self.env.user.company_id.currency_id.id
        else:
            thiscompany = self.env['res.company'].search([('parent_id', '=', False)])[0]
            thiscompany = self.env['res.company'].browse([thiscompany])[0]
            waehrung = thiscompany.currency_id.id
        if line.currency_id:
            waehrung = line.currency_id.id
        if waehrung:
            thisw = self.env['res.currency'].browse(waehrung)
            waehrung = thisw.name
            if waehrung != 'EUR' and line.amount_currency:
                faktor = ustr(line.currency_id.with_context(date=line.date).rate).replace('.', ',')
            else:
                faktor = ''
        return faktor

    @api.multi
    def generate_csv(self, ecofi_csv, bookingdict, log):
        """ Implements the generate_csv method for the datev interface
        """

        belegdatum_format = self.env.user.company_id.voucher_date_format
        year = belegdatum_format.find('jjjj')
        to_year = year + 4
        month = belegdatum_format.find('mm')
        to_month = month + 2
        day = belegdatum_format.find('dd')
        to_day = day + 2

        datum_arr = []

        for buchungssatz in bookingdict['buchungen']:
            datum_arr.append(buchungssatz[9])

        datum_von = str(min(datum_arr))
        datum_bis = str(max(datum_arr))

        current_date = datetime.datetime.now()
        current_date_string = current_date.isoformat()

        user = self.env.user
        berater_nr = user.company_id.tax_accountant_id
        mandanten_nr = user.company_id.client_id
        
        if user.company_id.enable_fixing:
            festschreibung = 1
        else:
            festschreibung = 0

        automatisierungs_header_dict = {
            'DATEVFormatKZ': 'EXTF',
            'Versionsnummer': 700,
            'Datenkategorie': 21,
            'Formatname': 'Buchungsstapel',
            'Formatversion': 9,
            'Erzeugtam': int('%s%s%s%s%s%s%s' % (
                current_date_string[0:4], current_date_string[5:7], current_date_string[8:10],
                current_date_string[11:13], current_date_string[14:16], current_date_string[17:19],
                current_date_string[20:23])),
            'Importiert': '',
            'Herkunft': 'OE',
            'Exportiertvon': self.env.user.partner_id.name,
            'Importiertvon': '',
            'Berater': int(berater_nr),
            'Mandant': int(mandanten_nr),
            'WJBeginn': int(str(datum_von[year:to_year]) + '0101'),
            'Sachkontenlaenge': self.env.user.company_id.account_code_digits,
            'Datumvon': int('%s%s%s' % (datum_von[year:to_year], datum_von[month:to_month], datum_von[day:to_day])),
            'Datumbis': int('%s%s%s' % (datum_bis[year:to_year], datum_bis[month:to_month], datum_bis[day:to_day])),
            'Bezeichnung': 'Odoo-Export',
            'Diktatkuerzel': '',
            'Buchungstyp': 1,
            'Rechnungslegungszweck': '',
            'Festschreibung': festschreibung,
            'WKZ': '',
            'res1': '',
            'Derivatskennzeichen': '',
            'res2': '',
            'res3': '',
            'SKR': '',
            'Branchenlösungs-Id': '',
            'res4': '',
            'res5': '',
            'Anwendungsinformationen': '',
        }

        ecofi_csv.writerow(self.buchungenAutomatisierungsHeaderDatev(automatisierungs_header_dict))

        if self._context['export_interface'] == 'datev':
            if self._context['export_interface'] == 'datev':
                ecofi_csv.writerow(bookingdict['buchungsheader'])
                for buchungsatz in bookingdict['buchungen']:
                    ecofi_csv.writerow(buchungsatz)
        (ecofi_csv, log) = super(ecofi, self).generate_csv(ecofi_csv, bookingdict, log)
        return ecofi_csv, log

    @api.multi
    def generate_csv_move_lines(self, move, buchungserror, errorcount, thislog, thismovename,
                                exportmethod, partnererror, buchungszeilencount, bookingdict):
        """ Implements the generate_csv_move_lines method for the datev interface
        """
        if self._context.get('export_interface', '') == 'datev':
            if 'buchungen' not in bookingdict:
                bookingdict['buchungen'] = []
            if 'buchungsheader' not in bookingdict:
                bookingdict['buchungsheader'] = self.buchungenHeaderDatev()
            user = self.env['res.users'].browse(self._uid)
            if user.company_id.enable_fixing == True:
                finance_secure = '1'
            else:
                finance_secure = '0'
            faelligkeit = False
            grouped_lines = []
            for line in move.line_ids:
                if line.debit == 0 and line.credit == 0:
                    continue
                datevkonto = move.ecofi_account_counterpart.code
                datevgegenkonto = ustr(line.account_id.code)
                if self.env.user.company_id.remove_leading_zeros:
                    if datevkonto[0] == '0':
                        datevkonto = datevkonto[1:]
                    if datevgegenkonto[0] == '0':
                        datevgegenkonto = datevgegenkonto[1:]
                if datevgegenkonto == datevkonto:
                    continue
                if line.date_maturity:
                    faelligkeit = line.date_maturity.strftime('%d%m%y')
                lineumsatz = Decimal(str(0))
                lineumsatz += Decimal(str(line.debit))
                lineumsatz -= Decimal(str(line.credit))
                self = self.with_context(waehrung = False)
                wkzumsatz = ''
                basisumsatz = ''
                wkzbasisumsatz = ''
                if line.currency_id and line.currency_id != user.company_id.currency_id and line.amount_currency != 0.0:
                    lineumsatz = Decimal(str(line.amount_currency))
                    self = self.with_context(waehrung = True)
                    wkzumsatz = line.currency_id.name
                    basisumsatz = ustr(Decimal(str(line.debit + line.credit)))
                    wkzbasisumsatz = 'EUR'
                buschluessel = ''
                if exportmethod == 'brutto':
                    if self.is_taxline(line.account_id.id) and not line.ecofi_bu == 'SD':
                        continue
                    if line.ecofi_bu and line.ecofi_bu == '40':
                        buschluessel = '40'
                    else:
                        taxamount = self.calculate_tax(line)
                        lineumsatz = lineumsatz + Decimal(str(taxamount))
                        linetax = self.get_line_tax(line)
                        if not line.account_id.automatic and linetax:
                            buschluessel = str(linetax.buchungsschluessel)  # pylint: disable-msg=E1103
                umsatz, sollhaben = self.format_umsatz(lineumsatz)
                
                datevline = {
                    'Umsatz (ohne Soll/Haben-Kz)': umsatz,
                    'Soll/Haben-Kennzeichen': sollhaben,
                    'WKZ Umsatz': wkzumsatz,
                    'Kurs': '',
                    'Basis-Umsatz': basisumsatz,
                    'WKZ Basis-Umsatz': wkzbasisumsatz,
                    'Konto': datevkonto or '',
                    'Gegenkonto (ohne BU-Schlüssel)': datevgegenkonto,
                    'BU-Schlüssel': buschluessel,
                    'Belegdatum': '',
                    'Belegfeld 1': '',
                    'Belegfeld 2': '',
                    'Skonto': '',
                    'Buchungstext': '',
                    'Postensperre': '',
                    'Diverse Adressnummer': '',
                    'Geschäftspartnerbank': '',
                    'Sachverhalt': '',
                    'Zinssperre': '',
                    'Beleglink': '',
                    'Beleginfo - Art 1': '',
                    'Beleginfo - Inhalt 1': '',
                    'Beleginfo - Art 2': '',
                    'Beleginfo - Inhalt 2': '',
                    'Beleginfo - Art 3': '',
                    'Beleginfo - Inhalt 3': '',
                    'Beleginfo - Art 4': '',
                    'Beleginfo - Inhalt 4': '',
                    'Beleginfo - Art 5': '',
                    'Beleginfo - Inhalt 5': '',
                    'Beleginfo - Art 6': '',
                    'Beleginfo - Inhalt 6': '',
                    'Beleginfo - Art 7': '',
                    'Beleginfo - Inhalt 7': '',
                    'Beleginfo - Art 8': '',
                    'Beleginfo - Inhalt 8': '',
                    'KOST1 - Kostenstelle': '',
                    'KOST2 - Kostenstelle': '',
                    'Kost-Menge': '',
                    'EU-Land u. UStID': '',
                    'EU-Steuersatz': '',
                    'Abw. Versteuerungsart': '',
                    'Sachverhalt L+L': '',
                    'Funktionsergänzung L+L': '',
                    'BU 49 Hauptfunktionstyp': '',
                    'BU 49 Hauptfunktionsnummer': '',
                    'BU 49 Funktionsergänzung': '',
                    'Zusatzinformation - Art 1': '',
                    'Zusatzinformation- Inhalt 1': '',
                    'Zusatzinformation - Art 2': '',
                    'Zusatzinformation- Inhalt 2': '',
                    'Zusatzinformation - Art 3': '',
                    'Zusatzinformation- Inhalt 3': '',
                    'Zusatzinformation - Art 4': '',
                    'Zusatzinformation- Inhalt 4': '',
                    'Zusatzinformation - Art 5': '',
                    'Zusatzinformation- Inhalt 5': '',
                    'Zusatzinformation - Art 6': '',
                    'Zusatzinformation- Inhalt 6': '',
                    'Zusatzinformation - Art 7': '',
                    'Zusatzinformation- Inhalt 7': '',
                    'Zusatzinformation - Art 8': '',
                    'Zusatzinformation- Inhalt 8': '',
                    'Zusatzinformation - Art 9': '',
                    'Zusatzinformation- Inhalt 9': '',
                    'Zusatzinformation - Art 10': '',
                    'Zusatzinformation- Inhalt 10': '',
                    'Zusatzinformation - Art 11': '',
                    'Zusatzinformation- Inhalt 11': '',
                    'Zusatzinformation - Art 12': '',
                    'Zusatzinformation- Inhalt 12': '',
                    'Zusatzinformation - Art 13': '',
                    'Zusatzinformation- Inhalt 13': '',
                    'Zusatzinformation - Art 14': '',
                    'Zusatzinformation- Inhalt 14': '',
                    'Zusatzinformation - Art 15': '',
                    'Zusatzinformation- Inhalt 15': '',
                    'Zusatzinformation - Art 16': '',
                    'Zusatzinformation- Inhalt 16': '',
                    'Zusatzinformation - Art 17': '',
                    'Zusatzinformation- Inhalt 17': '',
                    'Zusatzinformation - Art 18': '',
                    'Zusatzinformation- Inhalt 18': '',
                    'Zusatzinformation - Art 19': '',
                    'Zusatzinformation- Inhalt 19': '',
                    'Zusatzinformation - Art 20': '',
                    'Zusatzinformation- Inhalt 20': '',
                    'Stück': '',
                    'Gewicht': '',
                    'Zahlweise': '',
                    'Forderungsart': '',
                    'Veranlagungsjahr': '',
                    'Zugeordnete Fälligkeit': '',
                    'Skontotyp': '',
                    'Auftragsnummer': '',
                    'Buchungstyp': '',
                    'USt-Schlüssel (Anzahlungen)': '',
                    'EU-Land (Anzahlungen)': '',
                    'Sachverhalt L+L (Anzahlungen)': '',
                    'EU-Steuersatz (Anzahlungen)': '',
                    'Erlöskonto (Anzahlungen)': '',
                    'Herkunft-Kz': '',
                    'Buchungs GUID': '',
                    'KOST-Datum': '',
                    'SEPA-Mandatsreferenz': '',
                    'Skontosperre': '',
                    'Gesellschaftername': '',
                    'Beteiligtennummer': '',
                    'Identifikationsnummer': '',
                    'Zeichnernummer': '',
                    'Postensperre bis': '',
                    'Bezeichnung SoBil-Sachverhalt': '',
                    'Kennzeichen SoBil-Buchung': '',
                    'Festschreibung': finance_secure,
                    'Leistungsdatum': '',
                    'Datum Zuord. Steuerperiode': '',
                    'Fälligkeit': '',
                    'Generalumkehr (GU)': '',
                    'Steuersatz': '',
                    'Land': '',
                }
                (errorcount, partnererror, thislog, thismovename, datevdict, group) = \
                    self.field_config(move, line, errorcount, partnererror, thislog,
                    thismovename, faelligkeit, datevline)

                if group:
                    if not any(gl['Konto'] == datevkonto and gl['Gegenkonto (ohne BU-Schlüssel)'] == datevgegenkonto and gl['BU-Schlüssel'] == buschluessel
                        and gl['Soll/Haben-Kennzeichen'] == sollhaben and gl['WKZ Umsatz'] == wkzumsatz for gl in grouped_lines):
                        grouped_lines.append(datevline)
                    else:
                        for gl in grouped_lines:
                            if gl['Konto'] == datevkonto and gl['Gegenkonto (ohne BU-Schlüssel)'] == datevgegenkonto and gl['BU-Schlüssel'] == buschluessel and gl['Soll/Haben-Kennzeichen'] == sollhaben:
                                if gl['Basis-Umsatz'] and basisumsatz:
                                    gl['Basis-Umsatz'] = str(float(gl['Basis-Umsatz'].replace(',', '.')) + float(basisumsatz.replace(',', '.'))).replace('.', ',')
                                if gl['Umsatz (ohne Soll/Haben-Kz)'] and umsatz:
                                    gl['Umsatz (ohne Soll/Haben-Kz)'] = str(float(gl['Umsatz (ohne Soll/Haben-Kz)'].replace(',', '.')) + float(umsatz.replace(',', '.'))).replace('.', ',')
                                break
                else:
                    grouped_lines.append(datevline)

            for datevdict in grouped_lines:
                umsatz = datevdict['Umsatz (ohne Soll/Haben-Kz)'].replace(',', '.')
                umsatz_neu = Decimal(float(umsatz)).quantize(Decimal('.01'), rounding=ROUND_HALF_DOWN)
                datevdict['Umsatz (ohne Soll/Haben-Kz)'] = str(umsatz_neu).replace('.', ',')
                bookingdict['buchungen'].append(self.buchungenCreateDatev(datevdict))
                buchungszeilencount += 1

        buchungserror, errorcount, thislog, partnererror, buchungszeilencount, bookingdict = \
            super(ecofi, self).generate_csv_move_lines(move, buchungserror, errorcount, thislog, 
            thismovename, exportmethod, partnererror, buchungszeilencount, bookingdict)
        return buchungserror, errorcount, thislog, partnererror, buchungszeilencount, bookingdict

    def buchungenAutomatisierungsHeaderDatev(self, automatisierungs_header_dict):
        # erstellt den Automatisierungheader
        buchung = []

        buchung.append(automatisierungs_header_dict['DATEVFormatKZ'])
        buchung.append(automatisierungs_header_dict['Versionsnummer'])
        buchung.append(automatisierungs_header_dict['Datenkategorie'])
        buchung.append(automatisierungs_header_dict['Formatname'])
        buchung.append(automatisierungs_header_dict['Formatversion'])
        buchung.append(automatisierungs_header_dict['Erzeugtam'])
        buchung.append(automatisierungs_header_dict['Importiert'])
        buchung.append(automatisierungs_header_dict['Herkunft'])
        buchung.append(automatisierungs_header_dict['Exportiertvon'])
        buchung.append(automatisierungs_header_dict['Importiertvon'])
        buchung.append(automatisierungs_header_dict['Berater'])
        buchung.append(automatisierungs_header_dict['Mandant'])
        buchung.append(automatisierungs_header_dict['WJBeginn'])
        buchung.append(automatisierungs_header_dict['Sachkontenlaenge'])
        buchung.append(automatisierungs_header_dict['Datumvon'])
        buchung.append(automatisierungs_header_dict['Datumbis'])
        buchung.append(automatisierungs_header_dict['Bezeichnung'])
        buchung.append(automatisierungs_header_dict['Diktatkuerzel'])
        buchung.append(automatisierungs_header_dict['Buchungstyp'])
        buchung.append(automatisierungs_header_dict['Rechnungslegungszweck'])
        buchung.append(automatisierungs_header_dict['Festschreibung'])
        buchung.append(automatisierungs_header_dict['WKZ'])
        buchung.append(automatisierungs_header_dict['res1'])
        buchung.append(automatisierungs_header_dict['Derivatskennzeichen'])
        buchung.append(automatisierungs_header_dict['res2'])
        buchung.append(automatisierungs_header_dict['res3'])
        buchung.append(automatisierungs_header_dict['SKR'])
        buchung.append(automatisierungs_header_dict['Branchenlösungs-Id'])
        buchung.append(automatisierungs_header_dict['res4'])
        buchung.append(automatisierungs_header_dict['res5'])
        buchung.append(automatisierungs_header_dict['Anwendungsinformationen'])

        return buchung

    def buchungenHeaderDatev(self):
        """ Method that creates the Datev CSV header line
        """

        return [
            u'Umsatz (ohne Soll/Haben-Kz)',
            u'Soll/Haben-Kennzeichen',
            u'WKZ Umsatz',
            u'Kurs',
            u'Basis-Umsatz',
            u'WKZ Basis-Umsatz',
            u'Konto',
            u'Gegenkonto (ohne BU-Schlüssel)',
            u'BU-Schlüssel',
            u'Belegdatum',
            u'Belegfeld 1',
            u'Belegfeld 2',
            u'Skonto',
            u'Buchungstext',
            u'Postensperre',
            u'Diverse Adressnummer',
            u'Geschäftspartnerbank',
            u'Sachverhalt',
            u'Zinssperre',
            u'Beleglink',
            u'Beleginfo - Art 1',
            u'Beleginfo - Inhalt 1',
            u'Beleginfo - Art 2',
            u'Beleginfo - Inhalt 2',
            u'Beleginfo - Art 3',
            u'Beleginfo - Inhalt 3',
            u'Beleginfo - Art 4',
            u'Beleginfo - Inhalt 4',
            u'Beleginfo - Art 5',
            u'Beleginfo - Inhalt 5',
            u'Beleginfo - Art 6',
            u'Beleginfo - Inhalt 6',
            u'Beleginfo - Art 7',
            u'Beleginfo - Inhalt 7',
            u'Beleginfo - Art 8',
            u'Beleginfo - Inhalt 8',
            u'KOST1 - Kostenstelle',
            u'KOST2 - Kostenstelle',
            u'Kost-Menge',
            u'EU-Land u. UStID',
            u'EU-Steuersatz',
            u'Abw. Versteuerungsart',
            u'Sachverhalt L+L',
            u'Funktionsergänzung L+L',
            u'BU 49 Hauptfunktionstyp',
            u'BU 49 Hauptfunktionsnummer',
            u'BU 49 Funktionsergänzung',
            u'Zusatzinformation - Art 1',
            u'Zusatzinformation- Inhalt 1',
            u'Zusatzinformation - Art 2',
            u'Zusatzinformation- Inhalt 2',
            u'Zusatzinformation - Art 3',
            u'Zusatzinformation- Inhalt 3',
            u'Zusatzinformation - Art 4',
            u'Zusatzinformation- Inhalt 4',
            u'Zusatzinformation - Art 5',
            u'Zusatzinformation- Inhalt 5',
            u'Zusatzinformation - Art 6',
            u'Zusatzinformation- Inhalt 6',
            u'Zusatzinformation - Art 7',
            u'Zusatzinformation- Inhalt 7',
            u'Zusatzinformation - Art 8',
            u'Zusatzinformation- Inhalt 8',
            u'Zusatzinformation - Art 9',
            u'Zusatzinformation- Inhalt 9',
            u'Zusatzinformation - Art 10',
            u'Zusatzinformation- Inhalt 10',
            u'Zusatzinformation - Art 11',
            u'Zusatzinformation- Inhalt 11',
            u'Zusatzinformation - Art 12',
            u'Zusatzinformation- Inhalt 12',
            u'Zusatzinformation - Art 13',
            u'Zusatzinformation- Inhalt 13',
            u'Zusatzinformation - Art 14',
            u'Zusatzinformation- Inhalt 14',
            u'Zusatzinformation - Art 15',
            u'Zusatzinformation- Inhalt 15',
            u'Zusatzinformation - Art 16',
            u'Zusatzinformation- Inhalt 16',
            u'Zusatzinformation - Art 17',
            u'Zusatzinformation- Inhalt 17',
            u'Zusatzinformation - Art 18',
            u'Zusatzinformation- Inhalt 18',
            u'Zusatzinformation - Art 19',
            u'Zusatzinformation- Inhalt 19',
            u'Zusatzinformation - Art 20',
            u'Zusatzinformation- Inhalt 20',
            u'Stück',
            u'Gewicht',
            u'Zahlweise',
            u'Forderungsart',
            u'Veranlagungsjahr',
            u'Zugeordnete Fälligkeit',
            u'Skontotyp',
            u'Auftragsnummer',
            u'Buchungstyp',
            u'USt-Schlüssel (Anzahlungen)',
            u'EU-Land (Anzahlungen)',
            u'Sachverhalt L+L (Anzahlungen)',
            u'EU-Steuersatz (Anzahlungen)',
            u'Erlöskonto (Anzahlungen)',
            u'Herkunft-Kz',
            u'Buchungs GUID',
            u'KOST-Datum',
            u'SEPA-Mandatsreferenz',
            u'Skontosperre',
            u'Gesellschaftername',
            u'Beteiligtennummer',
            u'Identifikationsnummer',
            u'Zeichnernummer',
            u'Postensperre bis',
            u'Bezeichnung SoBil-Sachverhalt',
            u'Kennzeichen SoBil-Buchung',
            u'Festschreibung',
            u'Leistungsdatum',
            u'Datum Zuord. Steuerperiode',
            u'Fälligkeit',
            u'Generalumkehr (GU)',
            u'Steuersatz',
            u'Land',
        ]

    def buchungenCreateDatev(self, datevdict):
        """Method that creates the datev csv move line
        """
        if datevdict['BU-Schlüssel'] == '0':
            datevdict['BU-Schlüssel'] = ''
        
        if not datevdict['Buchungstext']:
            datevdict['Buchungstext'] = 'Buchungstext'

        return [
            datevdict['Umsatz (ohne Soll/Haben-Kz)'],
            datevdict['Soll/Haben-Kennzeichen'],
            datevdict['WKZ Umsatz'],
            datevdict['Kurs'],
            datevdict['Basis-Umsatz'],
            datevdict['WKZ Basis-Umsatz'],
            datevdict['Konto'],
            datevdict['Gegenkonto (ohne BU-Schlüssel)'],
            datevdict['BU-Schlüssel'],
            datevdict['Belegdatum'],
            datevdict['Belegfeld 1'],
            datevdict['Belegfeld 2'],
            datevdict['Skonto'],
            datevdict['Buchungstext'],
            datevdict['Postensperre'],
            datevdict['Diverse Adressnummer'],
            datevdict['Geschäftspartnerbank'],
            datevdict['Sachverhalt'],
            datevdict['Zinssperre'],
            datevdict['Beleglink'],
            datevdict['Beleginfo - Art 1'],
            datevdict['Beleginfo - Inhalt 1'],
            datevdict['Beleginfo - Art 2'],
            datevdict['Beleginfo - Inhalt 2'],
            datevdict['Beleginfo - Art 3'],
            datevdict['Beleginfo - Inhalt 3'],
            datevdict['Beleginfo - Art 4'],
            datevdict['Beleginfo - Inhalt 4'],
            datevdict['Beleginfo - Art 5'],
            datevdict['Beleginfo - Inhalt 5'],
            datevdict['Beleginfo - Art 6'],
            datevdict['Beleginfo - Inhalt 6'],
            datevdict['Beleginfo - Art 7'],
            datevdict['Beleginfo - Inhalt 7'],
            datevdict['Beleginfo - Art 8'],
            datevdict['Beleginfo - Inhalt 8'],
            datevdict['KOST1 - Kostenstelle'],
            datevdict['KOST2 - Kostenstelle'],
            datevdict['Kost-Menge'],
            datevdict['EU-Land u. UStID'],
            datevdict['EU-Steuersatz'],
            datevdict['Abw. Versteuerungsart'],
            datevdict['Sachverhalt L+L'],
            datevdict['Funktionsergänzung L+L'],
            datevdict['BU 49 Hauptfunktionstyp'],
            datevdict['BU 49 Hauptfunktionsnummer'],
            datevdict['BU 49 Funktionsergänzung'],
            datevdict['Zusatzinformation - Art 1'],
            datevdict['Zusatzinformation- Inhalt 1'],
            datevdict['Zusatzinformation - Art 2'],
            datevdict['Zusatzinformation- Inhalt 2'],
            datevdict['Zusatzinformation - Art 3'],
            datevdict['Zusatzinformation- Inhalt 3'],
            datevdict['Zusatzinformation - Art 4'],
            datevdict['Zusatzinformation- Inhalt 4'],
            datevdict['Zusatzinformation - Art 5'],
            datevdict['Zusatzinformation- Inhalt 5'],
            datevdict['Zusatzinformation - Art 6'],
            datevdict['Zusatzinformation- Inhalt 6'],
            datevdict['Zusatzinformation - Art 7'],
            datevdict['Zusatzinformation- Inhalt 7'],
            datevdict['Zusatzinformation - Art 8'],
            datevdict['Zusatzinformation- Inhalt 8'],
            datevdict['Zusatzinformation - Art 9'],
            datevdict['Zusatzinformation- Inhalt 9'],
            datevdict['Zusatzinformation - Art 10'],
            datevdict['Zusatzinformation- Inhalt 10'],
            datevdict['Zusatzinformation - Art 11'],
            datevdict['Zusatzinformation- Inhalt 11'],
            datevdict['Zusatzinformation - Art 12'],
            datevdict['Zusatzinformation- Inhalt 12'],
            datevdict['Zusatzinformation - Art 13'],
            datevdict['Zusatzinformation- Inhalt 13'],
            datevdict['Zusatzinformation - Art 14'],
            datevdict['Zusatzinformation- Inhalt 14'],
            datevdict['Zusatzinformation - Art 15'],
            datevdict['Zusatzinformation- Inhalt 15'],
            datevdict['Zusatzinformation - Art 16'],
            datevdict['Zusatzinformation- Inhalt 16'],
            datevdict['Zusatzinformation - Art 17'],
            datevdict['Zusatzinformation- Inhalt 17'],
            datevdict['Zusatzinformation - Art 18'],
            datevdict['Zusatzinformation- Inhalt 18'],
            datevdict['Zusatzinformation - Art 19'],
            datevdict['Zusatzinformation- Inhalt 19'],
            datevdict['Zusatzinformation - Art 20'],
            datevdict['Zusatzinformation- Inhalt 20'],
            datevdict['Stück'],
            datevdict['Gewicht'],
            datevdict['Zahlweise'],
            datevdict['Forderungsart'],
            datevdict['Veranlagungsjahr'],
            datevdict['Zugeordnete Fälligkeit'],
            datevdict['Skontotyp'],
            datevdict['Auftragsnummer'],
            datevdict['Buchungstyp'],
            datevdict['USt-Schlüssel (Anzahlungen)'],
            datevdict['EU-Land (Anzahlungen)'],
            datevdict['Sachverhalt L+L (Anzahlungen)'],
            datevdict['EU-Steuersatz (Anzahlungen)'],
            datevdict['Erlöskonto (Anzahlungen)'],
            datevdict['Herkunft-Kz'],
            datevdict['Buchungs GUID'],
            datevdict['KOST-Datum'],
            datevdict['SEPA-Mandatsreferenz'],
            datevdict['Skontosperre'],
            datevdict['Gesellschaftername'],
            datevdict['Beteiligtennummer'],
            datevdict['Identifikationsnummer'],
            datevdict['Zeichnernummer'],
            datevdict['Postensperre bis'],
            datevdict['Bezeichnung SoBil-Sachverhalt'],
            datevdict['Kennzeichen SoBil-Buchung'],
            datevdict['Festschreibung'],
            datevdict['Leistungsdatum'],
            datevdict['Datum Zuord. Steuerperiode'],
            datevdict['Fälligkeit'],
            datevdict['Generalumkehr (GU)'],
            datevdict['Steuersatz'],
            datevdict['Land'],
        ]
