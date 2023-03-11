from odoo import models, fields, api
class BookCategory(models.Model):
    _name = 'library.book.category'
    _parent_store = True
    parent_path = fields.Char(index=True)
    _parent_name = "parent_id"

    name = fields.Char('Category')
    description = fields.Text('Description')
    parent_id = fields.Many2one('library.book.category', string='Parent Category', ondelete='restrict', index=True)
    child_ids = fields.One2many('library.book.category', 'parent_id', string='Child Categories')

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')

    def create_categories(self):
        categ1 = {
            'name': 'Child category 3',
            'description': 'Description for child 3'
        }
        categ2 = {
            'name': 'Child category 4',
            'description': 'Description for child 4'
        }
        parent_category_val = {
            'name': 'Parent category 3',
            'description': 'Description for parent category',
            'child_ids': [
                (6, 0, categ1),
                (6, 0, categ2),
            ]
        }
        # Total 3 records (1 parent and 2 child) will be craeted in library.book.category model
        record = self.env['library.book.category'].create(parent_category_val)
        return True















