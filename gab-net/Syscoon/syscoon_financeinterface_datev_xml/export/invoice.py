# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import re
import os
from jinja2 import Environment, FileSystemLoader
from functools import wraps
from odoo import models, api, _
from odoo.exceptions import Warning
from collections import namedtuple
from decimal import Decimal, ROUND_HALF_DOWN, DecimalException
from functools import partial

jenv = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__))))


def iso_dtime_date(dtime):
    return dtime.split(' ')[0]


def flip(func):
    """
    :param func: function
    :returns: function that accepts positional
              arguments in reverse order

    Most usefull for cases when positional arguments
    are not in the needed order so that functools.partial
    can be used to "freeze" them.

    Example:

    is_int = partial(flip(isinstance), int)

    Can be used as a decorator aswell but doesn't
    really make sense :).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        args = tuple(reversed(args))
        return func(*args, **kwargs)
    return wrapper

DATEVInvLine = namedtuple('DATEVInvLine', [
    'order_unit', 'tax_amount', 'tax',
    'net_product_price', 'gross_product_price',
    'gross_price_line_amount', 'net_price_line_amount',
    'product_id', 'quantity', 'description_short',
    'account_no', 'bu_code', 'booking_text', 'cost_category_id', 'cost_category_id2'
])

DATEVInvLineAccountInfo = namedtuple('DATEVInvLineAccountInfo', [
    'account_no', 'cost_category_id', 'cost_amount',
    'booking_text',
])

DATEVTaxLine = namedtuple('DATEVTaxLine', [
    'currency', 'gross_price_line_amount', 'tax',
    'net_price_line_amount', 'tax_amount',
])

class DATEVInvoiceExport(models.AbstractModel):
    _name = 'export.datev.invoice'
    _inherit = 'export.datev'
    _schema = 'invoice.xsd'

    is_refund = False

    def get_inv_type(self, inv):
        if 'refund' in inv.type:
            return u'Gutschrift/Rechnungskorrektur', True
        return u'Rechnung', False

    def get_inv_delivery_date(self, inv):
        if inv.sale_ids:
            commitment_date = inv.sale_ids.commitment_date
            if commitment_date:
                return iso_dtime_date(commitment_date)
        return inv.date_invoice

    def get_inv_supplier(self, inv):
        supplier_name = False
        if inv.type in ('out_invoice', 'out_refund'):
            return inv.company_id.partner_id, False, inv.company_id.partner_id.name
        if inv.partner_id.parent_id:
            supplier_name = inv.partner_id.parent_id.name
        else:
            supplier_name = inv.partner_id.name
        return inv.partner_id, inv.account_id.code, supplier_name

    def get_inv_customer(self, inv):
        customer_name = False
        if inv.type in ('out_invoice', 'out_refund'):
            if inv.partner_id.parent_id:
                customer_name = inv.partner_id.parent_id.name
            else:
                customer_name = inv.partner_id.name
            return inv.partner_id, inv.account_id.code, customer_name
        return inv.company_id.partner_id, False, inv.company_id.partner_id.name

    def get_bank_acc(self, partner, inv):
        if partner.bank_ids and partner.bank_ids[0]:
            return partner.bank_ids and partner.bank_ids[0]
        else:
            return inv.company_id.partner_id.bank_ids and inv.company_id.partner_id.bank_ids[0]

    def make_DATEVInvLineAccInfo(self, inv):
        """
        Returns a function for matching an
        account analytic line (aal) with an invoice line (invl).

        Rationale: Odoo doesn't have a direct link
        between aal and invl. Only way to get to it is
        through the account move line (mvl) which also doesn't
        have a link to an invl. Odoo automatic invoice accounting
        creates a mvl for each invl though and copies some parameters
        (name, amount, etc). This function returns a function
        for matching an invl to a mvl by using some of these parameters.
        Implemented as a high order function for both encapsulation but also
        efficiency since the mvl recordset will be quieried for each invl and
        here we are converting it and storing it in the function's closure.
        """

        AccMvLine = namedtuple(
            'AccMvLine', ['name', 'credit', 'debit',
                          'analytic_lines'])

        def make_AccMvLine(mvl):
            return AccMvLine._make((mvl.name,
                                    mvl.credit, mvl.debit,
                                    mvl.analytic_line_ids))

        mv_lines = inv.move_id.mapped('line_ids').mapped(make_AccMvLine)

        def get_move_line_from_inv_line(invl):
            def invl_match_mvl(mvl):
                if (
                    invl.name == mvl.name and
                    invl.price_subtotal in (mvl.credit, mvl.debit)
                ):
                    return True
                return False

            mv_lines_filtered = filter(invl_match_mvl, mv_lines)

            if not mv_lines_filtered:
                raise Warning(_(
                    "Can't export %s ( id=%s ) because "
                    "invoice line %s ( id=%s ) can't be "
                    "matched to a move line"
                    % (inv.number, inv.id, invl.name, invl.id)
                ))
            elif len(mv_lines_filtered) > 1:
                raise Warning(_(
                    "Can't export %s ( id=%s ) because "
                    "invoice line %s ( id=%s ) matches to "
                    "multiple move lines %s"
                    % (inv.number, inv.id, invl.name,
                       invl.id, mv_lines_filtered)
                ))
            return mv_lines_filtered[0]

        def invl2aal(invl):
            def _make_DATEVInvLineAccInfo(aal):
                return DATEVInvLineAccountInfo._make((
                    invl.account_id.code, aal.account_id.code,
                    aal.amount, " ".join(filter(None, [aal.name, aal.ref]))
                ))

            analytic_lines = get_move_line_from_inv_line(invl).analytic_lines
            if analytic_lines:
                return analytic_lines.mapped(_make_DATEVInvLineAccInfo)
            # if no analytic lines write one line for the account
            return [DATEVInvLineAccountInfo._make(
                (invl.account_id.code, None, None, None))]

        return invl2aal

    def round2x(self, number):
        try:
            value = Decimal(number).quantize(Decimal('.01'), rounding=ROUND_HALF_DOWN)
        except:
            raise Warning(ValueError, DecimalException)
        return value

    def make_DATEVInvLine(self, l):
        def round2(number):
            return Decimal(number).quantize(Decimal('.01'), rounding=ROUND_HALF_DOWN)

        def round3(number):
            return Decimal(number).quantize(Decimal('.001'), rounding=ROUND_HALF_DOWN)

        tax_info = l.invoice_line_tax_ids.compute_all(
            (l.price_unit * (1 - (l.discount or 0.0) / 100.0)), l.currency_id,
            l.quantity, l.product_id, l.invoice_id.partner_id)

        if not l.quantity:
            quantity = 1.0
        else:
            quantity = l.quantity

        order_unit = l.uom_id.name
        product_id = l.product_id.default_code
        quantity = round2(quantity)
        description_short = re.sub(r'[^\w]', '', l.name)

        if self.refund:
            tax_amount = round2(sum(map(lambda x: -x['amount'], tax_info['taxes'])))
            tax = round2(-sum(l.invoice_line_tax_ids.mapped('amount')))
            net_product_price = round3(-l.price_unit)
            gross_product_price = round2(-tax_info['total_included'] / float(quantity))
            gross_price_line_amount = round2(-tax_info['total_included'])
            net_price_line_amount = round2(-tax_info['total_excluded'])
        else:
            tax_amount = round2(sum(map(lambda x: x['amount'], tax_info['taxes'])))
            tax = round2(sum(l.invoice_line_tax_ids.mapped('amount')))
            net_product_price = round3(l.price_unit)
            gross_product_price = round2(tax_info['total_included'] / float(quantity))
            gross_price_line_amount = round2(tax_info['total_included'])
            net_price_line_amount = round2(tax_info['total_excluded'])

        if self.env.user.company_id.remove_leading_zeros:
            if l.account_id.code and l.account_id.code[0] == '0':
                account_no = l.account_id.code[1:]
            else:
                account_no = l.account_id.code
        else:
            account_no = l.account_id.code
        if l.invoice_line_tax_ids:
            if l.invoice_line_tax_ids[0].buchungsschluessel != '0' and not l.account_id.automatic:
                bu_code = l.invoice_line_tax_ids[0].buchungsschluessel
            else:
                bu_code = False
        else:
            bu_code = False
        booking_text = l.account_id.name
        if l.account_analytic_id:
            cost_category_id = l.account_analytic_id.code
        else:
            cost_category_id = False
        if l.analytic_tag_ids:
            cost_category_id2 = l.analytic_tag_ids[0].name
        else:
            cost_category_id2 = False

        dil = DATEVInvLine._make((
            order_unit, tax_amount, tax, net_product_price,
            gross_product_price, gross_price_line_amount,
            net_price_line_amount, product_id, quantity,
            description_short, account_no, bu_code, booking_text,
            cost_category_id, cost_category_id2,
        ))

        return dil

    def make_DATEVTaxLine(self, tl):
        currency_id = tl.currency_id.name
        if not tl.tax_id.amount:
            tax = 0.00
            tax_amount = 0.00
            gross_price_line_amount = 0.00
            net_price_line_amount = 0.00
        else:
            if self.refund:
                tax = self.round2x(-tl.tax_id.amount)
                tax_amount = self.round2x(-tl.amount)
                net_amount = self.round2x(-tl.base)
                gross_price_line_amount = self.round2x(-net_amount + -tax_amount)
                net_price_line_amount = -net_amount
            else:
                tax = self.round2x(tl.tax_id.amount)
                tax_amount = self.round2x(tl.amount)
                net_amount = self.round2x(tl.base)
                gross_price_line_amount = self.round2x(net_amount + tax_amount)
                net_price_line_amount = net_amount

        dtl = DATEVTaxLine._make((
            currency_id, gross_price_line_amount, tax,
            net_price_line_amount, tax_amount,
        ))

        return dtl

    @api.model
    def get_error_msg(self, inv):
        return "%s (id=%s) could not be exported" % (inv.number, inv.id)

    @api.model
    def get_xml(self, inv, timestamp, export_mode):
        def is_tax_regular(l):
            return (l.amount_type == 'percent' and not l.price_include and
                    not l.include_base_amount)

        inv.ensure_one()
        if export_mode == 'extended':
            template = jenv.get_template('invoice_extended.xml')
        else:
            template = jenv.get_template('invoice_standard.xml')
        inv_customer, inv_customer_account, inv_customer_name = self.get_inv_customer(inv)
        inv_supplier, inv_supplier_account, inv_supplier_name = self.get_inv_supplier(inv)

        if inv_customer_account:
            bp_account_no = inv_customer_account
        if inv_supplier_account:
            bp_account_no = inv_supplier_account

        if inv.type in ['in_invoice', 'in_refund'] and inv.reference:
            inv_number = re.sub(r'[^\w]', '', inv.reference)
        else:
            inv_number = re.sub(r'[^\w]', '', inv.number)

        inv_type, self.refund = self.get_inv_type(inv)
        if self.refund:
            inv_amount_total = -self.round2x(inv.amount_total)
            inv_amount_net = -self.round2x(inv.amount_untaxed)
        else:
            inv_amount_total = self.round2x(inv.amount_total)
            inv_amount_net = self.round2x(inv.amount_untaxed)

        templ = template.render({
            'is_int': partial(flip(isinstance), int),
            'is_bool': partial(flip(isinstance), bool),
            'inv': inv,
            'inv_number': inv_number,
            'inv_type': self.get_inv_type(inv),
            'inv_type': inv_type,
            'inv_amount_total': inv_amount_total,
            'inv_amount_net': inv_amount_net,
            'inv_currency': inv.currency_id.name,
            'delivery_date': self.get_inv_delivery_date(inv),
            'supplier': inv_supplier,
            'supplier_name': inv_supplier_name,
            'customer': inv_customer,
            'customer_name': inv_customer_name,
            'cbank_acc': self.get_bank_acc(inv_customer, inv),
            'sbank_acc': self.get_bank_acc(inv_supplier, inv),
            'make_DATEVInvLine': self.make_DATEVInvLine,
            'make_DATEVInvLineAccInfo': self.make_DATEVInvLineAccInfo(inv),
            'make_DATEVTaxLine': self.make_DATEVTaxLine,
            'zip': zip,
            'bp_account_no': bp_account_no,
        })
        return templ
