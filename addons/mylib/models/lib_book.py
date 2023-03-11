from odoo import models, fields, api
from datetime import timedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'
    published_book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')
    authored_book_ids = fields.Many2many('library.book', string='Authored Books',
        # relation='library_book_res_partner_rel' #optional
    )
    count_books = fields.Integer('Number of Authored Books', compute='_compute_count_books')
    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)
class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

    name = fields.Char('Title', required=True, help='Total book page count')
    short_name = fields.Char('Short Title', required=True)
    ovog = fields.Char('ovog')
    lname = fields.Char('lname')
    fname = fields.Char('fname')
    date_release = fields.Date('Release Date', groups='mylib.group_librarian')
    author_ids = fields.Many2many(
        'res.partner',
        string='Authors1'
    )
    publisher_id = fields.Many2one(
        'res.partner', string='Publisher',
        # optional:
        ondelete='set null',
        context={},
        domain=[],
    )
    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True)
    category_id = fields.Many2one('library.book.category')

    cover = fields.Binary('Book Cover')
    active = fields.Boolean('Active', default=True)
    cost_price = fields.Float('Book Cost', digits='book price')



    def name_get(self):
        result = []
        # print(self.id, self.date_release)
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
        result.append((record.id, rec_name))
        return result

    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,
        # optional
        compute_sudo=True  # optional
    )

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()

        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
        book.date_release = d
    def _search_age(self, operator, value):
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

    #ref field ni
    ref_doc_id = fields.Reference(
        selection='_referencable_models',
        string='Reference Document')
    #dynamic ref gene
    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    state = fields.Selection(
           [('draft', 'Not Available'),
            ('available', 'Available'),
            ('lost', 'Lost')],
            'State', default="draft")

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state,new_state):
                book.state = new_state
            else:
                continue

    def make_available(self):
        self.change_state('available')
    def make_borrowed(self):
        self.change_state('borrowed')
    def make_lost(self):
        self.change_state('lost')
class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')