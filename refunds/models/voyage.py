from odoo import fields, models, api, _
from odoo.exceptions import UserError


class Voyage(models.Model):
    _name = 'voyage.voyage'

    name = fields.Char(required=True, default=_('New'), readonly=True)
    delivery_id = fields.Many2one('delivery.man', string='Livreur')
    voyage_line_ids = fields.One2many('voyage.line', 'voyage_id')
    date = fields.Date(default=lambda self: fields.Date.context_today(self), required=True)
    destination = fields.Many2many('res.country.state')
    state = fields.Selection([
        ('draft', 'draft'),
        ('delivered', 'Delivered'),
        ('finished', 'Finished'),
    ])

    total_received = fields.Float('Total Received', compute="_compute_total_received")
    total_due = fields.Float('Total Due', compute="_compute_total_due")

    @api.onchange('voyage_line_ids')
    def _change_destination(self):
        lines = []
        if self.voyage_line_ids:
            customer_states = self.voyage_line_ids.mapped('order_id').mapped('customer_id').mapped('state_id')
            lines = customer_states.ids
        self.destination = [(6, 0, lines)]

    @api.depends("voyage_line_ids", 'voyage_line_ids.received_value')
    def _compute_total_received(self):
        for voyage in self:
            sum_line = 0
            for line in voyage.voyage_line_ids:
                sum_line += line.received_value
            voyage.total_received = sum_line

    @api.depends("voyage_line_ids")
    def _compute_total_due(self):
        for voyage in self:
            sum_line = 0
            for line in voyage.voyage_line_ids:
                sum_line += line.total
            voyage.total_due = sum_line

    @api.constrains('date')
    def _check_date(self):
        for voyage in self:
            if voyage.date:
                if voyage.date < fields.Date.context_today(self):
                    raise UserError('Not Allowed Date before today')

    @api.model
    def create(self, vals):
        # We generate a standard reference
        vals['name'] = self.env['ir.sequence'].next_by_code('voyage.sequence') or '/'
        return super(Voyage, self).create(vals)


class VoyageLine(models.Model):
    _name = 'voyage.line'

    order_id = fields.Many2one('package.order', required=True)
    voyage_id = fields.Many2one('voyage.voyage')
    address = fields.Text(related='order_id.address')
    total = fields.Float(related='order_id.value_due')
    received_value = fields.Float(string='Received Value', required=True)
