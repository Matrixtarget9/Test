from odoo.tools import float_compare
from odoo import fields, models, api, _


class Caisse(models.Model):
    _name = 'caisse.caisse'

    name = fields.Char(required=True, default=_("New"), readonly=True)

    delivery_id = fields.Many2one('delivery.man')
    date = fields.Date(default=lambda self: fields.Date.context_today(self))

    caisse_line_ids = fields.One2many('caisse.line', 'caisse_id')

    @api.onchange('date', 'delivery_id')
    def _change_date(self):
        lines = [(5, 0, 0)]
        if self.date and self.delivery_id:
            voyage_lines = self.env['voyage.voyage'].search([
                ('date', '=', self.date), ('delivery_id', '=', self.delivery_id.id)
            ]).mapped('voyage_line_ids')
            for line in voyage_lines:
                lines.append((0, 0, {
                    'caisse_id': self.id,
                    'order_id': line.order_id.id,
                    'received_value': line.received_value
                }))

        self.caisse_line_ids = lines

    total_received = fields.Float('Total Received', compute="_compute_total_received")

    total_due = fields.Float('Total Due', compute="_compute_total_due")
    total_refund_amount = fields.Float('Total Refund', compute="_compute_refund_amount")
    total_customer_commission = fields.Float('Total Customer Commission', compute="_compute_customer_commission")

    @api.depends("caisse_line_ids")
    def _compute_total_received(self):
        for caisse in self:
            sum_line = 0
            for line in caisse.caisse_line_ids:
                sum_line += line.received_value
            caisse.total_received = sum_line

    @api.depends("caisse_line_ids")
    def _compute_total_due(self):
        for caisse in self:
            sum_line = 0
            for line in caisse.caisse_line_ids:
                sum_line += line.total
            caisse.total_due = sum_line

    @api.depends("caisse_line_ids")
    def _compute_refund_amount(self):
        for caisse in self:
            sum_line = 0
            for line in caisse.caisse_line_ids:
                sum_line += line.refund_amount
            caisse.total_refund_amount = sum_line

    @api.depends("caisse_line_ids")
    def _compute_customer_commission(self):
        for caisse in self:
            sum_line = 0
            for line in caisse.caisse_line_ids:
                sum_line += line.customer_commission
            caisse.total_customer_commission = sum_line

    @api.model
    def create(self, vals):
        # We generate a standard reference
        vals['name'] = self.env['ir.sequence'].next_by_code('caisse.sequence') or '/'
        return super(Caisse, self).create(vals)


class CaisseLine(models.Model):
    _name = 'caisse.line'

    caisse_id = fields.Many2one('caisse.caisse')
    order_id = fields.Many2one('package.order')
    address = fields.Text(related='order_id.address')
    total = fields.Float(related='order_id.value_due')
    refund_amount = fields.Float(related='order_id.refund_amount')
    customer_commission = fields.Float(related='order_id.customer_commission')
    received_value = fields.Float(string='Received Value', readonly=True)
