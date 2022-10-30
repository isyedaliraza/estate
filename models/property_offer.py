from datetime import datetime, timedelta
from odoo import models, fields, api, exceptions


def has_accepted_offer(self):
    for record in self.property_id.offer_ids:
        if record.status == 'accepted':
            return True
    return False


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'A real estate property offer object'
    _sql_constraints = [
        ('price', 'CHECK(price > 0)', 'Price must be positive')
    ]
    _order = 'price desc'

    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ]

    price = fields.Float()
    status = fields.Selection(selection=STATUS_CHOICES, copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True, ondelete='cascade')
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')
    property_type_id = fields.Many2one('estate.property.type', related='property_id.property_type_id',
                                       string='Property Type', store=True)

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date
            if not create_date:
                create_date = datetime.now()

            record.date_deadline = create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_date
            if not create_date:
                create_date = datetime.now()

            record.validity = (record.date_deadline - create_date.date()).days

    def accept_offer(self):
        if has_accepted_offer(self):
            raise exceptions.UserError('Already accepted an offer')
        for record in self:
            record.status = 'accepted'
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = 'offer_accepted'

        return True

    def refuse_offer(self):
        if has_accepted_offer(self):
            raise exceptions.UserError('Already accepted an offer')
        for record in self:
            record.status = 'refused'
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            offers_domain = [('property_id', '=', vals['property_id'])]
            offers = self.env['estate.property.offer'].search(offers_domain)

            prices = offers.mapped('price')
            max_price = 0
            if len(prices) > 0:
                max_price = max(prices)
            if vals['price'] <= max_price:
                msg = f"Offer can't be less than {max_price}"
                raise exceptions.UserError(msg)

            property_id = self.env['estate.property'].browse(vals['property_id'])
            property_id.state = 'offer_received'

        return super(PropertyOffer, self).create(vals_list)
