from odoo import models, fields


class Doctor(models.Model):
    _name = 'estate.doctor'
    _description = 'A real estate doctor object'
    _inherits = 'res.users'

    MY_GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    my_gender = fields.Selection(selection=MY_GENDER_CHOICES)

