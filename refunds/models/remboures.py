from odoo.tools import float_compare
from odoo import fields, models, api, _


class Remboures(models.Model):
    _name = 'remboures.remboures'

    name = fields.Char(required=True, default=_("New"), readonly=True)

    voyage_id = fields.Many2one('voyage.voyage')

    client_id = fields.Many2one('res.partner', string='Clients')

    remboures_line_ids = fields.One2many('remboures.line', 'remboures_id')

    state = fields.Selection([
        ('remboursé', 'Remboursé'),
        ('prêt', 'Prêt'),
    ], default='remboursé')

    @api.onchange('voyage_id')
    def _change_voyage(self):
        customers = [line.order_id.customer_id.id
                     for line in self.voyage_id.voyage_line_ids] if self.voyage_id else []
        # if self.voyage_id:
        #
        #     for line in self.voyage_id.voyage_line_ids:
        #         customers.append(line.order_id.customer_id.id)

        return {
            'domain': {
                'client_id': [('id', 'in', customers)]
            }
        }

    @api.onchange('client_id')
    def _change_client(self):
        lines = [(5, 0, 0)]
        if self.client_id:
            client_orders = self.voyage_id.voyage_line_ids.filtered(
                lambda line: line.order_id.customer_id.id == self.client_id.id)
            for order in client_orders:
                vals = {
                    'remboures_id': self.id.origin,
                    'order_id': order.order_id.id,
                    'received_value': order.received_value
                }
                lines.append((0, 0, vals))
        self.remboures_line_ids = lines

    @api.onchange('client_id')
    def _change_state(self):
        check = all(float_compare(line.total,line.received_value, precision_digits=1)
                    for line in self.remboures_line_ids)
        if not check:
            self.state = 'prêt'
        else:
            self.state = 'remboursé'

    total_received = fields.Float('Total Received', compute="_compute_total_received")

    total_due = fields.Float('Total Due', compute="_compute_total_due")

    @api.depends("remboures_line_ids")
    def _compute_total_received(self):
        for remboures in self:
            sum_line = 0
            for line in remboures.remboures_line_ids:
                sum_line += line.received_value
            remboures.total_received = sum_line

    @api.depends("remboures_line_ids")
    def _compute_total_due(self):
        for remboures in self:
            sum_line = 0
            for line in remboures.remboures_line_ids:
                sum_line += line.total
            remboures.total_due = sum_line

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('remboursement.sequence') or '/'
        return super(Remboures, self).create(vals)


class RembouresLine(models.Model):
    _name = 'remboures.line'

    remboures_id = fields.Many2one('remboures.remboures')
    order_id = fields.Many2one('package.order')
    address = fields.Text(related='order_id.address')
    total = fields.Float(related='order_id.value_due')
    received_value = fields.Float(string='Received Value')
