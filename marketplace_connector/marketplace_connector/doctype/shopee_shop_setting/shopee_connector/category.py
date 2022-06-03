# /usr/bin/env python
# -*- coding:utf8 -*-
from .base import BaseModule


class Category(BaseModule):

    def get_categories(self, **kwargs):
        """
        Use this call to get categories of product item
        :param kwargs:
        :return:
        """
        #return self.client.execute("item/categories/get", "POST", kwargs)
        return self.client.execute("/api/v2/product/get_category", "GET", kwargs, 2)

    def get_attributes(self, **kwargs):
        """
        Use this call to get attributes of product item
        :param kwargs:
        :return:
        """
        #return self.client.execute("item/attributes/get", "POST", kwargs)
        return self.client.execute("/api/v2/product/get_attributes", "GET", kwargs, 2)

