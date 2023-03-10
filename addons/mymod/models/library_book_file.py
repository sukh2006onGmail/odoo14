from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

class LibraryBook_class(models.Model):
    _name = 'library1.book1'
    _description = 'Library Book desc'
    _rec_name = 'short_name'

    name = fields.Char('Title1235555', required=True)
    ovog = fields.Char('ovog')
    date_release = fields.Date('Release Date')
    # short_name = fields.Char('Short Title', required=True)
    short_name = fields.Char('Short Title', translate=True, index=True)
    category_id = fields.Many2one('library.book.category')

    manager_remarks = fields.Text('Manager Remarks')

    # @api.model
    # def create(self, values):
    #     print('================================extend create======================================')
    #     print('values',values)
    #     print('group', self.user_has_groups('my_library.acl_book_librarian') )
    #     print('values', 'manager_remarks' in values)
    #     if not self.user_has_groups('my_library.acl_book_librarian'):  # lib group bish bol
    #         if 'manager_remarks' in values:
    #             raise UserError('You are not allowed to modify ' 'manager_remarks')
    #     return super(LibraryBook_class, self).create(values)


    publisher_id = fields.Many2one('res.partner', string='Publisher',
                                   # optional:
                                   ondelete='set null',
                                   context={},
                                   domain=[],
                                   )

    publisher_city = fields.Char('Publisher City', related='publisher_id.city', readonly=True)

    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,  # optional
        compute_sudo=True  # optional
    )

    def log_all_library_members(self):
        # This is an empty recordset of model library.member
        library_member_model = self.env['library1.book1']

        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members ) #, all_members)
        return True

    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model']   #.search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    @api.depends('date_release')
    def _compute_age(self):
        print("compute")
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    @api.depends('age_days')
    def _inverse_age(self):
        print("inverse")
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        print("search")
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)', 'No of pages must be positive')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        print('rec', self)
        for record in self:
            print('rec', record)
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError( 'Release date must be in the past')





















