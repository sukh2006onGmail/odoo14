from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import UserError
from odoo.tools.translate import _

class LibraryBook_class(models.Model):
    _name = 'library1.book1'
    _description = 'Library Book desc'
    _rec_name = 'short_name'

    name = fields.Char('Title', required=True)
    ovog = fields.Char('ovog')
    date_release = fields.Date('Release Date')
    # short_name = fields.Char('Short Title', required=True)
    short_name = fields.Char('Short Title', translate=True, index=True)
    author_ids = fields.Many2many('res.partner', string='Authors')

    notes = fields.Text('Internal Notes')
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [('draft', 'Not Available'),
         ('available', 'Available'),
         ('borrowed', 'Borrowed'),
         ('lost', 'Lost')],
        'State',  default="draft")
    description = fields.Html('Description')
    escription = fields.Html('Description',  sanitize=True, strip_style=False)
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages', groups='base.group_user', states={'lost': [('readonly', True)]}, help='Total book page count', company_dependent=False)
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4),)  # Optional precision decimals,  )
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary('Retail Price',)# optional: currency_field='currency_id',
    category_id = fields.Many2one('library.book.category')
    cost_price = fields.Float('Book Cost')


    def average_book_occupation(self):      #raw query
        self.flush()
        sql_query = """
            SELECT
                lb.name,
                avg((EXTRACT(epoch from age(return_date, rent_date)) / 86400))::int
            FROM
                library_book_rent AS lbr
            JOIN
                library1_book1 as lb ON lb.id = lbr.book_id
            WHERE lbr.state = 'returned'
            GROUP BY lb.name;"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        _logger.info("Average book occupation: %s", result)


    def book_rent(self):
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()    #end bookrent-n instance ruu sudo erheer handad bgamuda.
        rent_as_superuser.create({                                  #end bookrent-n create method iig duudj bn.
            'book_id': self.id,
            'borrower_id': self.env.user.partner_id.id,
        })


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
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)


    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,  # optional
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




    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
        result.append((record.id, rec_name))
        return result

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

    _sql_constraints = [
         ('name_uniq', 'UNIQUE (name)',         'Book title must be unique.'),
         ('positive_page', 'CHECK(pages>0)',    'No of pages must be positive')
         ]


    def log_all_library_members(self):
        # This is an empty recordset of model library.member
        library_member_model = self.env['library.member']

        all_members = library_member_model.search([])
        print("ALL MEMBERS:" ) #, all_members)
        return True

    def create_categories(self):
        categ1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }
        categ2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }
        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        # Total 3 records (1 parent and 2 child) will be craeted in library.book.category model
        record = self.env['library.book.category'].create(parent_category_val)
        return True

    class LibraryMember(models.Model):
        _name = 'library.member'
        _inherits = {'res.partner': 'partner_id'}
        _description = "Library member"

        partner_id = fields.Many2one('res.partner', ondelete='cascade')
        date_start = fields.Date('Member Since')
        date_end = fields.Date('Termination Date')
        member_number = fields.Char()
        date_of_birth = fields.Date('Date of birth')

    def change_release_date(self):  #db update hiij chadjiin.
        self.ensure_one()           #self ni yag neg moriig ilerhiilj bga esehig shalgana. chadq bol raise.
        self.date_release = fields.Date.today()
        # self.update({             #ene ingej boldin bn.
        #     'date_release': fields.Datetime.now(),
        #     'another_field': 'value'
        #         ...
        # })

        #write() bas iim func er hadgalj boldog gene.175 huudsand bga.


    def find_book(self):    #177 hudas der bga. lav print ni ajillaj bn.
        domain = [
            '|',
                '&', ('name', 'ilike', 'Book Name'),
                     ('category_id.name', '=', 'Category Name'),
                '&', ('name', 'ilike', 'Book Name 2'),
                     ('category_id.name', '=', 'Category Name 2')
        ]
        books = self.search(domain)
        print('books=========================================================================')
        # logger.info('Books found: %s', books)
        return True

    # def find_partner(self):
    #     PartnerObj = self.env['res.partner']
    #     domain = [
    #         '&', ('name', 'ilike', 'Parth Gajjar'),
    #         ('company_id.name', '=', 'Odoo')
    #     ]
    #     partner = PartnerObj.search(domain)

















