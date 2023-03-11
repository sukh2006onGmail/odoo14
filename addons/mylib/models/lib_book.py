from odoo import models, fields, api
from datetime import timedelta

from odoo.exceptions import UserError
from odoo.tools.translate import _

import logging
logger = logging.getLogger(__name__)

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

    # state = fields.Selection(
    #        [('draft', 'Not Available'),
    #         ('available', 'Available'),
    #         ('lost', 'Lost')],
    #         'State', default="draft")
    state = fields.Selection(
        [('available', 'Available'),
         ('borrowed', 'Borrowed'),
         ('lost', 'Lost')],
        'State', default="available")

    # @api.model
    # def is_allowed_transition(self, old_state, new_state):
    #     allowed = [('draft', 'available'),
    #                ('available', 'borrowed'),
    #                ('borrowed', 'available'),
    #                ('borrowed', 'ongoing'),
    #                ('available', 'lost'),
    #                ('borrowed', 'lost'),
    #                ('lost', 'available')]
    #     return (old_state, new_state) in allowed

    # def change_state(self, new_state):
    #     for book in self:
    #         if book.is_allowed_transition(book.state,new_state):
    #             book.state = new_state
    #         else:
    #             message = _('Moving from %s to %s is not allowd') % (book.state, new_state)
    #             raise UserError(message)

    # def make_available(self):
    #     self.change_state('available')
    # def make_borrowed(self):
    #     self.change_state('borrowed')
    # def make_lost(self):
    #     self.change_state('lost')

    def make_available(self):
        self.ensure_one()
        self.state = 'available'

    def make_borrowed(self):
        self.ensure_one()
        self.state = 'borrowed'

    def make_lost(self):
        self.ensure_one()
        self.state = 'lost'

    def make_lost(self):
        self.ensure_one()
        self.state = 'lost'
        if not self.env.context.get('avoid_deactivate'):    #end rent-s duudsan func avoid_deactivate = true damjuulsan bga.
            self.active = False
    def log_all_library_members(self):
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    def find_book(self):
        domain = [
            '|',
            # '&',
            ('name', 'ilike', 'bat'),
            # ('category_id.name', 'ilike', ''),
            #  '&',
            ('name', 'ilike', 'dorj'),
            # ('category_id.name', 'ilike', '')
             ]
        books = self.search(domain)
        return book

    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        logger.info('Filtered Books: %s', filtered_books)
        return true

    @api.model
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
        return all_books.filtered(predicate)

    def book_rent(self):
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()        #yamr neg hailt hiigdeq uchir empty recordset irne gejishu.
        rent_as_superuser.create({
            'book_id': self.id,
            'borrower_id': self.env.user.partner_id.id,
        })
        # public_user = self.env.ref('base.public_user')                #sudogiin orond ingej oor usereer uildel hiij bolhin shig bn.
        # public_book = self.env['library.book'].with_user(public_user)
        # public_book.search([('name', 'ilike', 'cookbook')])



















class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')
class LibraryBookRent(models.Model):
    _name = 'library.book.rent'

    book_id = fields.Many2one('library.book', 'Book', required=True)
    borrower_id = fields.Many2one('res.partner', 'Borrower', required=True)
    state = fields.Selection([('ongoing', 'Ongoing'), ('returned', 'Returned'), ('lost', 'Lost')], 'State', default='ongoing', required=True)
    rent_date = fields.Date(default=fields.Date.today)
    return_date = fields.Date()

    @api.model
    def create(self, vals):
        book_rec = self.env['library.book'].browse(vals['book_id'])  # returns record set from for given id
        book_rec.make_borrowed()
        return super(LibraryBookRent, self).create(vals)

    def book_return(self):
        self.ensure_one()
        self.book_id.make_available()
        self.write({
            'state': 'returned',
            'return_date': fields.Date.today()
        })

    def book_lost(self):
        self.ensure_one()
        self.sudo().state = 'lost'
        book_with_different_context = self.book_id.with_context(avoid_deactivate=False)  #ene bookiin make lost ruu avoid_deactivate=True utga damjuulj bn.
        book_with_different_context.sudo().make_lost()      #tegeed bok ni lost tolovteigoos gadna avtive ni false bolhin bn.
        # new_context = self.env.context.copy()
        # new_context.update({'avoid_deactivate': True})

class LibraryRentWizard(models.TransientModel):
    _name = 'library.rent.wizard'
    borrower_id = fields.Many2one('res.partner',    string='Borrower')
    book_ids = fields.Many2many('library.book',    string='Books')

    def add_book_rents(self):
        rentModel = self.env['library.book.rent']
        for wiz in self:
            for book in wiz.book_ids:
                rentModel.create({                      #ene shuud rent deer bichleg nemj bn.
                    'borrower_id': wiz.borrower_id.id,
                    'book_id': book.id
                })










