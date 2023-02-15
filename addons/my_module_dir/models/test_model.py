from odoo import models, fields


class testModel_class(models.Model):
    _name = 'test.model'
    _description = 'Library Book desc'

    name = fields.Char('Title', required=True)
    ovog = fields.Char('ovog')
    date_release = fields.Date('Release Date')