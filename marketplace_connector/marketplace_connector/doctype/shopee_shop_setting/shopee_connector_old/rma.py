# /usr/bin/env python
# -*- coding:utf8 -*-
from .base import BaseModule



class RMA(BaseModule):
    """
    shopee order returns api
    """
    def confirm_return(self, **kwargs):
        """
        Confirm return
        :param kwargs:
        :return:
        """
        return self.client.execute("returns/confirm", "POST", kwargs)

    def dispute_return(self, **kwargs):
        """
        Dispute return
        :param kwargs:
        :return:
        """
        return self.client.execute("returns/dispute", "POST", kwargs)

    def get_return_list(self, **kwargs):
        """
        Get return list
        :param kwargs:
        :return:
        """
        #return self.client.execute("returns/get", "POST", kwargs)
        return self.client.execute("returns/get_return_list", "POST", kwargs)

    def get_return_detail(self, **kwargs):
        """
        Get return detail
        :param kwargs:
        :return:
        """
        return self.client.execute("returns/get_return_detail", "POST", kwargs)

    def accept_offer(self, **kwargs):
        """
        Accept return offer
        :param kwargs:
        :return:
        """
        return self.client.execute("returns/accept_offer", "POST", kwargs)

    def returns_offer(self, **kwargs):
        """
        Returns offer
        :param kwargs:
        :return:
        """
        return self.client.execute("returns/offer", "POST", kwargs)