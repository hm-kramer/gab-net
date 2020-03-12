# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

from odoo import models, fields


class Invoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many(
        'sale.order', 'sale_order_invoice_rel', 'invoice_id', 'order_id',
        string='Sale Orders', readonly=True, copy=False,
        help="This is the list of sales orders associated with this invoice.")

