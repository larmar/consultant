# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class ProductProduct(models.Model):
    _inherit = "product.product"

    consultant_product = fields.Boolean('Is Consultant Product?', copy=False)
    non_standard_product = fields.Boolean('Is Non-Standard Product?', copy=False)
    consultant_id = fields.Many2one('consultant.consult', 'Related Consultant', copy=False, readonly=True)
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """This function is used to filter Consultant Products
        """
        context = self._context
        if not context: context = {}
        
        self._cr.execute("""select id from product_product where consultant_id >= 0;""")
        productlist = self._cr.fetchall()
        consultant_products = [x[0] for x in productlist]
        
        domain = ['id', 'not in', consultant_products]
        if context.get('show_consultant_product_template', False):
            domain = ['id', 'in', consultant_products]    

        if not args:
            args = [domain]
        else:
            args.append(domain)

        return super(ProductProduct, self).search(args, offset, limit, order, count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """This function is used to filter Consultant Products
        """
        context = self._context
        if not context: context = {}
        
        self._cr.execute("""select id from product_product where consultant_id >= 0;""")
        productlist = self._cr.fetchall()
        consultant_products = [x[0] for x in productlist]
        
        domain = ['id', 'not in', consultant_products]
        if context.get('show_consultant_product_template', False):
            domain = ['id', 'in', consultant_products]    

        if not args:
            args = [domain]
        else:
            args.append(domain)

        return super(ProductProduct, self).name_search(name, args, operator, limit)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """This function is used to filter Consultant Products
        """
        context = self._context
        if not context: context = {}
        
        self._cr.execute("""
                select pt.id from product_template pt, product_product pp 
                    where pt.id=pp.product_tmpl_id and
                        pp.consultant_id >= 0;
                """)
        productlist = self._cr.fetchall()
        consultant_products = [x[0] for x in productlist]
        
        domain = ['id', 'not in', consultant_products]
        if context.get('show_consultant_product_template', False):
            domain = ['id', 'in', consultant_products]    

        if not args:
            args = [domain]
        else:
            args.append(domain)

        return super(ProductTemplate, self).search(args, offset, limit, order, count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """This function is used to filter Consultant Products
        """
        context = self._context
        if not context: context = {}
        
        self._cr.execute("""
                select pt.id from product_template pt, product_product pp 
                    where pt.id=pp.product_tmpl_id and
                        pp.consultant_id >= 0;
                """)
        productlist = self._cr.fetchall()
        consultant_products = [x[0] for x in productlist]
        
        domain = ['id', 'not in', consultant_products]
        if context.get('show_consultant_product_template', False):
            domain = ['id', 'in', consultant_products]    

        if not args:
            args = [domain]
        else:
            args.append(domain)

        return super(ProductTemplate, self).name_search(name, args, operator, limit)
