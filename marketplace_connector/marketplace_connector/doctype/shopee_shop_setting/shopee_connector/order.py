# /usr/bin/env python
# -*- coding:utf8 -*-
from .base import BaseModule



class Order(BaseModule):
    """
    shopee order api
    """

    def get_order_list(self, **kwargs):
        """
        GetOrdersList is the recommended call to use for order management.
        Use this call to retrieve basic information of all orders which are updated within specific period of time.
        More details of each order can be retrieved from GetOrderDetails.
        At least one time filter need to be provided.
        You can either choose create time filter or update time filter.
        For each filter you need to provice start time and end time. Ex.
        If you choose to use create time filter, you need to specify "create_time_from" and "create_time_to" in your request.
        :param kwargs:
        :return:
        """
        #return self.client.execute("orders/basics", "POST", kwargs)
        return self.client.execute("/api/v2/orders/get_order_list", "POST", kwargs)

    def get_order_detail(self, **kwargs):
        """
        Use this call to retrieve detailed information about one or more orders based on OrderIDs.
        :param kwargs:
        :return:
        """
        #return self.client.execute("orders/detail", "POST", kwargs)
        return self.client.execute("/api/v2/orders/get_order_detail", "POST", kwargs)

    def get_order_escrow_detail(self, **kwargs):
        """
        Use this call to retrieve detailed escrow information about one order based on OrderID.
        :param kwargs:
        :return:
        """
        #return self.client.execute("orders/my_income", "POST", kwargs)
        return self.client.execute("/api/v2/payment/get_escrow_detail", "POST", kwargs)

    def get_order_by_status(self, **kwargs):
        """
        GetOrdersByStatus is the recommended call to use for order management.
        Use this call to retrieve basic information of all orders which are specific status.
        More details of each order can be retrieved from GetOrderDetails.
        :param kwargs:
        :return:
        """
        #return self.client.execute("orders/get", "POST", kwargs)
        return self.client.execute("/api/v2/orders/get_order", "POST", kwargs)

    def cancel_order(self, **kwargs):
        """
        Use this call to cancel an order
        :param kwargs:
        :return:
        """
        #return self.client.execute("orders/cancel", "POST", kwargs)
        return self.client.execute("/api/v2/orders/cancel_order", "POST", kwargs)

    def accept_buyer_cancellation(self, **kwargs):
        """
        Use this call to accept buyer cancellation
        :param kwargs:
        :return:
        """
        #return self.client.execute("orders/buyer_cancellation/accept", "POST", kwargs)
        return self.client.execute("/api/v2/orders/handle_buyer_cancellation?operation=ACCEPT&", "POST", kwargs)

    def reject_buyer_cancellation(self, **kwargs):
        """
        Use this call to reject buyer cancellation
        :param kwargs:
        :return:
        """
        #return self.client.execute("orders/buyer_cancellation/reject", "POST", kwargs)
        return self.client.execute("/api/v2/orders/handle_buyer_cancellation?operation=REJECT&", "POST", kwargs)


