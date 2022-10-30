from datetime import timedelta, datetime
from odoo import models, fields, api, exceptions


class Property(models.Model):
    _name = 'estate.property'
    _description = 'A Real Estate Property Object'
    _sql_constraints = [
        ('expected_price', 'CHECK(expected_price > 0)', 'Expected price must be positive'),
        ('selling_price', 'CHECK(selling_price > 0)', 'Selling price must be positive')
    ]
    _order = 'id desc'

    GARDEN_ORIENTATION_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ]

    STATE_CHOICES = [
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')
    ]

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False,
        default=lambda self: datetime.today() + timedelta(days=90)
    )
    expected_price = fields.Float(required=True, default=None)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=GARDEN_ORIENTATION_CHOICES)
    active = fields.Boolean(default=True)
    state = fields.Selection(selection=STATE_CHOICES, default='new')
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    salesman_id = fields.Many2one(
        'res.users',
        string='Salesman',
        default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    total_area = fields.Integer(compute='_compute_total_area')
    best_price = fields.Float(compute='_compute_best_price')

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped('price')
            if len(prices) == 0:
                record.best_price = 0
            else:
                record.best_price = max(prices)

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = None
            self.garden_orientation = None

    def sell_property(self):
        for record in self:
            if record.state == 'canceled':
                msg = 'Canceled property can not be sold'
                raise exceptions.UserError(msg)
            else:
                record.state = 'sold'
        return True

    def cancel_property(self):
        for record in self:
            if record.state == 'sold':
                msg = 'Sold property can not be canceled'
                raise exceptions.UserError(msg)
            else:
                record.state = 'canceled'
        return True

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_and_expected_price(self):
        for record in self:
            if record.selling_price == 0:
                return
            if record.selling_price < (record.expected_price * .9):
                msg = 'Selling price is very low'
                raise exceptions.ValidationError(msg)

    @api.ondelete(at_uninstall=False)
    def _unlink(self):
        for record in self:
            if record.state in ['offer_received', 'offer_accepted', 'sold']:
                raise exceptions.UserError("You can only delete a new or canceled property.")
