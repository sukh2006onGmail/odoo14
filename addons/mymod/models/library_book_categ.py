from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BookCategory(models.Model):
   _name = 'library.book.category'
   _parent_store = True
   _parent_name = "parent_id"  # optional if field is 'parent_id'
   _description = "aabb"
   parent_path = fields.Char(index=True)

   name = fields.Char('Category')



   description = fields.Text('Description')
   parent_id = fields.Many2one( 'library.book.category', string='Parent Category', ondelete='restrict', index=True)
   child_ids = fields.One2many('library.book.category', 'parent_id',  string='Child Categories')


   @api.constrains('parent_id')     #save burd ajillaj bn.
   def _check_hierarchy(self):
       print('orloo')
       if not self._check_recursion():
           raise models.ValidationError('Error! You cannot create recursive categories.')















