from odoo import fields, models, api, _


class PackageOrder(models.Model):
    _name = 'package.order'
    _description = 'Description'

    name = fields.Char(default=_('New'), readonly=True, required=True)
    customer_id = fields.Many2one('res.partner', domain=[('is_company', '=', False)])
    address = fields.Text('Address', store=True)
    vendor_id = fields.Many2one('res.partner', domain=[('is_company', '=', True)])
    line_ids = fields.One2many('package.order.line', 'order_id', string='Lines')
    note = fields.Html()
    total = fields.Float('Total', compute="_compute_total")
    customer_commission = fields.Float("Customer Commission", compute="_compute_customer_commission")
    refund_amount = fields.Float('Refund Amount', compute="_compute_refund_amount")
    value_due = fields.Float("Value Due", compute="_compute_value_due")

    @api.onchange("customer_id")
    def _change_address(self):
        for order in self:
            if order.customer_id:
                order.address = f'{order.customer_id.street} ' if order.customer_id.street else ''
                order.address += f'or {order.customer_id.street2} ' if order.customer_id.street2 else ''
                order.address += f', {order.customer_id.city}' if order.customer_id.city else ''
                order.address += f' in {order.customer_id.state_id.name}' if order.customer_id.state_id else ''
            else:
                order.address = ''


    @api.depends('total')
    def _compute_value_due(self):
        for order in self:
            order.value_due = order.total + (order.total * (order.customer_id.commission / 100))

    @api.depends('line_ids', 'customer_id')
    def _compute_total(self):
        for order in self:
            sum_line = 0
            for line in order.line_ids:
                sum_line += line.sub_total
            order.total = sum_line

    @api.depends('total', 'customer_id')
    def _compute_refund_amount(self):
        for order in self:
            order.refund_amount = order.value_due - (order.total * (order.customer_id.commission / 100))

    @api.depends('customer_id', 'total')
    def _compute_customer_commission(self):
        for order in self:
            order.customer_commission = order.total * (order.customer_id.commission / 100)

    @api.model
    def create(self, vals):
        # We generate a standard reference
        vals['name'] = self.env['ir.sequence'].next_by_code('package.order') or '/'
        return super(PackageOrder, self).create(vals)


class PackageOrderLine(models.Model):
    _name = 'package.order.line'

    order_id = fields.Many2one('package.order')
    product_id = fields.Many2one('product.product')
    quantity = fields.Integer('quantity', default=1)
    price = fields.Float('Price', related='product_id.lst_price')
    sub_total = fields.Float('Sub Total', compute="_compute_total")

    @api.depends('product_id', 'quantity')
    def _compute_total(self):
        for line in self:
            line.sub_total = line.quantity * line.price
