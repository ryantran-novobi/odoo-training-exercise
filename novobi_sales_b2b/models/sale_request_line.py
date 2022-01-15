from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleRequestLine(models.Model):
    _name = 'sale.request.line'
    _description = 'Sales Request Line'
    _order = 'request_id desc, sequence, id desc'
    _check_company_auto = True

    request_id = fields.Many2one('sale.request', string='Request Reference',
                                 required=True, ondelete='cascade', index=True, copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Text(string='Description')
    product_id = fields.Many2one(
        'product.product', string='Product',
        change_default=True, ondelete='restrict')
    currency_id = fields.Many2one(related='request_id.currency_id', depends=[
                                  'request_id.currency_id'], store=True, string='Currency')
    company_id = fields.Many2one(
        related='request_id.company_id', string='Company', store=True, index=True)
    price_unit = fields.Float(
        'Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom_qty = fields.Float(
        string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    price_subtotal = fields.Monetary(
        compute='_compute_amount', string='Subtotal', store=True)

    @api.depends('product_uom_qty', 'price_unit', 'currency_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * line.product_uom_qty
            line.update({
                'price_subtotal': price
            })
