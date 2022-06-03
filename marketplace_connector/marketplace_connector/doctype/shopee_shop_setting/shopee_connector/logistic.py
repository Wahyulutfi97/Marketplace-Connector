# /usr/bin/env python
# -*- coding:utf8 -*-
from .base import BaseModule


class Logistic(BaseModule):
    """
        shopee Logistic api
    """


    def update_logistics(self, **kwargs):
        """
        Use this call to get all supported Logistic Channel
        :return:
        """
        #return self.client.execute("logistics/channels/update", "POST", kwargs)
        return self.client.execute("/api/v2/logistics/update_channel", "POST", kwargs)

    def get_logistics(self, **kwargs):
        """
        Use this call to get all supported Logistic Channel
        :return:
        """
        #return self.client.execute("logistics/channel/get", "POST", kwargs)
        return self.client.execute("/api/v2/logistics/get_channel_list", "GET", kwargs)

    def get_address(self):
        """
        Use this call to get all required param for init logistic.
        :return:
        """
        #return self.client.execute("logistics/address/get", "POST")
        return self.client.execute("/api/v2/logistics/get_address_list", "GET")

    def get_airway_bill(self, **kwargs):
        """
        Use this API to get airway bill for orders
        :param kwargs:
        :return:
        """
        #return self.client.execute("logistics/airway_bill/get_mass", "POST", kwargs)
        return self.client.execute("/api/v2/logistics/get_shipping_document_info", "GET", kwargs)

    def get_branch(self, **kwargs):
        """
        Use this call to get all required param for init logistic.
        :param kwargs:
        :return:
        """
        #return self.client.execute("logistics/branch/get", "POST", kwargs)
        return self.client.execute("/api/v2/logistics/get_branch_list", "POST", kwargs)

    def get_logistic_message(self, **kwargs):
        """
        Use this call to get the logistics tracking information of an order.
        :param kwargs:
        :return:
        """
        #return self.client.execute("logistics/tracking", "POST", kwargs)
        return self.client.execute("/api/v2/logistics/get_tracking_info", "POST", kwargs)

    def get_order_logistic(self, **kwargs):
        """
        Use this call to fetch the logistics information of an order, these info can be used for waybill printing.
        :param kwargs:
        :return:
        """
        #return self.client.execute("logistics/order/get", "POST", kwargs)
        return self.client.execute("/api/v2/logistics/get_order_list", "POST", kwargs)

    def get_parameter_for_init(self, **kwargs):
        """
        Use this call to get all required param for init logistic.
        :param kwargs:
        :return:
        """
        #return self.client.execute("logistics/init_parameter/get", "POST", kwargs)
        return self.client.execute("/api/v2/logistics/get_shipping_parameter", "POST", kwargs)

    def get_time_slot(self, **kwargs):
        """
        Use this call to get all required param for init logistic.
        :param kwargs:
        :return:
        """
        return self.client.execute("logistics/timeslot/get", "POST", kwargs, 1)

    def get_tracking_no(self, **kwargs):
        """
        Use this API to get tracking number of orders

        :param kwargs:
        :return:
        """
        #return self.client.execute("logistics/tracking_number/get_mass", "POST", kwargs)
        return self.client.execute("/api/v2/logistics/get_tracking_number", "GET", kwargs)

    def init(self, **kwargs):
        """
        Use this call to arrange Pickup or Dropoff. Should call shopee.logistics.GetParameterForInit to fetch all required param first.
        pickup = {}
        dropoff = {}
        non_integrated = {}
        :param kwargs:
        :return:
        """
        return self.client.execute("logistics/init", "POST", kwargs, 1)

    def set_logistic_status(self, **kwargs):
        """
        Set Logistic Status to PICKUP_DONE, this API only works for non-integrated logistic channels

        :param kwargs:
        :return:
        """
        return self.client.execute("logistics/init", "POST", kwargs, 1)

    def delete_address(self, **kwargs):
        """
        Use this call to delete selected address in init logistics.
        :return:
        """
        return self.client.execute("/api/v2/logistics/delete_address", "POST", kwargs)











