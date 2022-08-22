from odoo import fields, models, api


class DeliveryMan(models.Model):
    _name = 'delivery.man'
    _description = 'Delivery Man Model for personal delivery packages'

    name = fields.Char()
    phone = fields.Char()
    salary = fields.Float()

