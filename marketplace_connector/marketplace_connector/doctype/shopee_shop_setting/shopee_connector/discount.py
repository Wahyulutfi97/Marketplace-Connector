# /usr/bin/env python
# -*- coding:utf8 -*-
from .base import BaseModule


class Discount(BaseModule):
    """
        shopee discount api
    """

    def add_discount(self, **kwargs):
        """
        Use this call to add shop discount activity
        :return:
        """
        return self.client.execute("/api/v2/discount/add_discount", "POST", kwargs)
        
    def delete_discount(self, **kwargs):
        """
        Use this call to delete shop discount activity
        :return:
        """
        return self.client.execute("/api/v2/discount/delete_discount", "POST", kwargs)
        
    def get_discount_list(self, **kwargs):
        """
        Use this call to get a shop discount activity list
        :return:
        """
        return self.client.execute("/api/v2/discount/get_discount_list", "GET", kwargs)
        
    def update_discount(self, **kwargs):
        """
        Use this call to update a shop discount activity
        :return:
        """
        return self.client.execute("/api/v2/discount/update_discount", "POST", kwargs)
        
    def end_discount(self, **kwargs):
        """
        Use this call to end a shop discount activity
        :return:
        """
        return self.client.execute("/api/v2/discount/end_discount", "POST", kwargs)
