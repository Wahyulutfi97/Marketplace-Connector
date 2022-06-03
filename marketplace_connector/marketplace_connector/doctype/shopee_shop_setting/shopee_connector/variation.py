# /usr/bin/env python
# -*- coding:utf8 -*-
from .base import BaseModule


class Variation(BaseModule):

    def add(self, variation_data):
        """
        Use this call to add item variations
        :param variation_data:
        :return:
        """
        return self.client.execute("item/add_variations", "POST", variation_data, 1)
        #return self.client.execute("product/add_variations", "POST", variation_data)

    def addTierVariation(self, **kwargs):
        """
        Use this call to add item variations
        :param variation_data:
        :return:
        """
        return self.client.execute("item/tier_var/add", "POST", kwargs, 1)
        #return self.client.execute("product/add_tier_variation", "POST", kwargs)

    def updateTierVariationList(self, **kwargs):
        """
        Use this call to add item variations
        :param variation_data:
        :return:
        """
        #return self.client.execute("item/tier_var/update_list", "POST", kwargs)
        return self.client.execute("/api/v2/product/update_tier_variation", "POST", kwargs)

    def updateVariationStock(self, **kwargs):
        """
        Use this call to add item variations
        :param variation_data:
        :return:
        """
        return self.client.execute("items/update_variation_stock", "POST", kwargs, 1)
    
    def updateVariationStockBatch(self, **kwargs):
        """
        Use this call to add item variations
        :param variation_data:
        :return:
        """
        return self.client.execute("items/update/vars_stock", "POST", kwargs, 1)
    
    def updateVariationPrice(self, **kwargs):
        """
        Use this call to add item variations
        :param variation_data:
        :return:
        """
        return self.client.execute("items/update_variation_price", "POST", kwargs, 1)
    
    def updateVariationPriceBatch(self, **kwargs):
        """
        Use this call to add item variations
        :param variation_data:
        :return:
        """
        return self.client.execute("items/update/vars_price", "POST", kwargs, 1)

    def getVariantTier(self, **kwargs):
        """
        Use this call to add item variations
        :param variation_data:
        :return:
        """
        return self.client.execute("item/tier_var/get", "POST", kwargs, 1)

    def initVariant(self, **kwargs):
        """
        Use this call to add item variations
        :param **kwargs:
        :return:
        """
        #return self.client.execute("item/tier_var/init", "POST", kwargs)
        return self.client.execute("/api/v2/product/init_tier_variation", "POST", kwargs)

    def delete(self, **kwargs):
        """
        Use this call to delete item variation
        :param kwargs:
        :return:
        """
        return self.client.execute("item/delete_variation", "POST", kwargs, 1)

    def update_price(self, **kwargs):
        """
        Use this call to update item variation price
        :param kwargs:
        :return:
        """
        return self.client.execute("items/update_variation_price", "POST", kwargs, 1)

    def update_stock(self, **kwargs):
        """
        Use this call to update item variation stock
        :param kwargs:
        :return:
        """
        return self.client.execute("items/update_variation_stock", "POST", kwargs, 1)