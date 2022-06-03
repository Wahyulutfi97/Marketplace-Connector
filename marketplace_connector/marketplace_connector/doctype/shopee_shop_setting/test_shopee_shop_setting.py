# -*- coding: utf-8 -*-
# Copyright (c) 2021, PT DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# from typing import final
import frappe
import math
from frappe.model.document import Document

from marketplace_connector.marketplace_connector.doctype.frappeclient import FrappeClient
from marketplace_connector.marketplace_connector.doctype.shopee_shop_setting.shopee_connector.client import Client
from marketplace_connector.marketplace_connector.doctype.shopee_shop_setting.shopee_connector.shopcategory import ShopCategory

import json
import os
import requests
import subprocess
from frappe.utils.background_jobs import enqueue
from frappe.utils import get_site_name

from frappe import utils
from frappe.utils import nowdate, add_days, random_string, get_url

import time
import datetime
from datetime import date
from numpy import asarray

from frappe import utils

import hmac
import hashlib


def epochTime(date):
	return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f").timetuple())


@frappe.whitelist()
def runGenerateAttribute():
	listCategory = frappe.get_list('Category Shopee',{}, ['name1', 'category_id'])
	start = 0
	end = 50
	total = math.floor( len(listCategory)/50 )
	result = []
	for i in range(total):
		result.append({
			"start": start,
			"end": end,
			"data": listCategory[start:end]
		})
		start = start + 50
		end = end + 50
	return result

@frappe.whitelist()
def generateAttributes(shop, result):
	# frappe.throw(str(result))
	dataToko = frappe.get_value('Shopee Shop Setting', {'name': shop}, ["shop_id","partner_id","partner_key","name","access_code"])
	
	result = json.loads(result)
	shopid = int(dataToko[0])
	partnerid = dataToko[1]
	api_key = dataToko[2]
	access_code = dataToko[4]
	shopeeclient = Client(shopid, partnerid, api_key, access_code)

	for i in result:
		#getAttributes = shopeeclient.category.get_attributes(shopid = shopid, category_id = int(i['category_id']))
		getAttributes = shopeeclient.category.get_attributes(language = "id", category_id = int(i['category_id']))
		if "error" in getAttributes :
			pass
		else: 
			for j in getAttributes['attribute_list']:
				
				docAttribute = frappe.new_doc('Shopee Attribute')
				docAttribute.category_id = i['category_id']
				docAttribute.attribute_id = j['attribute_id']
				docAttribute.attribute_name = j['original_attribute_name']
				docAttribute.attribute_value = str((", ".join(j['attribute_unit'])))
				docAttribute.save()
	return "oke"

@frappe.whitelist()
def generateCategory(data):
	dataToko = frappe.get_value('Shopee Shop Setting', {'name': data}, ["shop_id","partner_id","partner_key","name","access_code"])

	shopid = int(dataToko[0])
	partnerid = dataToko[1]
	api_key = dataToko[2]
	access_code = dataToko[4]
	shopeeclient = Client(shopid, partnerid, api_key, access_code)

	getCategory = shopeeclient.category.get_categories(shopid = shopid)

	for i in getCategory['categories']:
		docCategory = frappe.new_doc('Category Shopee')
		docCategory.category_id = i['category_id']
		docCategory.name1 = i['category_name']
		docCategory.has_children = i['has_children']
		docCategory.save()
	
	result = {
		"allcategory": getCategory
	}
	return result

@frappe.whitelist()
def generateLogistic(data):
	dataToko = frappe.get_value('Shopee Shop Setting', {'name': data}, ["shop_id","partner_id","partner_key","name","access_code"])

	shopid = int(dataToko[0])
	partnerid = dataToko[1]
	api_key = dataToko[2]
	access_code = dataToko[4]
	shopeeclient = Client(shopid, partnerid, api_key, access_code)
	
	#getLogistic = shopeeclient.logistic.get_logistics(shopid = shopid)
	getLogistic = shopeeclient.logistic.get_logistics()

	for i in getLogistic['logistics_channel_list']:
		docLogistic = frappe.new_doc('Logistic Shopee')
		docLogistic.logistic_id = i['logistic_channel_id']
		docLogistic.name1 = i['logistic_channel_name']
		docLogistic.description = i['logistics_description']
		docLogistic.enabled = i['enabled']
		docLogistic.force_enabled = i['force_enabled']
		docLogistic.has_cod = i['cod_enabled']
		docLogistic.mask_channel_id = i['mask_channel_id']
		docLogistic.weight_limit = str(i['weight_limit'])
		docLogistic.item_max_dimention = str(i['item_max_dimension'])
		docLogistic.preferred = i['preferred']
		docLogistic.volume_limit = str(i['volume_limit'])
		docLogistic.save()
	return getLogistic

@frappe.whitelist()
def addDiscount(data):
	data = json.loads(data)

	# get shop
	dataToko = frappe.get_value('Shopee Shop Setting', {'shop_name': data['shop']}, ["shop_id","partner_id","partner_key","shop_name","access_code"])
	shopid = int(dataToko[0])
	partnerid = dataToko[1]
	api_key = dataToko[2]
	access_code = dataToko[4]

	# generate date to epoch timestamp
	endTime = data['time']['end_time']
	startTime = data['time']['start_time']

	# input all data 
	discount_name = data['discount_name']
	start_time = int(epochTime(startTime))
	end_time = int(epochTime(endTime))
	items = data['items']

	shopeeclient = Client(shopid, partnerid, api_key)
	addDiscount = shopeeclient.item.addDiscount(discount_name = discount_name, start_time = start_time, end_time = end_time)#, items = items
	return addDiscount

@frappe.whitelist()
def syncProduct(shop, k):
	shop = json.loads(shop)
	frappe.msgprint(str(shop)+" "+str(k))
	shopid = int(shop['shopid'])
	partnerid = shop['partnerid']
	api_key = shop['api_key']
	access_code = shop['access_code']
	shopeeclient = Client(shopid, partnerid, api_key, access_code)
	allProduct = []
	allDetailProduct = []
	productExist2 = []
	shopeeGetItemList = {
		"items" : []
	}
	#shopeeGetItem = shopeeclient.item.get_item_list(shopid = shopid,pagination_offset = int(k), pagination_entries_per_page = 50,need_deleted_item = False)
	shopeeGetItem = shopeeclient.item.get_item_list(offset = int(k), page_size = 50,item_status = "NORMAL")
	for i in shopeeGetItem['item']:
		shopeeGetItemList['items'].append(i)
	
	# mengambil semua id dari item list
	for i in shopeeGetItemList['items']:
		allProduct.append(i['item_id'])

	# mendapatkan detail dari setiap item
	for j in allProduct :
		shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = j)
		# frappe.throw(str(shopeeGetItemDetail))
		if "item" in shopeeGetItemDetail:
			allDetailProduct.append(shopeeGetItemDetail['item_list'])
	
	return allDetailProduct

	# # membuat item yang tidak ada dahulu
	# for k in allDetailProduct  :
	# 	# check apakah di item sudah ada atau belum
	# 	itemExist = frappe.get_value("Item",{"name" : k['item_sku']}, "name")
	# 	# if itemExist:
	# 	# 	oke = 'oke'
	# 	# else :
	# 	# 	# frappe.throw(k['item_sku'])
	# 	# 	docItem = frappe.new_doc('Item')
	# 	# 	docItem.item_code = k['item_sku']
	# 	# 	docItem.item_name = k['name']
	# 	# 	docItem.item_group = "Shopee"
	# 	# 	docItem.stock_uom ="Pcs"
	# 	# 	docItem.opening_stock = k['stock']
	# 	# 	docItem.standard_rate = k['price']
	# 	# 	docItem.description = k['description']
	# 	# 	docItem.save()


@frappe.whitelist()
def temp_syncProduct():
	shopid = int("466657322")
	partnerid = "2000675"
	api_key = "516579454446565462706e505543517679614371736f456c665a54587a794c45"
	access_code = "6146714768616454565569774c4a6d7a"
	shopeeclient = Client(shopid, partnerid, api_key, access_code)
	allProduct = []
	allDetailProduct = []
	productExist2 = []
	shopeeGetItemList = {
		"items" : []
	}
	#shopeeGetItem = shopeeclient.item.get_item_list(shopid = shopid,pagination_offset = int(k), pagination_entries_per_page = 50,need_deleted_item = False)
	shopeeGetItem = shopeeclient.item.get_item_list(offset = int(0), page_size = 50,item_status = "NORMAL")

	# {'item': [{'item_id': 17269918597, 'item_status': 'NORMAL', 'update_time': 1653274430}, 
	# {'item_id': 21004243242, 'item_status': 'NORMAL', 'update_time': 1653272258},
	 # {'item_id': 13836603177, 'item_status': 'NORMAL', 'update_time': 1635224956}, 
	 # {'item_id': 10243842381, 'item_status': 'NORMAL', 'update_time': 1630465936}], 'total_count': 4, 'has_next_page': False}

	for i in shopeeGetItem['response']['item']:
		shopeeGetItemList['items'].append(i)

	# mengambil semua id dari item list
	for i in shopeeGetItemList['items']:
		allProduct.append(i['item_id'])

	# mendapatkan detail dari setiap item

	shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = allProduct)
	allDetailProduct.append(shopeeGetItemDetail['response']['item_list'])

	return allDetailProduct
