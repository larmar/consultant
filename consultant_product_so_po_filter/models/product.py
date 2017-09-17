# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2016-TODAY Linserv Aktiebolag, Sweden (<http://www.linserv.se>).
#
##############################################################################

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """This function is used to filter products in Sales order & Purchase Order; 
        products that are selected in exisging, Ongoing Sales Order OR Purchase Order.
        """
        context = self._context
        so_products, po_products, product_filter_ids = [], [], []

        if context and isinstance(context, dict):
            if context.get('product_filter_so_po', False):
                #get products from ongoing Sales Orders:
                self._cr.execute("""select sol.product_id from sale_order so, sale_order_line sol
                                        where sol.order_id=so.id and so.state='sale'""")
                result = self._cr.fetchall()
                for res in result:
                    so_products.append(res[0])
                so_products = list(set(so_products))

                #get products from ongoing Purchase Orders:
                self._cr.execute("""select pol.product_id from purchase_order po, purchase_order_line pol
                                        where pol.order_id=po.id and po.state='purchase'""")
                result = self._cr.fetchall()
                for res in result:
                    po_products.append(res[0])
                po_products = list(set(po_products))

                product_filter_ids = list(set(so_products + po_products))
                if product_filter_ids:
                    if not args:
                        args = [['id', 'not in', product_filter_ids]]
                    else:
                        args.append(['id', 'not in', product_filter_ids])

        return super(ProductProduct, self).search(args, offset, limit, order, count)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """This function is used to filter products in Sales order & Purchase Order; 
        products that are selected in exisging, Ongoing Sales Order OR Purchase Order.
        """
        context = self._context
        so_products, po_products, product_filter_ids = [], [], []

        if context and isinstance(context, dict):
            if context.get('product_filter_so_po', False):
                #get products from ongoing Sales Orders:
                self._cr.execute("""select sol.product_id from sale_order so, sale_order_line sol
                                        where sol.order_id=so.id and so.state='sale'""")
                result = self._cr.fetchall()
                for res in result:
                    so_products.append(res[0])
                so_products = list(set(so_products))

                #get products from ongoing Purchase Orders:
                self._cr.execute("""select pol.product_id from purchase_order po, purchase_order_line pol
                                        where pol.order_id=po.id and po.state='purchase'""")
                result = self._cr.fetchall()
                for res in result:
                    po_products.append(res[0])
                po_products = list(set(po_products))

                product_filter_ids = list(set(so_products + po_products))
                if product_filter_ids:
                    if not args:
                        args = [['id', 'not in', product_filter_ids]]
                    else:
                        args.append(['id', 'not in', product_filter_ids])

        return super(ProductProduct, self).name_search(name, args, operator, limit)
