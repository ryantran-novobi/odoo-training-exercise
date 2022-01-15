from odoo import api, models, fields, _
from odoo.exceptions import UserError


class SalesRequest(models.Model):
    _name = 'sale.request'
    _order = 'date_request desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Sales Request"
    _check_company_auto = True

    name = fields.Char(string='Request Reference', required=True, index=True, states={
                       'draft': [('readonly', False)]}, default=lambda self: _('New'))
    date_request = fields.Datetime(
        string='Request Date', required=True, readonly=True, index=True, default=fields.Datetime.now)
    date_order = fields.Datetime(
        string='Order Date', readonly=True, index=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    sale_user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, default=lambda self: self.env.user,
        domain=lambda self: [('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)])
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True, required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=[
                                  "pricelist_id"], store=True, ondelete="restrict")
    partner_id = fields.Many2one(
        'res.partner', string='Retailer',
        required=True, change_default=True, index=True)
    request_state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Request Status', default='pending')
    fulfillment_state = fields.Selection([
        ('ready', 'Ready'),
        ('waiting', 'Waiting'),
        ('done', 'Done')
    ], string='Fulfillment Status', default='ready')
    tag_ids = fields.Many2many(
        'crm.tag', string='Tags')
    order_id = fields.Many2one('sale.order', string='Sale order')
    request_line = fields.One2many(
        'sale.request.line', 'request_id', string='Request Lines')
    amount_total = fields.Monetary(
        string='Total', store=True, compute='_compute_amount_total_item')
    amount_item = fields.Integer(
        string='Items', store=True, compute='_compute_amount_total_item')

    @api.depends('request_line', 'request_line.price_subtotal')
    def _compute_amount_total_item(self):
        """
        Compute the total amounts, items of the RS.
        """
        for request in self:
            amount_total = 0.0
            amount_item = 0
            for line in request.request_line:
                amount_total += line.price_subtotal
                amount_item += 1
            request.update({
                'amount_total': amount_total,
                'amount_item': amount_item
            })

    @api.onchange('request_state')
    def _onchange_order_date(self):
        self.ensure_one()
        if self.request_state == 'approved':
            self.update({
                'date_order': fields.Datetime.now
            })

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'pending'),
                   ('pending', 'approved'),
                   ('pending', 'rejected'),
                   ('pending', 'cancelled')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for record in self:
            if record.is_allowed_transition(record.request_state, new_state):
                record.request_state = new_state
            else:
                raise UserError(_('Change request state invalid'))

    def make_pending(self):
        self.change_state('pending')

    def make_approved(self):
        self.change_state('approved')
        self.create_sale_order()

    def make_rejected(self):
        self.change_state('rejected')

    def make_cancelled(self):
        self.change_state('cancelled')

    def create_sale_order(self):
        sale_request_lines = []
        for line in self.request_line:
            sale_request_lines.append({
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty
            })
        order_line = [(0, 0, x) for x in sale_request_lines]
        sale_order = {
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'order_line': order_line
        }
        record = self.env['sale.order'].create(sale_order)
        self.update({
            'order_id': record.id
        })

    def action_view_sale_order(self):
        order = self.mapped('order_id')
        action = self.env["ir.actions.actions"]._for_xml_id(
            "novobi_sales_b2b.open_order_view_form_action")
        form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + \
                [(state, view)
                    for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = order.id
        return action

    def multi_approve_sale_request(self):
        request_ids = self.env.context['active_ids']
        action = self.env["ir.actions.actions"]._for_xml_id(
            "novobi_sales_b2b.sale_request_approve_view_wizard_action")
        action.update({
            'context': {
                'request_ids': request_ids
            }
        })
        return action
