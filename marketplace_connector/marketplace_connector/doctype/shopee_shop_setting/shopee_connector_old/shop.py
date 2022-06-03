from .base import BaseModule


class Shop(BaseModule):

    def get_shop_info(self, **kwargs):
        """
        Use this call to get information of shop.

        :param kwargs
        :return
            - shop_id
            - shop_name
            - country
            - shop_description
            - videos
            - images
            - disable_make_offer
            - enable_display_unitno

        @@Significant OpenAPI Updates (2018-09-15/2018-08-13)
        Added item_limit in the return parameters to indicate the max listed item number for the shop.
        """
        #return self.client.execute("shop/get", "POST", kwargs)
        return self.client.execute("shop/get_shop_info", "GET", kwargs)

    def get_shop_profile(self, **kwargs):
        """
        Use this call to get the shop information.

        :param kwargs
        :return
            - shop information
        @@Significant OpenAPI Updates (2018-09-15/2018-08-13)
        Added item_limit in the return parameters to indicate the max listed item number for the shop.
        """
        #return self.client.execute("shop/get", "POST", kwargs)
        return self.client.execute("shop/get_profile", "GET", kwargs)

    def update_shop_info(self, **kwargs):
        """
        Use this call to update information of shop.

        :param kwargs
            - shop_name
            - shop_logo
            - shop_description
        :return
        """
        #return self.client.execute("shop/update", "POST", kwargs)
        return self.client.execute("shop/update_profile", "POST", kwargs)

    def performance(self, **kwargs):
        """
        Shop performance includes the indexes from "My Performance" of Seller Center.

        :param kwargs
        :return

        @@Significant OpenAPI Updates (2018-09-15/2018-07-18)
        """
        return self.client.execute("account_health/shop_performance", "POST", kwargs)


    def authorize(self ,redirect_url="https://shopee.tw"):
        """
        Use this api to begin the process of authorization for a shop and a partner. 
        Partner should build this url with correct parameters and provide to shop owner. 
        After call this api as GET method, user will be leaded to seller login page to validate user's permission.

        :param kwargs
            - redirect, string, redirect url after authorization finished.
            - token, string, token created by partner key and redirect.
            - id, uint64, partner id.

        :return 
            - A authorize url

        @@Significant OpenAPI Updates (2018-10-19)
        """
        return self.client.shop_authorization("shop/auth_partner", "GET", redirect_url)


    def cancel_authorize(self ,redirect_url="https://shopee.tw"):
        """
        Use this api to begin the process of canceling authorization for a shop and a partner. 
        Partner should build this url with correct parameters and provide to shop owner.
        After call this api as GET method, user will be leaded to seller login page to validate user's permission.
        
        :param kwargs
            - redirect, string, redirect url after authorization finished.
            - token, string, token created by partner key and redirect.
            - id, uint64, partner id.

        :return 
            - A cancel authorize url

        @@Significant OpenAPI Updates (2018-10-19)
        """
        #return self.client.shop_authorization("shop/cancel_auth_partner", "GET", redirect_url)
        return self.client.shop_authorization("shop/cancel_partner", "GET", redirect_url)
