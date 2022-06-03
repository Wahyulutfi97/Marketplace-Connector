# /usr/bin/env python
# -*- coding:utf8 -*-
from .base import BaseModule
import frappe


class Item(BaseModule):

    def add(self, product_data_shopee):
        """
        Use this call to add a product item. Should get dependency by calling below API first
        shopee.product.GetCategories
        shopee.product.GetAttributes
        shopee.logistics.GetLogistics
        :param product_data:
        :return:
        """
        #return self.client.execute("item/add", "POST", product_data_shopee)
        return self.client.execute("product/add_item", "POST", product_data_shopee)
    
    # tambahan untuk update image
    def update_image(self, **kwargs):
        """
        Use this call to update product item images.

        :param kwargs:
        :return:
        """
        return self.client.execute("item/img/update", "POST", kwargs, 1)
        #return self.client.execute("product/update_item/image", "POST", kwargs)

    def addDiscount(self, **kwargs):
        """
        Use this call to add product item discount.

        :param kwargs:
        :return:
        """
        #return self.client.execute("discount/add", "POST", kwargs)
        return self.client.execute("discount/add_discount_item", "POST", kwargs)

    def deleteDiscount(self, **kwargs):
        """
        Use this call to delete product item discount.

        :param kwargs:
        :return:
        """
        ##return self.client.execute("discount/delete", "POST", kwargs)
        return self.client.execute("discount/delete_discount_item", "POST", kwargs)

    def updateDiscount(self, **kwargs):
        """
        Use this call to update product item discount.

        :param kwargs:
        :return:
        """
        return self.client.execute("discount/update_discount_item", "POST", kwargs, 1)

    def add_item_img(self, **kwargs):
        """
        Use this call to add product item images.

        :param kwargs:
        :return:
        """
        return self.client.execute("item/img/add", "POST", kwargs, 1)
        #return self.client.execute("product/add_item/img", "POST", kwargs)

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
        return self.client.execute("product/get_item_base_info", "GET", kwargs)

    def get_item_list(self, **kwargs):
        """
        Use this call to get a list of items
        :param kwargs:
        :return:
        """
        #return self.client.execute("items/get", "POST", kwargs)
        return self.client.execute("product/get_item_list", "GET", kwargs)

    def update(self, update_data):
        """
        Use this call to update a product item. Should get dependency by calling below API first
        shopee.item.GetItemDetail
        :param update_data:
        :return:
        """
        #return self.client.execute("item/update", "POST", update_data)
        return self.client.execute("product/update_item", "POST", update_data)

    def update_price(self, **kwargs):
        """
        Use this call to update item price

        :param kwargs:
        :return:
        """
       # return self.client.execute("items/update_price", "POST", kwargs)
        return self.client.execute("product/update_price", "POST", kwargs)

    def update_stock(self, **kwargs):
        """
        Use this call to update item stock
        :param kwargs:
        :return:
        """
        #return self.client.execute("items/update_stock", "POST", kwargs)
        return self.client.execute("product/update_stock", "POST", kwargs)

    def insert_item_img(self, **kwargs):
        """
        Use this call to add one item image in assigned position.
        :param kwargs:
        :return:
        """
        return self.client.execute("item/img/insert", "POST", kwargs, 1)
        #return self.client.execute("product/add_item/img", "POST", kwargs)
        
    def get_attributes(self, **kwargs):
        """
        Use this call to get attributes of product item
        :param kwargs:
        :return:
        """
        #return self.client.execute("item/attributes/get", "POST", kwargs)
        return self.client.execute("product/get_attributes", "GET", kwargs)

    def get_categories(self, **kwargs):
        """
        Use this call to get categories of product item
        :param kwargs:
        :return:
        """
        #return self.client.execute("item/categories/get", "POST", kwargs)
        return self.client.execute("product/get_shop_category_list", "GET", kwargs)

    def get_category_by_country(self, **kwargs):
        """
        SOON TO BE DEPRECATED WITH NO ALTERNATIVES
        Use this api to get categories list filtered by country and cross border without using shopID.
        :param kwargs:
            : country(String)      - Two-digit country code.
            : is_cb(uint8)         - Is cross border or not. 1: cross border; 0: not cross border
        @@Significant OpenAPI Updates (2018-09-15/2018-07-18)
        """
        return self.client.execute("item/categories/get_by_country", "POST", kwargs, 1)
        #return self.client.execute("product/get_category/by_country", "POST", kwargs)


    def update_price_batch(self, **kwargs):
        """
        Update items price in batch.
        :param kwargs:
            : items(object[])  - List of items to update price. Up to 50 items in one call.
                : item_id
                : price
        @@Significant OpenAPI Updates (2018-09-15/2018-09-11)
        """
        return self.client.execute("items/update/items_price", "POST", kwargs, 1)
        #return self.client.execute("product/update_item/price", "POST", kwargs)

    def update_stock_batch(self, **kwargs):
        """
        Update items stock in batch.
        :param kwargs:
            : items(object[])  - List of items to update stock. Up to 50 items in one call.
                : item_id
                : stock
        @@Significant OpenAPI Updates (2018-09-15/2018-09-11)
        """
        return self.client.execute("items/update/items_stock", "POST", kwargs, 1)
        #return self.client.execute("product/update_item/stock", "POST", kwargs)


    def update_variation_price_batch(self, **kwargs):
        """
        Update variations price in batch.
        :param kwargs:
            : variations(object[])  - List of variations to update price. Up to 50 variations in one call.
                : variation_id
                : price
                : item_id
        
        @@Significant OpenAPI Updates (2018-09-15/2018-09-11)
        """
        return self.client.execute("items/update/vars_price", "POST", kwargs, 1)
        #return self.client.execute("product/update_item/vars_price", "POST", kwargs)


    def update_variation_stock_batch(self, **kwargs):
        """
        Update variations stock in batch.
        :param kwargs:
            : variations(object[])  - List of variations to update stock. Up to 50 variations in one call.
                : variation_id
                : stock
                : item_id
        
        @@Significant OpenAPI Updates (2018-09-15/2018-09-11)
        """
        return self.client.execute("items/update/vars_stock", "POST", kwargs, 1)
        #return self.client.execute("product/update_item/vars_stock", "POST", kwargs)




    '''
        2-Tier Variation API set(TW not live)
            item.InitTierVariation
            item.AddTierVariation
            item.GetVariations
            item.UpdateTierVariationList
            item.UpdateTierVariationIndex
        @@Significant OpenAPI Updates (2018-12-01)
    '''
    
    def init_tier_variation(self, **kwargs):
        """
        Initialize a non-tier-variation item to a tier-variation item, and initialize stock and price for each variation. 
        This API cannot edit existed tier_variation and variation price/stock.
        :param kwargs:
        """
        return self.client.execute("item/tier_var/init", "POST", kwargs, 1)

    def add_tier_variation(self, **kwargs):
        """
        Use this api to add new tier variations in batch. 
        Tier variation index of variations in the same item must be unique.
        :param kwargs:
        """
        return self.client.execute("item/tier_var/add", "POST", kwargs, 1)

    def get_variations(self, **kwargs):
        """
        Use this call to get tier-variation basic information under an item.
        :param kwargs:
        """
        return self.client.execute("item/tier_var/get", "POST", kwargs, 1)

    def update_tier_variation_list(self, **kwargs):
        """
        Use this api to update tier-variation list of a tier-variation item.
        :param kwargs:
        """
        return self.client.execute("item/tier_var/update_list", "POST", kwargs, 1)


    def update_tier_variation_index(self, **kwargs):
        """
        Use this api to update existing tier index under the same variation_id.
        :param kwargs:
        """
        return self.client.execute("item/tier_var/update", "POST", kwargs, 1)


    def boost_item(self, **kwargs):
        """
        Use this api to boost multiple items at once.
        :param kwargs:
            - item_id(uint32[]) : A list of item ids to be boosted. You can input a maximum of 5 items per request.
            
        @@Significant OpenAPI Updates (2019-06-03)
        """
        #return self.client.execute("items/boost", "POST", kwargs)
        return self.client.execute("product/boost_item", "POST", kwargs)


    def get_boosted_items(self, **kwargs):
        """
        Use this api to get all boosted items.
        :param kwargs:
        @@Significant OpenAPI Updates (2019-06-03)
        """
        #return self.client.execute("items/get_boosted", "POST", kwargs)
        return self.client.execute("product/get_boosted_list", "POST", kwargs)


    def set_item_installment_tenures(self, **kwargs):
        """
        Only for TW whitelisted shop. Use this API to set the installment tenures of items.
        :param kwargs:
            - item_id(uint32): Shopee's unique identifier for an item.
            - tenures(list): List of installments, applicable values: 3, 6, 12, 24. 
                             If the list is empty, it means you wanna close the installment.
        @@Significant OpenAPI Updates (2019-06-03)
        """
        #return self.client.execute("item/installment/set", "POST", kwargs)
        return self.client.execute("payment/get_item_installment_status", "POST", kwargs)


    def reply_comment(self, **kwargs):
        """
        Use this api to reply comment in batch.
        :param kwargs:
        @@Significant OpenAPI Updates (2019-06-03)
        """

        #return self.client.execute("items/comments/reply","POST",kwargs)
        return self.client.execute("product/reply_comment", "POST", kwargs)
