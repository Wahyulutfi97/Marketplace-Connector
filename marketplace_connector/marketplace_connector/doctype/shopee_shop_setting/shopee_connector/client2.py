# /usr/bin/env python
# -*- coding:utf8 -*-
import time
import json
import hmac, hashlib
import requests
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
from .setting import BASE_URL
from .setting import BASE_URL2
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
        # console.log(str(name))
        klass = super().__new__(mcs, name, bases, dct)
        setattr(
            klass, "installed_module",
            installed_module
        )
        return klass


class Client2(object, metaclass=ClientMeta):
    __metaclass__ = ClientMeta
    cached_module = {}

    def __init__(self, shop_id: int, partner_id: int, secret_key: str, access_token: str):
        self.shop_id = int(shop_id)
        self.partner_id = int(partner_id)
        self.secret_key = secret_key
        if (access_token):
            self.access_token = access_token
        self.timestamp = self.make_timestamp()
        # console.log(str(str(self.shop_id) + "<<< self shop id yang di atas"))

    def __getattr__(self, name):
        try:
            value = super(Client, self).__getattribute__(name)
        except AttributeError as e:
            value = self.get_cached_module(name)
            if not value:
                raise e
                frappe.throw(str(e))
        return value

    def make_timestamp(self):
        return int(time.time())

    def make_default_parameterV1(self):
        # console.log(str(str(self.shop_id) + "<<< self shop id yang di bawah"))
        return {
            "partner_id": self.partner_id,
            "shopid": self.shop_id,
            "timestamp": self.timestamp
        }
    def make_default_parameter(self):
        # console.log(str(str(self.shop_id) + "<<< self shop id yang di bawah"))
        if self.access_token: 
            return {
                "partner_id": self.partner_id,
                "shopid": self.shop_id,
                "partner_key": self.secret_key,
                "timestamp": self.timestamp,
                "access_token": self.access_token
            }
        else: 
            return {
                "partner_id": self.partner_id,
                "shopid": self.shop_id,
                "partner_key": self.secret_key,
                "timestamp": self.timestamp
            }

    def signV1(self, url, body):
        bs = url + "|" + json.dumps(body)
        dig = hmac.new(self.secret_key.encode(), bs.encode(), hashlib.sha256).hexdigest()
        return dig
        
    def sign(self, uri):
        bs = str(self.partner_id)+str(uri)+str(self.timestamp)+str(self.access_token)+str(self.shop_id)
        hash_token = hmac.new( self.secret_key.encode(), bs.encode(), hashlib.sha256).hexdigest()
        extrabody = {'partner_id': str(self.partner_id), 'timestamp': str(self.make_timestamp()), 'shop_id': str(self.shop_id), 'sign':str(hash_token)}
        console.log(str(bs))
        return extrabody
        

    def build_request(self, uri, method, body, version=2):
        method = method.upper()
        if version==1:
            url = urljoin(BASE_URL, uri)
            authorization = self.signV1(url, body)
            headers = {
                "Authorization": authorization
            }
            req = requests.Request(method, url, headers=headers)
        elif version==2:
            authorization = self.sign(uri)
            url = urljoin(BASE_URL2, uri)
            headers = {
                
            }
            req = requests.Request(method, url, headers=headers)
            if method=="GET":
                body.update(authorization)
        else:
            e = "Shopee doesn't have that version"
            frappe.throw(e)
            return None
        if body is not None:
            if req.method in ["POST", "PUT", "PATH"]:
                if version == 2:
                    req.params = authorization
                req.json = body
            else:
                req.params = body
        console.log(str(body)+str(req.params))
        return req
    
    def execute(self, uri, method, body=None, version=2):
        if version==1:
            parameter = self.make_default_parameterV1()
        elif version ==2:
            parameter = self.make_default_parameter()
        new_parameter = {}
        console.log(str(body))
        if body is not None:
            parameter.update(body)
        
        for i in parameter: 
            if  i == "shopid" :
                #new_parameter['shopid'] = body['shopid']
                new_parameter[i] = str(parameter['shopid'])
            else :
                new_parameter[i] = parameter[i]

        req = self.build_request(uri, method, new_parameter, version)
        console.log(str(req.url))
        prepped = req.prepare()
        s = Session()
        
        resp = s.send(prepped,stream=False)
        resp = self.build_response(resp)
        return resp

    def build_response(self, resp):
        try:
            console.log(str(resp.json()))
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
