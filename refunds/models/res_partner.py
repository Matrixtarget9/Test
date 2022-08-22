# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    commission = fields.Float('Commission', default=10)

