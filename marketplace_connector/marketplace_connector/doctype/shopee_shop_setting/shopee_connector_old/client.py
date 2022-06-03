# /usr/bin/env python
# -*- coding:utf8 -*-
import time
import json
import hmac, hashlib
from urllib.parse import urljoin
from requests import Request, Session, exceptions
from .shop import Shop
from .shopcategory import ShopCategory
from .order import Order
from .product import Product
from .item import Item
from .variation import Variation
from .logistic import Logistic
from .rma import RMA
from .category import Category
from .discount import Discount
from .setting import BASE_URL, BASE_URL2 as BASE_URL_V2
import frappe

# installed sub-module
installed_module = {
    "shop":Shop,
    "shopcategory":ShopCategory,
    "order":Order,
    "product":Product,
    "item":Item,
    "variation":Variation,
    "logistic":Logistic,
    "rma":RMA,
    "discount":Discount,
    "category":Category
}


class ClientMeta(type):
    def __new__(mcs, name, bases, dct):
        # frappe.msgprint(str(name))
        klass = super().__new__(mcs, name, bases, dct)
        setattr(
            klass, "installed_module",
            installed_module
        )
        return klass


class Client(object, metaclass=ClientMeta):
    __metaclass__ = ClientMeta
    cached_module = {}

    def __init__(self, shop_id: int, partner_id: int, secret_key: str):
        self.shop_id = shop_id
        self.partner_id = int(partner_id)
        self.secret_key = secret_key
        # frappe.msgprint(str(str(self.shop_id) + "<<< self shop id yang di atas"))

    def __getattr__(self, name):
        try:
            value = super(Client, self).__getattribute__(name)
        except AttributeError as e:
            value = self.get_cached_module(name)
            if not value:
                raise e
        return value

    def make_timestamp(self):
        return int(time.time())

    def make_default_parameter(self):
        # frappe.msgprint(str(str(self.shop_id) + "<<< self shop id yang di bawah"))
        return {
            "partner_id": self.partner_id,
            "shopid": self.shop_id,
            "timestamp": self.make_timestamp()
        }

    def sign(self, url, body):
        bs = url + "|" + json.dumps(body)
        dig = hmac.new(self.secret_key.encode(), msg=bs.encode(), digestmod=hashlib.sha256).hexdigest()
        return dig

    """
    def build_request(self, uri, method, body):
        method = method.upper()
        url = urljoin(BASE_URL_V2, uri)
        authorization = self.sign(url, body)
        headers = {
            "Authorization": authorization
        }
        req = Request(method, url, headers=headers)
        
        if body:
            if req.method in ["POST", "PUT", "PATH"]:
                req.json = body
            else:
                req.params = body
        
        # req.close()
        return req
        
    def execute(self, uri, method, body=None):
        parameter = self.make_default_parameter()
        
        new_parameter = {}

        if body is not None:
            parameter.update(body)
        
        for i in parameter: 
            if  i == "shopid" :
                new_parameter['shopid'] = body['shopid']
            else :
                new_parameter[i] = parameter[i]

        req = self.build_request(uri, method, new_parameter)
        prepped = req.prepare()
        s = Session()
        # s = requests.session(config={'keep_alive': False})
        
        resp = s.send(prepped,stream=False)
        resp = self.build_response(resp)
        # frappe.msgprint(str(s))
        return resp
    """

    def build_request(self, uri, method, body, version):
        method = method.upper()
        if version==1:
            url = urljoin(BASE_URL, uri)
        elif version==2:
            url = urljoin(BASE_URL_V2, uri)
        else:
            e = "Shopee doesn't have that version"
            raise e
        authorization = self.sign(url, body)
        headers = {
            "Authorization": authorization
        }
        req = Request(method, url, headers=headers)
        
        if body:
            if req.method in ["POST", "PUT", "PATH"]:
                req.json = body
            else:
                req.params = body
        
        return req
    
    def execute(self, uri, method, body=None, version=2):
        parameter = self.make_default_parameter()
        
        new_parameter = {}

        if body is not None:
            parameter.update(body)
        
        for i in parameter: 
            if  i == "shopid" :
                new_parameter['shopid'] = body['shopid']
            else :
                new_parameter[i] = parameter[i]

        req = self.build_request(uri, method, new_parameter, version)
        prepped = req.prepare()
        s = Session()
        
        resp = s.send(prepped,stream=False)
        resp = self.build_response(resp)
        return resp

    def build_response(self, resp):
        try:
            return resp.json()
        except (ValueError, json.JSONDecodeError) as e:
            raise resp.raise_for_status()

    def get_cached_module(self, key):
        cache_key = str(self.partner_id) + key

        cached_module = self.cached_module.get(cache_key)

        if not cached_module:
            installed = self.installed_module.get(key)
            if not installed:
                return None
            cached_module = installed(self)
            self.cached_module.setdefault(cache_key, cached_module)
        return cached_module
