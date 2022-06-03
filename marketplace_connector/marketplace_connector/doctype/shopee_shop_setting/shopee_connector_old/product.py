# /usr/bin/env python
# -*- coding:utf8 -*-
from .base import BaseModule


class Product(BaseModule):

    def add(self, product_data):
        """
        Use this call to add a product item. Should get dependency by calling below API first
        shopee.item.GetCategories
        shopee.item.GetAttributes
        shopee.logistics.GetLogistics
        :param product_data:
        :return:
        """
        #return self.client.execute("item/add", "POST", product_data)
        return self.client.execute("product/add_item", "POST", product_data)

    # tambahan untuk update image
    def update_image(self, **kwargs):
        """
        Use this call to update product item images.

        :param kwargs:
        :return:
        """
        return self.client.execute("item/img/update", "POST", kwargs, 1)
        #return self.client.execute("product/update_item/image", "POST", kwargs)

    def add_item_img(self, **kwargs):
        """
        Use this call to add product item images.

        :param kwargs:
        :return:
        """
        return self.client.execute("item/img/add", "POST", kwargs, 1)
        #return self.client.execute("product/add_item/image", "POST", kwargs)

    def delete(self, **kwargs):
        """
        Use this call to delete a product item.
        :param kwargs:
        :return:
        """
        #return self.client.execute("item/delete", "POST", kwargs)
        return self.client.execute("product/delete_item", "POST", kwargs)

    def delete_item_img(self, **kwargs):
        """
        Use this call to delete a product item image.
        :param kwargs:
        :return:
        """
        return self.client.execute("item/img/delete", "POST", kwargs, 1)
        #return self.client.execute("product/delete_item/image", "POST", kwargs)

    def get_item_detail(self, **kwargs):
        """
        Use this call to get detail of item
        :param kwargs:
        :return:
        """
        #return self.client.execute("item/get", "POST", kwargs)
        return self.client.execute("product/get_item_base_info", "POST", kwargs)

    def get_item_ex_detail(self, **kwargs):
        """
        Use this call to get extra detail of item
        :param kwargs:
        :return:
        """
        return self.client.execute("product/get_item_extra_info", "POST", kwargs)

    def get_item_list(self, **kwargs):
        """
        Use this call to get a list of items
        :param kwargs:
        :return:
        """
        #return self.client.execute("items/get", "POST", kwargs)
        return self.client.execute("product/get_item_list", "POST", kwargs)

    def update(self, update_data):
        """
        Use this call to update a product item. Should get dependency by calling below API first
        shopee.item.GetItemDetail
        :param update_data:
        :return:
        """
        #return self.client.execute("item/update", "POST", update_data)
        return self.client.execute("product/update_item", "POST", kwargs)

    def update_price(self, **kwargs):
        """
        Use this call to update item price

        :param kwargs:
        :return:
        """
        #return self.client.execute("items/update_price", "POST", kwargs)
        return self.client.execute("product/update_price", "POST", kwargs)

    def update_stock(self, **kwargs):
        """
        Use this call to update item stock
        :param kwargs:
        :return:
        """
        #return self.client.execute("items/update_stock", "POST", kwargs)
        return self.client.execute("product/update_stock", "POST", kwargs)

    def update_stock_batch(self, **kwargs):
        """
        Use this call to update item stock
        :param kwargs:
        :return:
        """
        return self.client.execute("items/update/items_stock", "POST", kwargs, 1)

    def insert_item_img(self, **kwargs):
        """
        Use this call to add one item image in assigned position.
        :param kwargs:
        :return:
        """
        return self.client.execute("item/img/insert", "POST", kwargs, 1)