"""
{'item_id': 17269918597, 'category_id': 101961, 'item_name': 'HDD SAMSUNG', 'description': 'Berkualitas Tinggi dan tidak mudah rusak', 'item_sku': 'SKU-456', 'create_time': 1653274430, 'update_time': 1653274430, 'attribute_list': [{'attribute_id': 100418, 'original_attribute_name': 'Internal/External', 'is_mandatory': True, 'attribute_value_list': [{'value_id': 2561, 'original_value_name': 'Internal', 'value_unit': ''}]}], 'image': {'image_url_list': ['https://cf.shopee.co.id/file/c4183c26016363f35848e80db55a79ee'], 'image_id_list': ['c4183c26016363f35848e80db55a79ee']}, 'weight': '1.000', 'dimension': {'package_length': 20, 'package_width': 10, 'package_height': 13}, 'logistic_info': [{'logistic_id': 8003, 'logistic_name': 'Reguler', 'enabled': False, 'is_free': False, 'estimated_shipping_fee': 15000}, {'logistic_id': 8001, 'logistic_name': 'Same Day', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 12000}], 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'condition': 'NEW', 'size_chart': '', 'item_status': 'NORMAL', 'has_model': True, 'brand': {'brand_id': 1695294, 'original_brand_name': 'Samsung'}, 'item_dangerous': 0, 'description_type': 'normal'}

 {'tier_variation': [{'name': 'Kapasitas', 'option_list': [{'option': '500 GB', 'image': {'image_id': '0065ee41555e218fb3b9dc8f491e2f9f', 'image_url': 'https://cf.shopee.co.id/file/0065ee41555e218fb3b9dc8f491e2f9f'}}, {'option': '1 TB', 'image': {'image_id': '9d78a3ac63e4d2aa8087bd39a6fd996c', 'image_url': 'https://cf.shopee.co.id/file/9d78a3ac63e4d2aa8087bd39a6fd996c'}}]}], 'model': [{'model_id': 38808798408, 'promotion_id': 0, 'tier_index': [0], 'stock_info': [{'stock_type': 2, 'current_stock': 0, 'normal_stock': 0, 'reserved_stock': 0}, {'stock_type': 1, 'current_stock': 0, 'normal_stock': 0, 'reserved_stock': 0}], 'price_info': [{'current_price': 1000000, 'original_price': 1000000, 'inflated_price_of_current_price': 1000000, 'inflated_price_of_original_price': 1000000}], 'model_sku': 'G-123', 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'stock_info_v2': {'summary_info': {'total_reserved_stock': 0, 'total_available_stock': 0}}}, {'model_id': 38808798409, 'promotion_id': 0, 'tier_index': [1], 'stock_info': [{'stock_type': 2, 'current_stock': 0, 'normal_stock': 0, 'reserved_stock': 0}, {'stock_type': 1, 'current_stock': 0, 'normal_stock': 0, 'reserved_stock': 0}], 'price_info': [{'current_price': 2000000, 'original_price': 2000000, 'inflated_price_of_current_price': 2000000, 'inflated_price_of_original_price': 2000000}], 'model_sku': 'T-123', 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'stock_info_v2': {'summary_info': {'total_reserved_stock': 0, 'total_available_stock': 0}}}]}
"""
@frappe.whitelist()
def test_RunSyncProduct():
	# shop = json.loads(shop)
	item = [{'item_id': 17269918597, 'category_id': 101961, 'item_name': 'HDD SAMSUNG', 'description': 'Berkualitas Tinggi dan tidak mudah rusak', 'item_sku': 'SKU-456', 'create_time': 1653274430, 'update_time': 1653274430, 'attribute_list': [{'attribute_id': 100418, 'original_attribute_name': 'Internal/External', 'is_mandatory': True, 'attribute_value_list': [{'value_id': 2561, 'original_value_name': 'Internal', 'value_unit': ''}]}], 'image': {'image_url_list': ['https://cf.shopee.co.id/file/c4183c26016363f35848e80db55a79ee'], 'image_id_list': ['c4183c26016363f35848e80db55a79ee']}, 'weight': '1.000', 'dimension': {'package_length': 20, 'package_width': 10, 'package_height': 13}, 'logistic_info': [{'logistic_id': 8003, 'logistic_name': 'Reguler', 'enabled': False, 'is_free': False, 'estimated_shipping_fee': 15000}, {'logistic_id': 8001, 'logistic_name': 'Same Day', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 12000}], 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'condition': 'NEW', 'size_chart': '', 'item_status': 'NORMAL', 'has_model': True, 'brand': {'brand_id': 1695294, 'original_brand_name': 'Samsung'}, 'item_dangerous': 0, 'description_type': 'normal'}, {'item_id': 21004243242, 'category_id': 100780, 'item_name': 'Makanan Ringan', 'description': 'Makanan Ringan Manis', 'item_sku': 'SKU-123', 'create_time': 1653272258, 'update_time': 1653272258, 'attribute_list': [{'attribute_id': 100029, 'original_attribute_name': 'Cooked Food Type', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 8, 'original_value_name': 'Braised Dishes', 'value_unit': ''}]}, {'attribute_id': 100974, 'original_attribute_name': 'Ingredient', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': 'Tepung, Gula', 'value_unit': ''}]}, {'attribute_id': 100037, 'original_attribute_name': 'Region of Origin', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 68, 'original_value_name': 'Indonesia', 'value_unit': ''}]}, {'attribute_id': 101050, 'original_attribute_name': 'Storage Condition', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 6231, 'original_value_name': 'Normal', 'value_unit': ''}]}, {'attribute_id': 100030, 'original_attribute_name': 'Cooking Style', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 117, 'original_value_name': 'Chinese', 'value_unit': ''}]}, {'attribute_id': 100095, 'original_attribute_name': 'Weight', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 515, 'original_value_name': '10', 'value_unit': 'g'}]}, {'attribute_id': 100010, 'original_attribute_name': 'Shelf Life', 'is_mandatory': True, 'attribute_value_list': [{'value_id': 580, 'original_value_name': '6 Months', 'value_unit': ''}]}, {'attribute_id': 100963, 'original_attribute_name': 'FDA Registration No.', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': '12323', 'value_unit': ''}]}, {'attribute_id': 100999, 'original_attribute_name': 'Quantity', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': '1', 'value_unit': ''}]}, {'attribute_id': 101029, 'original_attribute_name': 'Pack Size', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': '100', 'value_unit': 'ML'}]}, {'attribute_id': 100061, 'original_attribute_name': 'Expiry Date', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': '1748538000', 'value_unit': ''}]}], 'image': {'image_url_list': ['https://cf.shopee.co.id/file/c4183c26016363f35848e80db55a79ee'], 'image_id_list': ['c4183c26016363f35848e80db55a79ee']}, 'weight': '0.100', 'dimension': {'package_length': 11, 'package_width': 10, 'package_height': 12}, 'logistic_info': [{'logistic_id': 8003, 'logistic_name': 'Reguler', 'enabled': False, 'is_free': False, 'estimated_shipping_fee': 15000}, {'logistic_id': 8001, 'logistic_name': 'Same Day', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 12000}], 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'condition': 'NEW', 'size_chart': '', 'item_status': 'NORMAL', 'has_model': True, 'brand': {'brand_id': 1014576, 'original_brand_name': 'Cadbury Dairy Milk'}, 'item_dangerous': 0, 'description_type': 'normal'}, {'item_id': 13836603177, 'category_id': 101923, 'item_name': 'Laptop Mainan', 'description': 'sdadasdsadasdasdsadsadsadasdasdasdasdasadasdasdasdasaasdas', 'item_sku': 'SKU-LUTFi1', 'create_time': 1635224956, 'update_time': 1635224956, 'price_info': [{'currency': 'IDR', 'original_price': 500000, 'current_price': 500000}], 'stock_info': [{'stock_type': 2, 'current_stock': 19, 'normal_stock': 19, 'reserved_stock': 0}], 'image': {'image_url_list': ['https://cf.shopee.co.id/file/b1a4681fb937f8b4dee42157d552360e'], 'image_id_list': ['b1a4681fb937f8b4dee42157d552360e']}, 'weight': '1.000', 'dimension': {'package_length': 1, 'package_width': 1, 'package_height': 1}, 'logistic_info': [{'logistic_id': 8001, 'logistic_name': 'Same Day', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 12000}, {'logistic_id': 8003, 'logistic_name': 'Reguler', 'enabled': False, 'shipping_fee': 0, 'is_free': False}], 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'condition': 'NEW', 'size_chart': '', 'item_status': 'NORMAL', 'has_model': False, 'promotion_id': 0, 'brand': {'brand_id': 0, 'original_brand_name': 'NoBrand'}, 'item_dangerous': 0, 'description_type': 'normal', 'stock_info_v2': {'summary_info': {'total_reserved_stock': 0, 'total_available_stock': 19}, 'seller_stock': [{'stock': 19}]}}, {'item_id': 10243842381, 'category_id': 100227, 'item_name': 'baju kemeja', 'description': 'bhbbhhhhbhbhbhbhbhbhbhbhbhbh', 'item_sku': 'baju-kemeja-tommy', 'create_time': 1630412466, 'update_time': 1630465936, 'image': {'image_url_list': ['https://cf.shopee.co.id/file/c26ace1a0bd982a3f0727fa869a8f5b6'], 'image_id_list': ['c26ace1a0bd982a3f0727fa869a8f5b6']}, 'weight': '1.000', 'dimension': {'package_length': 10, 'package_width': 10, 'package_height': 10}, 'logistic_info': [{'logistic_id': 8001, 'logistic_name': 'Same Day', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 12000}, {'logistic_id': 8003, 'logistic_name': 'Reguler', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 15000}], 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'condition': 'NEW', 'size_chart': '', 'item_status': 'NORMAL', 'has_model': True, 'brand': {'brand_id': 1014735, 'original_brand_name': 'ARWVS Attitude'}, 'item_dangerous': 0, 'description_type': 'normal'}]

	shopid = int("466657322")
	partnerid = "2000675"
	api_key = "516579454446565462706e505543517679614371736f456c665a54587a794c45"
	access_code = "456375444852596b774a7465636e737a"

	shopeeclient = Client(shopid, partnerid, api_key, access_code)
	allProduct = []
	allDetailProduct = []
	productExist2 = []
	shopeeGetItemList = {
		"items" : []
	}
	alldat = []

	for k in item:
		#print(str(k))
		#json.loads(item)
		# mencari apakah document sudah ada atau belum

		productExist = frappe.get_value("Marketplace Item Shopee",{"shopee_product_id" : k['item_id']}, "name")
		if productExist :
			test = []
			productExist2.append(productExist)
			#shopeeGetItemDetail = shopeeclient.item.get_item_detail(shopid = shopid,item_id = k['item_id'])
			shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
			tries = 0
			while (shopeeGetItemDetail['error'] and tries <= 3):
				time.sleep(2)
				if (shopeeGetItemDetail['message'] == 'Wrong sign.' and tries < 3):
					tries = tries + 1
					shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
				else:
					if (shopeeGetItemDetail['message'] != 'Wrong sign.'):
						print(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
						#frappe.throw(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
						return None
					else:
						print(str("attempts to right the wrong sign 296 failed: ")+str(shopeeGetItemDetail['message']))
						#frappe.throw(str("attempts to right the wrong sign failed: ")+str(shopeeGetItemDetail['message']))
						return None
			#print(str(shopeeGetItemDetail))
			for i in shopeeGetItemDetail['response']['item_list'] :
				test.append(i['item_sku'])

			alldat.append(test)
			# existDoc = frappe.get_doc({
			# 			'doctype': 'Marketplace Item Shopee',
			# 			'name': str(productExist)
			# 		})
			# existDoc.status_sync = 'No'
			# existDoc.db_update()
			# frappe.throw(str(existDoc))
			
		else :
			doc = frappe.new_doc('Marketplace Item Shopee')
			doc.status_sync = 'Yes'
			# doc.shop_name = shop['shop_name']
			doc.shop_name = "Crativate SHOP"
			doc.nama_product = k['item_name']
			
			# memasukkan data ke tabel logistic
			child = frappe.get_list('Logistic Shopee',{'mask_channel_id': '0'}, ['name1','name','mask_channel_id'])
			test = []
			for i in child :
				enable = 0
				childAttribute = doc.append('logistic', {})
				childAttribute.id_logistik = i['name']
				childAttribute.nama_logistik = i['name1']
				for j in k['logistic_info'] :
					if int(j['logistic_id']) == int(i['name']) :
						enable = 1
				childAttribute.enable = enable
				childAttribute.mask_channel_id = 0
				test.append({
					"product name": k['item_sku'],
					"id": i['name'],
					"nama" : i['name1'],
					"enable" : enable ,
					"mask channel" : 0
				})
			
			# status template/product
			# if k['is_2tier_item'] == True :
			# 	doc.type = 'Template'
			# else :
			# 	doc.type = 'Product'

			doc.type = 'Product'

			doc.shopee_product_id = k['item_id']
			doc.item_code = k['item_sku']
			doc.deskripsi_product = k['description']
			doc.category = k['category_id']
			
			# memasukkan attribute
			if ('attribute_list' in k.keys()):
				for l in k['attribute_list'] :
					childAttribute = doc.append('shopee_item_attribute', {})
					childAttribute.attribute_id = l['attribute_id']
					childAttribute.attribute_name = l['original_attribute_name']
					childAttribute.attribute_value = l['attribute_value_list'][0]['value_id']

			doc.condition = k['condition']

			if k['pre_order']['is_pre_order'] == False :
				doc.pre_order ='NO'
			else :
				doc.pre_order ='YES'
			
			doc.status = k['item_status']
			# memasukkan gambar
			for index,i in enumerate(k['image']['image_url_list']) :
				#print(str(i))
				if index == 0 :
					doc.gambar_1 = i#['image_url_list'][index]
				elif index == 1 :
					doc.gambar_2 = i#['image_url_list'][index]
				elif index == 2 :
					doc.gambar_3 = i#['image_url_list'][index]
				elif index == 3 :
					doc.gambar_4 = i#['image_url_list'][index]
				elif index == 4 :
					doc.gambar_5 = i#['image_url_list'][index]
				elif index == 5 :
					doc.gambar_6 = i#['image_url_list'][index]
				elif index == 6:
					doc.gambar_7 = i#['image_url_list'][index]
				elif index == 7 :
					doc.gambar_8 = i#['image_url_list'][index]
			
			
			shopeeGetVariantTier = shopeeclient.item.get_model_list(item_id = k['item_id'])
			tries = 0
			while (shopeeGetVariantTier['error'] and tries <= 3):
				time.sleep(2)
				if (shopeeGetVariantTier['message'] == 'Wrong sign.' and tries < 3):
					tries = tries + 1
					shopeeGetVariantTier = shopeeclient.item.get_model_list(item_id = k['item_id'])
				else:
					if (shopeeGetVariantTier['message'] != 'Wrong sign.'):
						print(str(shopeeGetVariantTier['error'])+", "+str(shopeeGetVariantTier['message']))
						#frappe.throw(str(shopeeGetVariantTier['error'])+", "+str(shopeeGetVariantTier['message']))
						return None
					else:
						print(str("attempts to right the wrong sign 401 failed: ")+str(shopeeGetVariantTier['message']))
						#frappe.throw(str("attempts to right the wrong sign failed: ")+str(shopeeGetVariantTier['message']))
						return None
			#print(str(shopeeGetVariantTier))
			# all options
			if ('tier_variation' in shopeeGetVariantTier['response'].keys()):	
				print(str(len(shopeeGetVariantTier['response']['tier_variation']))+", "+str(shopeeGetVariantTier['response']['tier_variation']))
				if (len(shopeeGetVariantTier['response']['tier_variation']) != 0) :
					option_1 = []
					option_2 = []
					option_im = []
					if (len(shopeeGetVariantTier['response']['tier_variation']) > 1) :
						doc.variant_type_1 = shopeeGetVariantTier['response']['tier_variation'][0]['name']
						if (shopeeGetVariantTier['response']['tier_variation'][1]['name']):
							doc.variant_type_2 = shopeeGetVariantTier['response']['tier_variation'][1]['name']

						# memasukkan data ke child variant 1
						for i in shopeeGetVariantTier['response']['tier_variation'][0]['option_list']:
							option_1.append(i['option'])
							childAttribute = doc.append('variant_1', {})
							childAttribute.nama = i['option']
						
						# memasukkan data ke child variant 2
						if (shopeeGetVariantTier['response']['tier_variation'][1]):
							for i in shopeeGetVariantTier['response']['tier_variation'][1]['option_list']:
								option_2.append(i['option'])
								childAttribute = doc.append('variant_2', {})
								childAttribute.nama = i['option']
						
						# memasukkan data ke child item model
						if ('model' in shopeeGetVariantTier['response'].keys()):
							for i in shopeeGetVariantTier['response']['model']:
								option_im.append(i)
								childAttribute = doc.append('item_model', {})
								childAttribute.tier_index = i['tier_index'][0]
								childAttribute.normal_stock = i['stock_info_v2']['summary_info']['total_available_stock']
								childAttribute.original_price = i['price_info']['current_price']
                                
						lengthAllVar = len(shopeeGetVariantTier['response']['tier_variation'][0]['option_list']) * len(shopeeGetVariantTier['response']['tier_variation'][1]['option_list'])
						
						# untuk get sku variant
						sku = []
						#shopeeGetItemDetail = shopeeclient.item.get_item_detailV1(shopid = shopid,item_id = k['item_id'])
						shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
						tries = 0
						while (shopeeGetItemDetail['error'] and tries <= 3):
							if (shopeeGetItemDetail['message'] == 'Wrong sign.' and tries < 3):
								time.sleep(2)
								tries = tries + 1
								shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
							else:
								if (shopeeGetItemDetail['message'] != 'Wrong sign.'):
									print(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
									#frappe.throw(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
									return None
								else:
									print(str("attempts to right the wrong sign 445 failed: ")+str(shopeeGetItemDetail['message']))
									#frappe.throw(str("attempts to right the wrong sign failed: ")+str(shopeeGetItemDetail['message']))
									return None
						
						for i in shopeeGetItemDetail['response']['item_list'][0]:
							sku.append(i['item_sku'])

						count = -1
						for index1,i in enumerate(option_1):
							for index2,j in enumerate(option_2):
								options = [i, j]
								count = count + 1
								# frappe.msgprint(str(options))
								# frappe.msgprint(str(shopeeGetVariantTier['variations'][count]['variation_id']))
								# frappe.msgprint(str(count))
								# test = [option_1[shopeeGetVariantTier['variations'][i]['tier_index'][0]], option_2[shopeeGetVariantTier['variations'][i]['tier_index'][1]]]
								# frappe.throw(str(shopeeGetVariantTier['variations'][i]['tier_index'][0]))
								# while count < len(shopeeGetVariantTier['variations']):
								childAttribute = doc.append('tabel_gabung_variant', {})
								childAttribute.variant_1 = i
								childAttribute.variant_2 = j
								if ('model_id' in shopeeGetVariantTier['response']['model'].keys()):
									childAttribute.product_id = shopeeGetVariantTier['response']['model']['model_id']
                                    #shopeeGetVariantTier['variations'][count]['variation_id']
								else: childAttribute.product_id = '0'
								childAttribute.indexing_1 = index1
								childAttribute.indexing_2 = index2
								# # childAttribute.refresh_field('tabel_gabung_variant');
								# if count < len(shopeeGetVariantTier['variations']):
								# 	count = count + 1
					else :
						doc.variant_type_1 = shopeeGetVariantTier['response']['tier_variation'][0]['name']
						# frappe.throw(str(shopeeGetVariantTier))
						# memasukkan data ke child variant 1
						for i in shopeeGetVariantTier['response']['tier_variation'][0]['option_list']:
							childAttribute = doc.append('variant_1', {})
							childAttribute.nama = i['option']
						
						lengthAllVar = len(shopeeGetVariantTier['response']['tier_variation'][0]['option_list'])
						
						# untuk get sku variant
						sku = []
						shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
						tries = 0
						while (shopeeGetItemDetail['error'] and tries <= 3):
							if (shopeeGetItemDetail['message'] == 'Wrong sign.' and tries < 3):
								time.sleep(2)
								tries = tries + 1
								shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
							else:
								if (shopeeGetItemDetail['message'] != 'Wrong sign.'):
									print(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
									#frappe.throw(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
									return None
								else:
									print(str("attempts to right the wrong sign 497 failed: ")+str(shopeeGetItemDetail['message']))
									#frappe.throw(str("attempts to right the wrong sign failed: ")+str(shopeeGetItemDetail['message']))
									return None
						for i in shopeeGetItemDetail['response']['item_list']:
							sku.append(i['item_sku'])

						for i in range(int(lengthAllVar) - 2):
							childAttribute = doc.append('tabel_gabung_variant', {})
							childAttribute.variant_1 = shopeeGetVariantTier['response']['tier_variation'][0]['option_list'][i]['option']
							childAttribute.product_id = shopeeGetVariantTier['response']['model'][i]['model_id']#shopeeGetVariantTier['variations'][i]['variation_id']
							childAttribute.indexing_1 = shopeeGetVariantTier['response']['model'][i]['tier_index'][0]#shopeeGetVariantTier['variations'][i]['tier_index'][0]
						#test.append(k['item_sku'])
					alldat.append(shopeeGetVariantTier)

			doc.berat_product = k['weight']
			doc.tinggi_product = k['dimension']['package_height']
			doc.panjang_product = k['dimension']['package_length']
			doc.lebar_product = k['dimension']['package_width']
			
			# allDetailProduct.append('test')
			doc.save()
		
			# allDetailProduct.append('oke')
			# for d in doc.get('logistic', {'nama_logistik': 'Instant'}) :
		# 	# 	d.enable = 1
		#print(str(alldat))
		print('Sync pada '+k['item_name']+' Berhasil!!') 


@frappe.whitelist()
def RunSyncProduct(shop, item):
	# frappe.throw(str(item))
	shop = json.loads(shop)
	shopid = int(shop['shopid'])
	partnerid = shop['partnerid']
	api_key = shop['api_key']
	access_code = shop['access_code']
	shopeeclient = Client(shopid, partnerid, api_key, access_code)
	allProduct = []
	allDetailProduct = []
	productExist2 = []
	shopeeGetItemList = {
		"items" : []
	}
	alldat = []

	k = json.loads(item)
	# mencari apakah document sudah ada atau belum
	productExist = frappe.get_value("Marketplace Item Shopee",{"shopee_product_id" : k['item_id']}, "name")
	if productExist :
		test = []
		productExist2.append(productExist)
		#shopeeGetItemDetail = shopeeclient.item.get_item_detail(shopid = shopid,item_id = k['item_id'])
		shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
		for i in shopeeGetItemDetail['item_list'] :
			test.append(i['item_sku'])

		alldat.append(test)
		# existDoc = frappe.get_doc({
		# 			'doctype': 'Marketplace Item Shopee',
		# 			'name': str(productExist)
		# 		})
		# existDoc.status_sync = 'No'
		# existDoc.db_update()
		# frappe.throw(str(existDoc))
		

	else :
		doc = frappe.new_doc('Marketplace Item Shopee')
		doc.status_sync = 'Yes'
		doc.shop_name = shop['shop_name']
		doc.nama_product = k['name']
		
		# memasukkan data ke tabel logistic
		child = frappe.get_list('Logistic Shopee',{'mask_channel_id': '0'}, ['name1','name','mask_channel_id'])
		test = []
		for i in child :
			enable = 0
			childAttribute = doc.append('logistic', {})
			childAttribute.id_logistik = i['name']
			childAttribute.nama_logistik = i['name1']
			for j in k['logistic_info'] :
				if int(j['logistic_id']) == int(i['name']) :
					enable = 1
			childAttribute.enable = enable
			childAttribute.mask_channel_id = 0
			test.append({
				"product name": k['item_sku'],
				"id": i['name'],
				"nama" : i['name1'],
				"enable" : enable ,
				"mask channel" : 0
			})
		
		# status template/product
		if k['is_2tier_item'] == True :
			doc.type = 'Template'
		else :
			doc.type = 'Product'

		doc.shopee_product_id = k['item_id']
		doc.deskripsi_product = k['description']
		doc.category = k['category_id']
		
		# memasukkan attribute
		for l in k['attributes'] :
			childAttribute = doc.append('shopee_item_attribute', {})
			childAttribute.attribute_id = l['attribute_id']
			childAttribute.attribute_name = l['attribute_name']
			childAttribute.attribute_value = l['attribute_value']

		doc.condition = k['condition']

		if k['is_pre_order'] == False :
			doc.pre_order ='NO'
		else :
			doc.pre_order ='YES'
		
		doc.status = k['status']
		# memasukkan gambar
		for index,i in enumerate(k['image']) :
			if index == 0 :
				doc.gambar_1 = i['image_url_list'][index]
			elif index == 1 :
				doc.gambar_2 = i['image_url_list'][index]
			elif index == 2 :
				doc.gambar_3 = i['image_url_list'][index]
			elif index == 3 :
				doc.gambar_4 = i['image_url_list'][index]
			elif index == 4 :
				doc.gambar_5 = i['image_url_list'][index]
			elif index == 5 :
				doc.gambar_6 = i['image_url_list'][index]
			elif index == 6:
				doc.gambar_7 = i['image_url_list'][index]
			elif index == 7 :
				doc.gambar_8 = i['image_url_list'][index]
		
		if k['is_2tier_item'] == True :
			#shopeeGetVariantTier = shopeeclient.variation.getVariantTier(shopid = shopid,item_id = k['item_id'])
			shopeeGetVariantTier = shopeeclient.item.get_model_list(item_id = k['item_id'])
			# all options
			option_1 = []
			option_2 = []

			if len(shopeeGetVariantTier['tier_variation']) > 1 :
				doc.variant_type_1 = shopeeGetVariantTier['tier_variation'][0]['name']
				doc.variant_type_2 = shopeeGetVariantTier['tier_variation'][1]['name']

				# memasukkan data ke child variant 1
				for i in shopeeGetVariantTier['tier_variation'][0]['option_list']:
					option_1.append(i)
					childAttribute = doc.append('variant_1', {})
					childAttribute.nama = i
				
				# memasukkan data ke child variant 2
				for i in shopeeGetVariantTier['tier_variation'][1]['option_list']:
					option_2.append(i)
					childAttribute = doc.append('variant_2', {})
					childAttribute.nama = i
				
				lengthAllVar = len(shopeeGetVariantTier['tier_variation'][0]['option_list']) * len(shopeeGetVariantTier['tier_variation'][1]['option_list'])
				
				# untuk get sku variant
				#sku = []
				#shopeeGetItemDetail = shopeeclient.item.get_item_detailV1(shopid = shopid,item_id = k['item_id'])
				#for i in shopeeGetItemDetail['item']['variations'] :
				#	sku.append(i['variation_sku'])

				count = -1
				for index1,i in enumerate(option_1):
					for index2,j in enumerate(option_2):
						options = [i, j]
						count = count + 1
						# frappe.msgprint(str(options))
						# frappe.msgprint(str(shopeeGetVariantTier['variations'][count]['variation_id']))
						# frappe.msgprint(str(count))
						# test = [option_1[shopeeGetVariantTier['variations'][i]['tier_index'][0]], option_2[shopeeGetVariantTier['variations'][i]['tier_index'][1]]]
						# frappe.throw(str(shopeeGetVariantTier['variations'][i]['tier_index'][0]))
						# while count < len(shopeeGetVariantTier['variations']):
						childAttribute = doc.append('tabel_gabung_variant', {})
						childAttribute.variant_1 = i
						childAttribute.variant_2 = j
						childAttribute.product_id = shopeeGetVariantTier['model']['model_id']#shopeeGetVariantTier['variations'][count]['variation_id']
						childAttribute.indexing_1 = index1
						childAttribute.indexing_2 = index2
						# # childAttribute.refresh_field('tabel_gabung_variant');
						# if count < len(shopeeGetVariantTier['variations']):
						# 	count = count + 1
					
			else :
				doc.variant_type_1 = shopeeGetVariantTier['tier_variation'][0]['name']
				# frappe.throw(str(shopeeGetVariantTier))
				# memasukkan data ke child variant 1
				for i in shopeeGetVariantTier['tier_variation'][0]['option_list']:
					childAttribute = doc.append('variant_1', {})
					childAttribute.nama = i
				
				lengthAllVar = len(shopeeGetVariantTier['tier_variation'][0]['option_list'])
				
				# untuk get sku variant
				#sku = []
				#shopeeGetItemDetail = shopeeclient.item.get_item_detailV1(shopid = shopid,item_id = k['item_id'])
				#shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
				#for i in shopeeGetItemDetail['item']:
				#	sku.append(i['item_sku'])

				for i in range(int(lengthAllVar) - 2):
					childAttribute = doc.append('tabel_gabung_variant', {})
					childAttribute.variant_1 = shopeeGetVariantTier['tier_variation'][0]['option_list'][i]
					childAttribute.product_id = shopeeGetVariantTier['model']['model_id']#shopeeGetVariantTier['variations'][i]['variation_id']
					childAttribute.indexing_1 = i #shopeeGetVariantTier['variations'][i]['tier_index'][0]
					
			alldat.append(shopeeGetVariantTier)
		doc.berat_product = k['weight']
		doc.tinggi_product = k['package_height']
		doc.panjang_product = k['package_length']
		doc.lebar_product = k['package_width']
		
		# allDetailProduct.append('test')

		doc.save()
	
		# allDetailProduct.append('oke')
		# for d in doc.get('logistic', {'nama_logistik': 'Instant'}) :
	# 	# 	d.enable = 1
	frappe.msgprint('Sync Berhasil!!') 

@frappe.whitelist()
def addOrUpdateVariant(product_data, shop):
	product_data = json.loads(product_data)
	# frappe.throw(str(product_data))
	dataToko = frappe.get_value('Shopee Shop Setting', {'shop_name': shop}, ["shop_id","partner_id","partner_key","shop_name","access_code"])
	shopid = int(dataToko[0])
	partnerid = dataToko[1]
	api_key = dataToko[2]
	shop_name= dataToko[3]
	access_code = dataToko[4]
	shopeeclient = Client(shopid, partnerid, api_key, access_code)
	#shopeeGetItemDetail = shopeeclient.item.get_item_detail(shopid = shopid,item_id = product_data['item_id'])
	shopeeGetItemDetail = shopeeclient.item.get_item_detailV1(item_id_list = product_data['item_id'])

	dataVariation = {
		"item_id": product_data['item_list'],
		"tier_variation" : product_data['attribute_list'],
		"variation" : product_data['variation']
	}
	# frappe.throw(str(dataVariation))
	# dataVariation = {
	# 	"item_id": product_data['item_id'],
	# 	"tier_variation" : [{
	# 		"name": 'warna',
	# 		"options": ['biru','merah']
	# 	},
	# 	{
	# 		"name": 'ukuran',
	# 		"options": ['xl']
	# 	}
	# 	],
	# 	"variation" : [
	# 		{
	# 			"tier_index": [0,0],
	# 			"stock": 10000,
	# 			"price": 100000,
	# 			"variation_sku": 'test'
	# 		},
	# 		{
	# 			"tier_index": [1,0],
	# 			"stock": 10000,
	# 			"price": 100000,
	# 			"variation_sku": 'test'
	# 		}
	# 	]
	# }
	
	
	result = []
	shopeeGetVariantTier = shopeeclient.variation.getVariantTier(shopid = shopid,item_id = product_data['item_id'])
	if ('error' in shopeeGetVariantTier or len(shopeeGetVariantTier['tier_variation']) != len(dataVariation['tier_variation'])) :
		initVariant = shopeeclient.variation.initVariant(shopid = shopid,item_id = product_data['item_id'], tier_variation = dataVariation['tier_variation'], variation = dataVariation['variation'])
		# frappe.msgprint(str(initVariant))
		# if (initVariant['error']) :
		# 	result.append({
		# 		"yang ada di shopee": shopeeGetVariantTier['tier_variation'],
		# 		"yang di erp": dataVariation['tier_variation']
		# 	})
		# else :
		# 	result.append({
		# 		"init": initVariant
		# 	})
		result.append({
					"allVariantAdded": initVariant
				})
	else :
		shopeeUpdateItemVariation = shopeeclient.variation.updateTierVariationList(shopid = shopid,item_id = dataVariation['item_id'], tier_variation = dataVariation['tier_variation'])
		# frappe.throw(str(shopeeUpdateItemVariation))
		varianInShopee = []
		varianInErp = []
		for index,i in enumerate(shopeeGetVariantTier['tier_variation']) :
			temp = []
			for j in i['options'] :
				temp.append(j)
			varianInShopee.append(temp)

		for index,i in enumerate(dataVariation['tier_variation']) :
			temp = []
			for j in i['options'] :
				temp.append(j)
			varianInErp.append(temp)

		# frappe.throw(str(varianInShopee))
		if ('error' in shopeeUpdateItemVariation) :
			#delete index ke 1
			hasil = list(set(varianInShopee[0]) - set(varianInErp[0]))
			finalResult = []
			for index, i in enumerate(shopeeGetVariantTier['tier_variation'][0]['options']) :
				for j in hasil :
					if i == j :
						finalResult.append(index)
			#delete index ke 2
			hasil2 = list(set(varianInShopee[1]) - set(varianInErp[1]))
			finalResult2 = []
			for index, i in enumerate(shopeeGetVariantTier['tier_variation'][1]['options']) :
				for j in hasil2 :
					if i == j :
						finalResult2.append(index)

			# get index 1 to delete
			variationIdToDelete = []
			for index, i in enumerate(shopeeGetVariantTier['variations']) :
				for j in finalResult :
					if i['tier_index'][0] == j :
						variationIdToDelete.append(i['variation_id'])

			# get index 2 to delete
			variationIdToDelete2 = []
			for index, i in enumerate(shopeeGetVariantTier['variations']) :
				for j in finalResult2 :
					if i['tier_index'][1] == j :
						variationIdToDelete2.append(i['variation_id'])

			test = []
			for i in variationIdToDelete :
				deleteVariation =  shopeeclient.variation.delete(shopid = shopid,item_id = product_data['item_id'], variation_id = i)
				test.append({
					"message": deleteVariation
				})

			test2 = []
			for i in variationIdToDelete2 :
				deleteVariation =  shopeeclient.variation.delete(shopid = shopid,item_id = product_data['item_id'], variation_id = i)
				test2.append({
					"message": deleteVariation
				})	
			
			# frappe.throw(str(hasil2))

			# result.append({
			# 	"yang ada di shopee": shopeeGetVariantTier['tier_variation'],
			# 	"yang di erp": dataVariation['tier_variation'],
			# 	"data semua" : shopeeGetVariantTier,
			# 	"coba ": hasil,
			# 	"final result": finalResult,
			# 	"delete variation": variationIdToDelete
			# })
			shopeeGetVariantTierUpdate = shopeeclient.variation.getVariantTier(shopid = shopid,item_id = product_data['item_id'])
			# frappe.throw(str(shopeeGetVariantTier))
			result.append({
					"allVariant": shopeeGetVariantTierUpdate
				})
			frappe.msgprint('Update Variant Berhasil')
		else :
			shopeeGetVariantTierUpdate = shopeeclient.variation.getVariantTier(shopid = shopid,item_id = product_data['item_id'])
			shopeeGetProduct = shopeeclient.item.get_item_detail(shopid = shopid,item_id = product_data['item_id'])
			# addTierVariation =  shopeeclient.variation.addTierVariation(item_id = product_data['item_id'], variation = dataVariation['variation'])
			variations = []
			existIndex = []
			allIndex = []
			addVariations = []

			# getAllindex
			for i in dataVariation['variation'] :
				allIndex.append(i['tier_index'])

			# if len(shopeeGetVariantTierUpdate['variations']) == len(dataVariation['variation']) :
			for i in shopeeGetVariantTierUpdate['variations'] :
				for j in dataVariation['variation'] :
					if i['tier_index'][0] == j['tier_index'][0] and i['tier_index'][1] == j['tier_index'][1] and 'variation_id' in i :
						variations.append({
							"variation_id": i['variation_id'],
							"price": j['price'],
							"item_id": product_data['item_id'],
							"index": j['tier_index'],
							"stock": j['stock']
						})
						existIndex.append(j['tier_index'])
			# else : 

			# frappe.throw(str(dataVariation['variation']))	
			indexNotExist = [x for x in allIndex if x not in existIndex]
			for i in indexNotExist:
				for index,j in enumerate(dataVariation['variation']) :
					if j['tier_index'] == i :
						# frappe.msgprint(str(dataVariation['variation'][index]))
						sku = j['variation_sku']
							
						addVariations.append({
							"price": j['price'],
							"item_id": product_data['item_id'],
							"tier_index": j['tier_index'],
							"stock": j['stock'],
							"variation_sku": sku
						})
						
			batchUpdateStockVariation = shopeeclient.variation.updateVariationStockBatch(shopid = shopid,item_id = product_data['item_id'], variations = variations)
			batchUpdatePriceVariation = shopeeclient.variation.updateVariationPriceBatch(shopid = shopid,item_id = product_data['item_id'], variations = variations)
			addTierVariation = shopeeclient.variation.addTierVariation(shopid = shopid,item_id = product_data['item_id'], variation = addVariations)
			# frappe.msgprint(str(allIndex))
			# frappe.msgprint(str(addTierVariation))
			# # frappe.msgprint(str(shopeeGetVariantTierUpdate['variations']))
			# # frappe.msgprint(str(dataVariation['variation']))
			# # frappe.msgprint(str(batchUpdateStockVariation))
			# frappe.msgprint(str(batchUpdatePriceVariation))
			# frappe.throw(str(indexNotExist))
			if len(batchUpdatePriceVariation['batch_result']['failures']) > 0 :
				# frappe.throw(batchUpdatePriceVariation)
				frappe.throw('Update harga gagal, harga tertinggi yang bisa di gunakan maksimal adalah 7 kali harga terendah dari SKU yang tersedia')
			else :
				shopeeGetVariantTierUpdate2 = shopeeclient.variation.getVariantTier(shopid = shopid,item_id = product_data['item_id'])
				# frappe.throw(str(shopeeGetVariantTierUpdate2))
				result.append({
					"allVariant": shopeeGetVariantTierUpdate2
				})
				frappe.msgprint('Update Variant Berhasil')
		
	# if (shopeeGetItemDetail['item']['has_variation']) :
	# 	initVariant = shopeeclient.variation.initVariant(item_id = product_data['item_id'], tier_variation = dataVariation['tier_variation'], variation = dataVariation['variation'])
	# 	if (initVariant['error'] or initVariant['msg'] == "This item has 2-tier variations structure already and there is no tier_variation level change.") :
	# 	# shopeeGetItemVariation = shopeeclient.variation.getVariantTier(item_id = product_data['item_id'])
	# 		shopeeUpdateItemVariation = shopeeclient.variation.updateTierVariationList(item_id = dataVariation['item_id'], tier_variation = dataVariation['tier_variation'])
	
	return result

@frappe.whitelist()
def updateLogistic(logistic_data, shop_info):
	shop_info = json.loads(shop_info)
	logistic_data = json.loads(logistic_data)

	shopid = int(shop_info['shopid'])
	partnerid = int(shop_info['partnerid'])
	api_key = shop_info['api_key']
	access_code = shop_info['access_code']
	shopeeclient = Client(shopid, partnerid, api_key, access_code)
	result = []
	for i in logistic_data:
		enableCheck = True
		if i['enable'] == 0 :
			enableCheck = False
		shopeeUpdateLogistic = shopeeclient.logistic.update_logistics(logistics_channel_id = int(i['id_logistik']), enabled = enableCheck)
		result.append(shopeeUpdateLogistic)
	return result

@frappe.whitelist()
def deleteProduct(product_data):
	product_data = json.loads(product_data)
	dataToko = frappe.get_value('Shopee Shop Setting', {'shop_name': product_data['shop']}, ["shop_id","partner_id","partner_key","shop_name","access_code"])
	shopid = int(dataToko[0])
	partnerid = dataToko[1]
	api_key = dataToko[2]
	shop_name= dataToko[3]
	access_code= dataToko[4]
	shopeeclient = Client(shopid, partnerid, api_key, access_code)
	deleteShopeeProduct = shopeeclient.item.delete(item_id = product_data['item_id'])

	return deleteShopeeProduct

@frappe.whitelist()
def addProductOrUpdate(product_data):
	product_data = json.loads(product_data)
	
	#mengambil harga product
	price = frappe.db.get_value("Item Price", {"item_code": product_data['item_sku'], "name": product_data['price list']}, "price_list_rate")
	# frappe.throw(str(price))
	# mengambil data stock di warehouse melalui Bin
	totalStock = 0
	tokoShopee = frappe.db.get_list('Bin',{ 'item_code': product_data['item_sku'], "warehouse": product_data['warehouse']}, 'actual_qty')
	for i in tokoShopee:
		totalStock = totalStock + i['actual_qty']

	# mengambil data toko
	toko = []
	dataToko = frappe.get_value('Shopee Shop Setting', {'shop_name': product_data['shop']}, ["shop_id","partner_id","partner_key","shop_name","access_code"])
	toko.append({
		"shopid" : int(dataToko[0]),
		"partnerid" : dataToko[1],
		"api_key" : dataToko[2],
		"shop_name": dataToko[3],
		"access_code": dataToko[4]
	})
	# frappe.msgprint(str(toko))
	resultGetProduct = []
	resultAddProduct = []
	resultUpdateProduct = []
	resultInitVariant = []

	
	# looping untuk melakukan add/update berdasarkan toko yang tersedia
	for k in toko:
		# mengambil data toko
		shopid = int(k['shopid'])
		partnerid = k['partnerid']
		api_key = k['api_key']
		access_code = k['access_code']
		shopeeclient = Client(shopid, partnerid, api_key, access_code)

		# memasukkan data product
		item_id = int(product_data['item_id_shopee'])
		category_id = product_data['category_id']
		name = product_data['name']
		description = product_data['description']
		item_sku = product_data['item_sku']
		images = product_data['images']
		attributes = product_data['attributes']
		logistics = product_data['logistics']
		weight = int(product_data['weight'])
		package_length = int(product_data['package_length'])
		package_width = int(product_data['package_width'])
		package_height = int(product_data['package_height'])
		condition= product_data['condition']
		price= product_data['price']
		status= product_data['status']
		is_pre_order= product_data['is_pre_order']
		days_to_ship= int(product_data['days_to_ship'][0])
		initial_stock= int(product_data['normal_stock'])

		# check apakah produk sudah ada
		shopeeGetProduct = shopeeclient.item.get_item_detail(item_id_list = item_id)
		resultGetProduct.append(shopeeGetProduct)

		#data untuk add product jika tidak pre order
		if is_pre_order[0] == False: 
			product_data_input = {
				"category_id": category_id,
				"item_name": name,
				"description": description,
				"item_sku": item_sku,
				"image": {"image_id_list": images},
				"attribute_list": attributes,
				"logistic_info": logistics,
				"weight": weight,
				"original_price": str(price),
				"normal_stock": initial_stock,
				"dimension":{
				"package_length": package_length[0],
				"package_width": package_width[0],
				"package_height": package_height[0]
				},
				"condition": condition[0],
				"item_status": status[0],
				"pre_order": {"is_pre_order": "false","days_to_ship": 0}
			}
		else :
			#data untuk add product jika pre order
			product_data_input = {
				"category_id": category_id,
				"item_name": name,
				"description": description,
				"item_sku": item_sku,
				"image": {"image_id_list": images},
				"attribute_list": attributes,
				"logistic_info": logistics,
				"weight": weight,
				"original_price": str(price),
				"normal_stock": initial_stock,
				"dimension":{
				"package_length": package_length[0],
				"package_width": package_width[0],
				"package_height": package_height[0]
				},
				"condition": condition[0],
				"item_status": status[0],
				"pre_order": {"is_pre_order": "true",
				"days_to_ship": days_to_ship}
			}

		#data untuk update jika tidak pre order
		if is_pre_order[0] == False: 
			update_data = {
				"item_id": item_id,
				"category_id": category_id,
				"item_name": name,
				"description": description,
				"item_sku": item_sku,
				"image": {"image_id_list": images},
				"attribute_list": attributes,
				"logistic_info": logistics,
				"weight": weight,
				#"price_info": {"current_price": price},
				#"stock": str(totalStock),
				"dimension":{
				"package_length": package_length[0],
				"package_width": package_width[0],
				"package_height": package_height[0]
				},
				"condition": condition[0],
				"item_status": status[0],
				"pre_order": {"is_pre_order": "false","days_to_ship":0}
			}
		else :
			update_data = {
				"item_id": item_id,
				"category_id": category_id,
				"item_name": name,
				"description": description,
				"item_sku": item_sku,
				"image": {"image_id_list": images},
				"attribute_list": attributes,
				"logistics": logistics,
				"weight": weight,
				#"price_info": {"current_price": price},
				#"stock": str(totalStock),
				"dimension":{
				"package_length": package_length[0],
				"package_width": package_width[0],
				"package_height": package_height[0]
				},
				"condition": condition[0],
				"item_status": status[0],
				"is_pre_order": "true",
				"pre_order": {"is_pre_order": "true",
				"days_to_ship": days_to_ship}
			}
		resultInitVariant.append(product_data_input)

		getProductKey = 'item_list'
		if getProductKey in shopeeGetProduct:
			if shopeeGetProduct['item_list']['item_status'] == "DELETED" :
				product_data_input["shopid"] = shopid
				addProduct = shopeeclient.item.add(product_data_shopee = product_data_input)
				resultAddProduct.append(addProduct)
			else :
				# mengambil data image untuk di update
				#imagesUpdate = []
				#for i in images :
				#	imagesUpdate.append(i['url'])
				#if len(imagesUpdate) > 0
				#	update_data.update({"image": images_update})
				#updateProductImage = shopeeclient.item.update_image(shopid = shopid,item_id = item_id, images = imagesUpdate)

				# mengupdate stock
				updateStock = shopeeclient.item.update_stock(item_id = item_id, stock_list = {"normal_stock":str(totalStock)})
				
				# mengupdate harga
				shopeeUpdatePrice = shopeeclient.item.update_price(price_list = {"original_price": str(price)}, item_id = item_id) 

				#update_data["shopid"] = shopid
				updateProduct = shopeeclient.item.update(update_data = update_data)
				# frappe.msgprint(str(updateProduct))
				resultUpdateProduct.append(updateProduct)

				#TESTING ADD VARIANT
				#shopeeGetVariantTier = shopeeclient.variation.getVariantTier(shopid = shopid,item_id = item_id) 
				# if (shopeeGetVariantTier['msg']):
				# 	addVariantInit = shopeeclient.variation.initVariant(item_id = item_id, tier_variation = product_data['tier_variation'], variation = product_data['variation'] )

				# resultUpdateProduct.append(updateProduct)
				# resultInitVariant.append(addVariantInit)
		else :
			product_data_input["shopid"] = shopid
			addProduct = shopeeclient.item.add(product_data_shopee = product_data_input)
			resultAddProduct.append(addProduct)
	
	return {
		"getProduct": resultGetProduct,
		"dataAdd": resultAddProduct,
		"dataUpdate": resultUpdateProduct,
		"initVariant": resultInitVariant
	}

@frappe.whitelist()
def bulkUpdateStock(item_data):
		item_data = json.loads(item_data)
		
		# get toko shopee
		result = []

		shop_name = []
		for x in item_data:
			if x['shop_name'] not in shop_name:
				shop_name.append(x['shop_name'])
		
		result = []
		result_message = []
		for k in shop_name:
			temp = []
			secondTemp = []
			
			for j in item_data:
				if j['shop_name'] == k:
					temp.append({
						"item_id": int(j['product_id']),
						"stock": int(j['new_stock'])
					})
			# temp = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101]
			test = len(temp)
			if test > 50:
				res = test % 50
				sec = test - res
				ges = sec/50
				final = []
				if res > 0:
					first = 0
					last = 0
					for i in range(int(test)):
						if i == 0:
							resultFinal = slice(first,last + 50)
							final.append(temp[resultFinal])
							# final.append([first,last + 50])
							first = first + 50
							last = first + 50
						elif i < ges:
							resultFinal = slice(first,last)
							final.append(temp[resultFinal])
							# final.append([first,last])
							first = first + 50
							last = first + 50
						elif i == ges: 
							resultFinal = slice(first,test)
							final.append(temp[resultFinal])
				else:
					first = 0
					last = 0
					for i in range(int(ges)):

						if i == 0:
							final.append([first,last + 50])
							first = first + 50
							last = first + 50
						elif i < ges:
							final.append([first,last])
							first = first + 50
							last = first + 50
						elif i == ges: 
							final.append([first,test])
				
				for d in final:
					dataToko = frappe.get_value('Shopee Shop Setting', {'shop_name': k}, ["shop_id","partner_id","partner_key","shop_name"])
					shopeeclient = Client(int(dataToko[0]), int(dataToko[1]), dataToko[2])
					shopeeUpdateStock = shopeeclient.product.update_stock_batch(shopid = int(dataToko[0]), items = d)
					if 'batch_result' in shopeeUpdateStock :
						if len(shopeeUpdateStock['batch_result']['failures']) < 1:
							message = ("Update Stock di toko: <b> {} </b> berhasil!".format(dataToko[3]))
							result_message.append(message)
				
			else:
				dataToko = frappe.get_value('Shopee Shop Setting', {'shop_name': k}, ["shop_id","partner_id","partner_key","shop_name"])
				shopeeclient = Client(int(dataToko[0]), int(dataToko[1]), dataToko[2])
				shopeeUpdateStock = shopeeclient.product.update_stock_batch(shopid = int(dataToko[0]), items = temp)
				if 'batch_result' in shopeeUpdateStock :
					if len(shopeeUpdateStock['batch_result']['failures']) < 1:
						message = ("Update Stock di toko: <b> {} </b> berhasil!".format(dataToko[3]))
						result_message.append(message)
						# frappe.msgprint(str(message))
				# initBulkClient(shopid = int(dataToko[0]), partnerid = dataToko[1], api_key = dataToko[2], items = temp, shop_name = dataToko[3])
				# frappe.msgprint(str(initBulkClient))
				# return initBulkClient
		return result_message
		# for (index, value) in enumerate(shop_name):
		# 		dataToko = frappe.get_value('Shopee Shop Setting', {'shop_name': value}, ["shop_id","partner_id","partner_key","shop_name"])
		# 		initBulkClient(shopid = int(dataToko[0]), partnerid = dataToko[1], api_key = dataToko[2], items = result[index], shop_name = dataToko[3])
		# for j in item_data:
		# 	result.append({
		# 		"item_id": int(j['product_id']),
		# 		"stock": int(j['new_stock'])
		# 	})
		# object_dict = dict((x.shop_name, x) for x in item_data)
		
		# for i in item_data:
		# 	dataToko = frappe.get_value('Shopee Shop Setting', {'shop_name': i['shop_name']}, ["shop_id","partner_id","partner_key","shop_name"])
		# 	initBulkClient(shopid = int(dataToko[0]), partnerid = dataToko[1], api_key = dataToko[2], items = result)				
			
@frappe.whitelist()
def initBulkClient(shopid,partnerid,api_key, items, shop_name):
	return 'okeeee'
	# shopeeclient = Client(shopid, int(partnerid), api_key)
	# shopeeUpdateStock = shopeeclient.product.update_stock_batch(shopid = shopid, items = items)
	# # frappe.msgprint(str(shopeeUpdateStock))
	# if 'batch_result' in shopeeUpdateStock :
	# 	if len(shopeeUpdateStock['batch_result']['failures']) < 1:
	# 		message = ("Update Stock di toko: <b> {} </b> berhasil!".format(shop_name))
	# 		return message
	# 		# frappe.msgprint(str(message))
			

@frappe.whitelist()
def initClient(shopid,partnerid,api_key, totalStock, item_id, shop_name):
	shopeeclient = Client(shopid, int(partnerid), api_key)
	shopeeUpdateStock = shopeeclient.item.update_stock(shopid = shopid, stock = int(totalStock), item_id = int(item_id))
	
	if 'item' in shopeeUpdateStock :
		result = "Update Product di Toko: <b> {} </b> dengan Product ID : <b> {} </b> berhasil! \n Stock saat ini: <b> {} </b>".format(shop_name, shopeeUpdateStock['item']['item_id'], shopeeUpdateStock['item']['stock'])
		frappe.msgprint(str(result))
	else:
		frappe.msgprint(str(shopeeUpdateStock))

@frappe.whitelist()
def updateStock(doc, method):
	# mengambil item untuk di ambil item shopeenya
	dataProduct = frappe.db.get_list('Marketplace Item Shopee',{'item_code': doc.item_code , 'warehouse': doc.warehouse},['shopee_product_id', 'shop_name','bobot'])
	data_shop = []
	if len(dataProduct) > 0 :
		newlist = sorted(dataProduct, key=lambda x: x.bobot, reverse=True)
		totalStockProduct = 250
		totalScore = 0
		stockExist = 0
		stockA = []
		for k in dataProduct:
			totalScore = totalScore + k['bobot']
		for index, h in enumerate(newlist):
			if index == (len(dataProduct) - 1) :
				result2 = totalStockProduct - stockExist
				stockA.append(result2)
			else :
				result = (int(h['bobot'])*totalStockProduct) / totalScore
				stockA.append(math.ceil(result))
				stockExist = stockExist + math.ceil(result)

		frappe.msgprint(str(stockA))

		for j in dataProduct: 
			# mengambil toko yang enable_sync untuk di update
			dataTokoSync = frappe.db.get_value('Shopee Shop Setting',
					{
						'store_name': j['shop_name']
					},
					['shop_id','partner_id','partner_key','store_name','access_code']
				)
			# frappe.msgprint(str(dataTokoSync))
			data_shop.append({
				"store_name": dataTokoSync[3],
				"shopid": int(dataTokoSync[0]),
				"partnerid": dataTokoSync[1],
				"api_key": dataTokoSync[2],
				"access_code": dataTokoSync[4]
			})
			shopid = int(dataTokoSync[0])
			partnerid = dataTokoSync[1]
			api_key = dataTokoSync[2]
			access_code = dataTokoSync[4]
			item_id = j['shopee_product_id']
			

			# mengambil data stock di warehouse melalui Bin
			totalStock = 0
			tokoShopee = frappe.db.get_list('Bin',{ 'item_code': doc.item_code, 'warehouse': doc.warehouse}, 'actual_qty')
			
			for i in tokoShopee:
				totalStock = totalStock + i['actual_qty']
			
			# menjalankan update stock
			initClient(shopid, partnerid, api_key, totalStock, item_id)
			
				

@frappe.whitelist()
def updatePrice(doc, method):
	# mengambil toko yang enable_sync untuk di update
	dataTokoSync = frappe.db.get_list('Shopee Shop Setting',
			filters = {
				'enable_sync': 1
			},
			fields = ['*']
		)
	for i in dataTokoSync:
		# mengambil item untuk di ambil item shopeenya
		dataProduct = frappe.db.get_list('Marketplace Item Shopee',{'item_code': doc.item_code, 'price_list': doc.name},['shopee_product_id'])
		for j in dataProduct: 
			shopid = int(i['shop_id'])
			partnerid = i['partner_id']
			api_key = i['partner_key']
			item_id = int(j['shopee_product_id'])

			# mengambil data harga melalui item Price
			newPrice = frappe.db.get_value('Item Price',{ 'item_code': doc.item_code, 'name': doc.name}, 'price_list_rate')
			
			# menjalankan update stock
			shopeeclient = Client(shopid, partnerid, api_key)
			shopeeUpdatePrice = shopeeclient.item.update_price(shopid = shopid,price = int(doc.price_list_rate), item_id = item_id) 
			frappe.msgprint(str(shopeeUpdatePrice))

@frappe.whitelist()
def getListAttribute(test):
	data = frappe.db.get_list('Shopee Attribute',
				filters = {
					'category_id': test
				},
				fields = ['name','attribute_name','attribute_id', 'attribute_value']
			)
	return data

@frappe.whitelist()
def settingShop(dataShop):
	dataShop = json.loads(dataShop)
	# frappe.throw(str(dataShop))

	shopid = int(dataShop['shop_id'])
	partnerid = int(dataShop['partner_id'])
	api_key = str(dataShop['partner_key'])
	access_code = str(dataShop['access_code'])
	shopeeclients = Client(shopid, partnerid, api_key, access_code)
	result = shopeeclients.shop.get_shop_info()#()
	# if result :
	# 	# frappe.msgprint(str(shopCategory))
	# 	# frappe.msgprint(str(shopeeGetLogistic['logistics']))
	# 	# frappe.msgprint(str(shopeeGetItem))
	# 	# frappe.msgprint(str(logistic_data))

	# 	# frappe.msgprint(str(shopeeAttributes['attributes'][0]['options']))
	# 	dataShop.shop_name = result["shop_name"]
	# 	dataShop.shop_region = result["country"]
	# 	dataShop.shop_status = result["status"]
	return result

class ShopeeShopSetting(Document):

	def generate_url_for_shop_id(self):
		if (self.request_type == "Partner Authorization"):
			if not self.partner_id :
				frappe.throw("Partner ID harus diisi")
			if not self.partner_key :
				frappe.throw("Partner Key harus diisi")
			if not self.redirect_url :
				frappe.throw("Redirect URL harus diisi")

			timest = int(time.time())
			host = "https://partner.shopeemobile.com"
			path = "/api/v2/shop/auth_partner"
			#host = "https://partner.test-stable.shopeemobile.com"
			partner_id = self.partner_id
			redirect= self.redirect_url
			partner_key = self.partner_key
			base_string = "%s%s%s"%(partner_id, path, timest)
			sign = hmac.new( partner_key.encode(), base_string.encode() , hashlib.sha256).hexdigest()
			url = str(host+path+"?partner_id={}&timestamp={}&sign={}&redirect={}".format(partner_id, timest, sign, redirect))
			# token = partner_key + base_string
			# sign = hashlib.sha256(token.encode()).hexdigest()
			# url = host+path+"?id={}&redirect={}&token={}".format(partner_id,redirect,hash_token)
			# test_host = "https://partner.uat.shopeemobile.com/api/v1/shop/auth_partner"
			# test_id = 100958
			# test_key = "27fc6a405e1443e4853f9915ef65babb3c60b0dec6cab25450757405e1abb1bf"
			# test_token = hashlib.sha256((test_key+redirect).encode("utf-8")).hexdigest()
			# url = test_host+"?id={}&token={}&redirect={}".format(test_id,test_token,redirect)
			self.url_shop_id = url
			frappe.msgprint(url)
			# resp = requests.get(url)
			# print(resp.content)

		elif (self.request_type == "Get Access Token"):
			if not self.partner_id :
				frappe.throw("Partner ID harus diisi")
			if not self.partner_key :
				frappe.throw("Partner Key harus diisi")
			if not self.redirect_url :
				frappe.throw("Redirect URL harus diisi")
			if not self.shop_id :
				frappe.throw("Shop ID harus diisi")
			if not self.shop_code :
				frappe.throw("Shop Code harus diisi")

			timest = int(time.time())
			host = "https://partner.shopeemobile.com"
			path = "/api/v2/auth/token/get"
			shop_id = self.shop_id
			partner_id = self.partner_id
			redirect= self.redirect_url
			partner_key = self.partner_key
			code = self.shop_code
			base_string = "%s%s%s"%(partner_id, path, timest)
			sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
			url = str(host+path+"?partner_id={}&timestamp={}&sign={}".format(partner_id, timest, sign))
			body = {"code":code, "shop_id":int(shop_id), "partner_id": int(partner_id)}
			headers = { "Content-Type": "application/json"}
			resp = requests.post(url, json=body, headers=headers)
			ret = json.loads(resp.content)
			access_token = ret.get("access_token")
			refresh_token = ret.get("refresh_token")
			# answer = "access token: "+str(access_token)+"\nrefresh token:"+str(refresh_token)
			# answer = answer+"\nThe tokens returns \"None\" that means something is wrong"
			# test_token = hashlib.sha256((test_key+redirect).encode("utf-8")).hexdigest()
			# url = test_host+"?id={}&token={}&redirect={}".format(test_id,test_token,redirect)
			self.url_shop_id = url
			if (access_token != "None"):
				self.access_code = access_token
			if (refresh_token != "None"):
				self.refresh_code = refresh_token
			if (access_token == "None" or refresh_token == "None"):
				frappe.throw("The tokens returns \"None\" that means something is wrong\n"+str(ret))
			else:
				frappe.msgprint(str(ret))

		elif (self.request_type == "Get Token by Resend Code"):
			if not self.partner_id :
				frappe.throw("Partner ID harus diisi")
			if not self.partner_key :
				frappe.throw("Partner Key harus diisi")
			if not self.shop_code :
				frappe.throw("Shop Code harus diisi untuk resend ")
			path = "/api/v2/public/get_token_by_resend_code"
			host = "https://partner.shopeemobile.com"
			timest = int(time.time())
			partner_id = self.partner_id
			partner_key = self.partner_key
			resend_code = self.shop_code
			base_string = partner_id+path+str(timest)+partner_key
			hash_token = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
			url = str(host+path+"?partner_id={}&;timestamp={}&;sign={}".format(partner_id,str(timest),hash_token))
			body = {"resend_code": shop_code}
			headers = { "Content-Type": "application/json"}
			#resp = requests.post(url, headers=headers,json=body,allow_redirects=False)
			resp = requests.post(url, json=body, headers=headers)
			ret = json.loads(resp.content)
			access_token = ret.get("access_token")
			refresh_token = ret.get("refresh_token")
			self.url_shop_id = url
			if (access_token != "None"):
				self.access_code = access_token
			if (refresh_token != "None"):
				self.refresh_code = refresh_token
			if (access_token == "None" or refresh_token == "None"):
				frappe.throw("The tokens returns \"None\" that means something is wrong\n"+str(ret))
			else:
				frappe.msgprint(str(ret))
			
		elif (self.request_type == "Refresh New Access Token"):
			if not self.partner_id :
				frappe.throw("Partner ID harus diisi")
			if not self.partner_key :
				frappe.throw("Partner Key harus diisi")
			if not self.redirect_url :
				frappe.throw("Redirect URL harus diisi")
			if not self.shop_id :
				frappe.throw("Shop ID harus diisi")
			if not self.refresh_code :
				frappe.throw("Refresh Code lama harus diisi")

			timest = int(time.time())
			host = "https://partner.shopeemobile.com"
			path = "/api/v2/auth/access_token/get"
			shop_id = self.shop_id
			partner_id = self.partner_id
			redirect= self.redirect_url
			partner_key = self.partner_key
			refresh_code = self.refresh_code
			base_string = "%s%s%s"%(partner_id, path, timest)
			sign = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
			url = str(host+path+"?partner_id={}&timestamp={}&sign={}".format(partner_id, timest, sign))
			body = {"shop_id":int(shop_id), "refresh_token": refresh_code}
			headers = { "Content-Type": "application/json"}
			resp = requests.post(url, json=body, headers=headers)
			ret = json.loads(resp.content)
			access_token = ret.get("access_token")
			refresh_token = ret.get("refresh_token")
			#answer = "access token: "+str(access_token)+"\nrefresh token:"+str(refresh_token)
			#if (access_token == "None" || refresh_token == "None"):
			#	answer = answer+"\nThe tokens returns \"None\" that means something is wrong"
			# test_token = hashlib.sha256((test_key+redirect).encode("utf-8")).hexdigest()
			# url = test_host+"?id={}&token={}&redirect={}".format(test_id,test_token,redirect)
			self.url_shop_id = url
			if (access_token != "None"):
				self.access_code = access_token
			if (refresh_token != "None"):
				self.refresh_code = refresh_token
			if (access_token == "None" or refresh_token == "None"):
				frappe.throw("The tokens returns \"None\" that means something is wrong\n"+str(ret))
			else:
				frappe.msgprint(str(ret))
		
	def refresh_upgrade_code_manual():
		timest = int(time.time())
		path = "/api/v2/public/get_refresh_token_by_upgrade_code"
		host = "https://partner.test-stable.shopeemobile.com"
		partner_id = "1000266"
		partner_key = "70ab0e8d1b587697ebf4ad6321e3c48ea867156dfa08c29003cf5f5e65b0a3db"
		base_string = partner_id+path+str(timest)+partner_key
		hash_token = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
		url = host+path+"?partner_id={}&amp;timestamp={}&amp;sign={}".format(partner_id,str(timest),hash_token)
		#url = "https://partner.uat.shopeemobile.com/api/v2/public/get_refresh_token_by_upgrade_code?partner_id=partner_id&sign=sign&timestamp=timestamp"
		payload=json.dumps({
		"shop_id_list": [
			"466657322"
			],
			"upgrade_code": "6866614657666462597041574d7a756650656d565271755858524352697a6765"
			})
		headers = {
			'Content-Type': 'application/json'
			}
		response = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
		print(response.text)

	# def validate(self):
	# 	# if self.enable_sync :
	# 	# 	if self.shop_id and self.partner_id and self.partner_key :
	# 	# 		shopid = int(self.shop_id)
	# 	# 		partnerid = int(self.partner_id)
	# 	# 		api_key = str(self.partner_key)
	# 	# 		shopeeclients = Client(shopid, partnerid, api_key)
	# 	# 		shopeeCategory = shopeeclients.item.get_categories(language="id")
	# 	# 		result = shopeeclients.shop.get_shop_info()
	# 	# 		frappe.msgprint(str(result))
	# 	# 		if result :
	# 	# 			# frappe.msgprint(str(shopCategory))
	# 	# 			# frappe.msgprint(str(shopeeGetLogistic['logistics']))
	# 	# 			# frappe.msgprint(str(shopeeGetItem))
	# 	# 			# frappe.msgprint(str(logistic_data))

	# 	# 			# frappe.msgprint(str(shopeeAttributes['attributes'][0]['options']))
	# 	# 			self.shop_name = result["shop_name"]
	# 	# 			self.shop_region = result["country"]
	# 	# 			self.shop_status = result["status"]



@frappe.whitelist()
def test_RunSyncProduct2():
	# shop = json.loads(shop)
	item = [{'item_id': 17269918597, 'category_id': 101961, 'item_name': 'HDD SAMSUNG', 'description': 'Berkualitas Tinggi dan tidak mudah rusak', 'item_sku': 'SKU-456', 'create_time': 1653274430, 'update_time': 1653274430, 'attribute_list': [{'attribute_id': 100418, 'original_attribute_name': 'Internal/External', 'is_mandatory': True, 'attribute_value_list': [{'value_id': 2561, 'original_value_name': 'Internal', 'value_unit': ''}]}], 'image': {'image_url_list': ['https://cf.shopee.co.id/file/c4183c26016363f35848e80db55a79ee'], 'image_id_list': ['c4183c26016363f35848e80db55a79ee']}, 'weight': '1.000', 'dimension': {'package_length': 20, 'package_width': 10, 'package_height': 13}, 'logistic_info': [{'logistic_id': 8003, 'logistic_name': 'Reguler', 'enabled': False, 'is_free': False, 'estimated_shipping_fee': 15000}, {'logistic_id': 8001, 'logistic_name': 'Same Day', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 12000}], 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'condition': 'NEW', 'size_chart': '', 'item_status': 'NORMAL', 'has_model': True, 'brand': {'brand_id': 1695294, 'original_brand_name': 'Samsung'}, 'item_dangerous': 0, 'description_type': 'normal'}, {'item_id': 21004243242, 'category_id': 100780, 'item_name': 'Makanan Ringan', 'description': 'Makanan Ringan Manis', 'item_sku': 'SKU-123', 'create_time': 1653272258, 'update_time': 1653272258, 'attribute_list': [{'attribute_id': 100029, 'original_attribute_name': 'Cooked Food Type', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 8, 'original_value_name': 'Braised Dishes', 'value_unit': ''}]}, {'attribute_id': 100974, 'original_attribute_name': 'Ingredient', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': 'Tepung, Gula', 'value_unit': ''}]}, {'attribute_id': 100037, 'original_attribute_name': 'Region of Origin', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 68, 'original_value_name': 'Indonesia', 'value_unit': ''}]}, {'attribute_id': 101050, 'original_attribute_name': 'Storage Condition', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 6231, 'original_value_name': 'Normal', 'value_unit': ''}]}, {'attribute_id': 100030, 'original_attribute_name': 'Cooking Style', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 117, 'original_value_name': 'Chinese', 'value_unit': ''}]}, {'attribute_id': 100095, 'original_attribute_name': 'Weight', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 515, 'original_value_name': '10', 'value_unit': 'g'}]}, {'attribute_id': 100010, 'original_attribute_name': 'Shelf Life', 'is_mandatory': True, 'attribute_value_list': [{'value_id': 580, 'original_value_name': '6 Months', 'value_unit': ''}]}, {'attribute_id': 100963, 'original_attribute_name': 'FDA Registration No.', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': '12323', 'value_unit': ''}]}, {'attribute_id': 100999, 'original_attribute_name': 'Quantity', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': '1', 'value_unit': ''}]}, {'attribute_id': 101029, 'original_attribute_name': 'Pack Size', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': '100', 'value_unit': 'ML'}]}, {'attribute_id': 100061, 'original_attribute_name': 'Expiry Date', 'is_mandatory': False, 'attribute_value_list': [{'value_id': 0, 'original_value_name': '1748538000', 'value_unit': ''}]}], 'image': {'image_url_list': ['https://cf.shopee.co.id/file/c4183c26016363f35848e80db55a79ee'], 'image_id_list': ['c4183c26016363f35848e80db55a79ee']}, 'weight': '0.100', 'dimension': {'package_length': 11, 'package_width': 10, 'package_height': 12}, 'logistic_info': [{'logistic_id': 8003, 'logistic_name': 'Reguler', 'enabled': False, 'is_free': False, 'estimated_shipping_fee': 15000}, {'logistic_id': 8001, 'logistic_name': 'Same Day', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 12000}], 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'condition': 'NEW', 'size_chart': '', 'item_status': 'NORMAL', 'has_model': True, 'brand': {'brand_id': 1014576, 'original_brand_name': 'Cadbury Dairy Milk'}, 'item_dangerous': 0, 'description_type': 'normal'}, {'item_id': 13836603177, 'category_id': 101923, 'item_name': 'Laptop Mainan', 'description': 'sdadasdsadasdasdsadsadsadasdasdasdasdasadasdasdasdasaasdas', 'item_sku': 'SKU-LUTFi1', 'create_time': 1635224956, 'update_time': 1635224956, 'price_info': [{'currency': 'IDR', 'original_price': 500000, 'current_price': 500000}], 'stock_info': [{'stock_type': 2, 'current_stock': 19, 'normal_stock': 19, 'reserved_stock': 0}], 'image': {'image_url_list': ['https://cf.shopee.co.id/file/b1a4681fb937f8b4dee42157d552360e'], 'image_id_list': ['b1a4681fb937f8b4dee42157d552360e']}, 'weight': '1.000', 'dimension': {'package_length': 1, 'package_width': 1, 'package_height': 1}, 'logistic_info': [{'logistic_id': 8001, 'logistic_name': 'Same Day', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 12000}, {'logistic_id': 8003, 'logistic_name': 'Reguler', 'enabled': False, 'shipping_fee': 0, 'is_free': False}], 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'condition': 'NEW', 'size_chart': '', 'item_status': 'NORMAL', 'has_model': False, 'promotion_id': 0, 'brand': {'brand_id': 0, 'original_brand_name': 'NoBrand'}, 'item_dangerous': 0, 'description_type': 'normal', 'stock_info_v2': {'summary_info': {'total_reserved_stock': 0, 'total_available_stock': 19}, 'seller_stock': [{'stock': 19}]}}, {'item_id': 10243842381, 'category_id': 100227, 'item_name': 'baju kemeja', 'description': 'bhbbhhhhbhbhbhbhbhbhbhbhbhbh', 'item_sku': 'baju-kemeja-tommy', 'create_time': 1630412466, 'update_time': 1630465936, 'image': {'image_url_list': ['https://cf.shopee.co.id/file/c26ace1a0bd982a3f0727fa869a8f5b6'], 'image_id_list': ['c26ace1a0bd982a3f0727fa869a8f5b6']}, 'weight': '1.000', 'dimension': {'package_length': 10, 'package_width': 10, 'package_height': 10}, 'logistic_info': [{'logistic_id': 8001, 'logistic_name': 'Same Day', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 12000}, {'logistic_id': 8003, 'logistic_name': 'Reguler', 'enabled': True, 'is_free': False, 'estimated_shipping_fee': 15000}], 'pre_order': {'is_pre_order': False, 'days_to_ship': 2}, 'condition': 'NEW', 'size_chart': '', 'item_status': 'NORMAL', 'has_model': True, 'brand': {'brand_id': 1014735, 'original_brand_name': 'ARWVS Attitude'}, 'item_dangerous': 0, 'description_type': 'normal'}]

	shopid = int("466657322")
	partnerid = "2000675"
	api_key = "516579454446565462706e505543517679614371736f456c665a54587a794c45"
	access_code = "456375444852596b774a7465636e737a"
	
	shopeeclient = Client(shopid, partnerid, api_key, access_code)

	bs = str(shopeeclient.partner_id)+str("/api/v2/product/get_model_list")+str(shopeeclient.timestamp)+str(shopeeclient.access_token)+str(shopeeclient.shop_id)
	hash_token = hmac.new( shopeeclient.secret_key.encode(), bs.encode(), hashlib.sha256).hexdigest()
	print("1:{}".format(str(hash_token)))


	allProduct = []
	allDetailProduct = []
	productExist2 = []
	shopeeGetItemList = {
		"items" : []
	}
	alldat = []

	for k in item:
		#print(str(k))
		#json.loads(item)
		# mencari apakah document sudah ada atau belum

		productExist = frappe.get_value("Marketplace Item Shopee",{"shopee_product_id" : k['item_id']}, "name")
		if productExist :
			test = []
			productExist2.append(productExist)
			#shopeeGetItemDetail = shopeeclient.item.get_item_detail(shopid = shopid,item_id = k['item_id'])
			shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
			tries = 0
			while (shopeeGetItemDetail['error']):
				time.sleep(2)
				if (shopeeGetItemDetail['message'] == 'Wrong sign.'):
					test_RunSyncProduct2()
					tries = tries + 1
					shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
				else:
					if (shopeeGetItemDetail['message'] != 'Wrong sign.'):
						print(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
						#frappe.throw(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
						return None
					else:
						print(str("attempts to right the wrong sign 296 failed: ")+str(shopeeGetItemDetail['message']))
						#frappe.throw(str("attempts to right the wrong sign failed: ")+str(shopeeGetItemDetail['message']))
						return None
			#print(str(shopeeGetItemDetail))
			for i in shopeeGetItemDetail['response']['item_list'] :
				test.append(i['item_sku'])

			alldat.append(test)

		else :
			doc = frappe.new_doc('Marketplace Item Shopee')
			doc.status_sync = 'Yes'
			doc.shop_name = "Crativate SHOP"
			doc.nama_product = k['item_name']
			
			# memasukkan data ke tabel logistic
			child = frappe.get_list('Logistic Shopee',{'mask_channel_id': '0'}, ['name1','name','mask_channel_id'])
			test = []
			for i in child :
				enable = 0
				childAttribute = doc.append('logistic', {})
				childAttribute.id_logistik = i['name']
				childAttribute.nama_logistik = i['name1']
				for j in k['logistic_info'] :
					if int(j['logistic_id']) == int(i['name']) :
						enable = 1
				childAttribute.enable = enable
				childAttribute.mask_channel_id = 0
				test.append({
					"product name": k['item_sku'],
					"id": i['name'],
					"nama" : i['name1'],
					"enable" : enable ,
					"mask channel" : 0
				})
			

			doc.type = 'Product'

			doc.shopee_product_id = k['item_id']
			doc.deskripsi_product = k['description']
			doc.category = k['category_id']
			
			# memasukkan attribute
			if ('attribute_list' in k.keys()):
				for l in k['attribute_list'] :
					childAttribute = doc.append('shopee_item_attribute', {})
					childAttribute.attribute_id = l['attribute_id']
					childAttribute.attribute_name = l['original_attribute_name']
					childAttribute.attribute_value = l['attribute_value_list'][0]['value_id']

			doc.condition = k['condition']

			if k['pre_order']['is_pre_order'] == False :
				doc.pre_order ='NO'
			else :
				doc.pre_order ='YES'
			
			doc.status = k['item_status']
			# memasukkan gambar
			for index,i in enumerate(k['image']['image_url_list']) :
				#print(str(i))
				if index == 0 :
					doc.gambar_1 = i#['image_url_list'][index]
				elif index == 1 :
					doc.gambar_2 = i#['image_url_list'][index]
				elif index == 2 :
					doc.gambar_3 = i#['image_url_list'][index]
				elif index == 3 :
					doc.gambar_4 = i#['image_url_list'][index]
				elif index == 4 :
					doc.gambar_5 = i#['image_url_list'][index]
				elif index == 5 :
					doc.gambar_6 = i#['image_url_list'][index]
				elif index == 6:
					doc.gambar_7 = i#['image_url_list'][index]
				elif index == 7 :
					doc.gambar_8 = i#['image_url_list'][index]
			
			shopeeclient = Client(shopid, partnerid, api_key, access_code)
			shopeeGetVariantTier = shopeeclient.item.get_model_list(item_id = k['item_id'])
			tries = 0
			while (shopeeGetVariantTier['error'] and tries <= 3):
				
				if (shopeeGetVariantTier['message'] == 'Wrong sign.'):
					tries = tries + 1
					shopeeclient = Client(shopid, partnerid, api_key, access_code)
					shopeeGetVariantTier = shopeeclient.item.get_model_list(item_id = k['item_id'])
				else:
					if (shopeeGetVariantTier['message'] != 'Wrong sign.'):
						print(str(shopeeGetVariantTier['error'])+", "+str(shopeeGetVariantTier['message']))
						#frappe.throw(str(shopeeGetVariantTier['error'])+", "+str(shopeeGetVariantTier['message']))
						return None
					else:
						# print(str("attempts to right the wrong sign 401 failed: ")+str(shopeeGetVariantTier['message']))
						print(str(shopeeGetVariantTier))
						#frappe.throw(str("attempts to right the wrong sign failed: ")+str(shopeeGetVariantTier['message']))
						return None
			print("Success")
			# pass
		# 	if ('tier_variation' in shopeeGetVariantTier['response'].keys()):	
		# 		print(str(len(shopeeGetVariantTier['response']['tier_variation']))+", "+str(shopeeGetVariantTier['response']['tier_variation']))
		# 		if (len(shopeeGetVariantTier['response']['tier_variation']) != 0) :
		# 			option_1 = []
		# 			option_2 = []
		# 			option_im = []
		# 			if (len(shopeeGetVariantTier['response']['tier_variation']) > 1) :
		# 				doc.variant_type_1 = shopeeGetVariantTier['response']['tier_variation'][0]['name']
		# 				if (shopeeGetVariantTier['response']['tier_variation'][1]['name']):
		# 					doc.variant_type_2 = shopeeGetVariantTier['response']['tier_variation'][1]['name']

		# 				# memasukkan data ke child variant 1
		# 				for i in shopeeGetVariantTier['response']['tier_variation'][0]['option_list']:
		# 					option_1.append(i['option'])
		# 					childAttribute = doc.append('variant_1', {})
		# 					childAttribute.nama = i['option']
						
		# 				# memasukkan data ke child variant 2
		# 				if (shopeeGetVariantTier['response']['tier_variation'][1]):
		# 					for i in shopeeGetVariantTier['response']['tier_variation'][1]['option_list']:
		# 						option_2.append(i['option'])
		# 						childAttribute = doc.append('variant_2', {})
		# 						childAttribute.nama = i['option']
						
		# 				# memasukkan data ke child item model
		# 				if ('model' in shopeeGetVariantTier['response'].keys()):
		# 					for i in shopeeGetVariantTier['response']['model']:
		# 						option_im.append(i)
		# 						childAttribute = doc.append('item_model', {})
		# 						childAttribute.tier_index = i['tier_index'][0]
		# 						childAttribute.normal_stock = i['stock_info_v2']['summary_info']['total_available_stock']
		# 						childAttribute.original_price = i['price_info']['current_price']
                                
		# 				lengthAllVar = len(shopeeGetVariantTier['response']['tier_variation'][0]['option_list']) * len(shopeeGetVariantTier['response']['tier_variation'][1]['option_list'])
						
		# 				# untuk get sku variant
		# 				sku = []
		# 				#shopeeGetItemDetail = shopeeclient.item.get_item_detailV1(shopid = shopid,item_id = k['item_id'])
		# 				shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
		# 				tries = 0
		# 				while (shopeeGetItemDetail['error'] and tries <= 3):
		# 					if (shopeeGetItemDetail['message'] == 'Wrong sign.' and tries < 3):
		# 						time.sleep(2)
		# 						tries = tries + 1
		# 						shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
		# 					else:
		# 						if (shopeeGetItemDetail['message'] != 'Wrong sign.'):
		# 							print(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
		# 							#frappe.throw(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
		# 							return None
		# 						else:
		# 							print(str("attempts to right the wrong sign 445 failed: ")+str(shopeeGetItemDetail['message']))
		# 							#frappe.throw(str("attempts to right the wrong sign failed: ")+str(shopeeGetItemDetail['message']))
		# 							return None
						
		# 				for i in shopeeGetItemDetail['response']['item_list'][0]:
		# 					sku.append(i['item_sku'])

		# 				count = -1
		# 				for index1,i in enumerate(option_1):
		# 					for index2,j in enumerate(option_2):
		# 						options = [i, j]
		# 						count = count + 1
		# 						# frappe.msgprint(str(options))
		# 						# frappe.msgprint(str(shopeeGetVariantTier['variations'][count]['variation_id']))
		# 						# frappe.msgprint(str(count))
		# 						# test = [option_1[shopeeGetVariantTier['variations'][i]['tier_index'][0]], option_2[shopeeGetVariantTier['variations'][i]['tier_index'][1]]]
		# 						# frappe.throw(str(shopeeGetVariantTier['variations'][i]['tier_index'][0]))
		# 						# while count < len(shopeeGetVariantTier['variations']):
		# 						childAttribute = doc.append('tabel_gabung_variant', {})
		# 						childAttribute.variant_1 = i
		# 						childAttribute.variant_2 = j
		# 						if ('model_id' in shopeeGetVariantTier['response']['model'].keys()):
		# 							childAttribute.product_id = shopeeGetVariantTier['response']['model']['model_id']
  #                                   #shopeeGetVariantTier['variations'][count]['variation_id']
		# 						else: childAttribute.product_id = '0'
		# 						childAttribute.indexing_1 = index1
		# 						childAttribute.indexing_2 = index2
		# 						# # childAttribute.refresh_field('tabel_gabung_variant');
		# 						# if count < len(shopeeGetVariantTier['variations']):
		# 						# 	count = count + 1
		# 			else :
		# 				doc.variant_type_1 = shopeeGetVariantTier['response']['tier_variation'][0]['name']
		# 				# frappe.throw(str(shopeeGetVariantTier))
		# 				# memasukkan data ke child variant 1
		# 				for i in shopeeGetVariantTier['response']['tier_variation'][0]['option_list']:
		# 					childAttribute = doc.append('variant_1', {})
		# 					childAttribute.nama = i['option']
						
		# 				lengthAllVar = len(shopeeGetVariantTier['response']['tier_variation'][0]['option_list'])
						
		# 				# untuk get sku variant
		# 				sku = []
		# 				shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
		# 				tries = 0
		# 				while (shopeeGetItemDetail['error'] and tries <= 3):
		# 					if (shopeeGetItemDetail['message'] == 'Wrong sign.' and tries < 3):
		# 						time.sleep(2)
		# 						tries = tries + 1
		# 						shopeeGetItemDetail = shopeeclient.item.get_item_detail(item_id_list = k['item_id'])
		# 					else:
		# 						if (shopeeGetItemDetail['message'] != 'Wrong sign.'):
		# 							print(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
		# 							#frappe.throw(str(shopeeGetItemDetail['error'])+", "+str(shopeeGetItemDetail['message']))
		# 							return None
		# 						else:
		# 							print(str("attempts to right the wrong sign 497 failed: ")+str(shopeeGetItemDetail['message']))
		# 							#frappe.throw(str("attempts to right the wrong sign failed: ")+str(shopeeGetItemDetail['message']))
		# 							return None
		# 				for i in shopeeGetItemDetail['response']['item_list']:
		# 					sku.append(i['item_sku'])

		# 				for i in range(int(lengthAllVar) - 2):
		# 					childAttribute = doc.append('tabel_gabung_variant', {})
		# 					childAttribute.variant_1 = shopeeGetVariantTier['response']['tier_variation'][0]['option_list'][i]['option']
		# 					childAttribute.product_id = shopeeGetVariantTier['response']['model'][i]['model_id']#shopeeGetVariantTier['variations'][i]['variation_id']
		# 					childAttribute.indexing_1 = shopeeGetVariantTier['response']['model'][i]['tier_index'][0]#shopeeGetVariantTier['variations'][i]['tier_index'][0]
		# 				#test.append(k['item_sku'])
		# 			alldat.append(shopeeGetVariantTier)

		# 	doc.berat_product = k['weight']
		# 	doc.tinggi_product = k['dimension']['package_height']
		# 	doc.panjang_product = k['dimension']['package_length']
		# 	doc.lebar_product = k['dimension']['package_width']
			
		# 	# allDetailProduct.append('test')
		# 	doc.save()
		
		# 	# allDetailProduct.append('oke')
		# 	# for d in doc.get('logistic', {'nama_logistik': 'Instant'}) :
		# # 	# 	d.enable = 1
		# #print(str(alldat))
		# print('Sync pada '+k['item_name']+' Berhasil!!') 




