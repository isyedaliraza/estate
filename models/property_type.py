from odoo import models, fields, api


class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'A real estate property type object'
    _sql_constraints = [
        ('name', 'unique (name)', 'Name already exists')
    ]
    _order = 'sequence, name'

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    sequence = fields.Integer('Sequence', default=1)
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    offer_count = fields.Integer(compute='_compute_offer_count', default=0)

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
