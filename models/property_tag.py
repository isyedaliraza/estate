from odoo import models, fields


class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'A real estate property tag object'
    _sql_constraints = [
        ('name', 'unique (name)', 'Name already exists')
    ]
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer('Color')
