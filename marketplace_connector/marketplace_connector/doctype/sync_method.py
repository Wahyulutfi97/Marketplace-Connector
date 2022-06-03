# -*- coding: utf-8 -*-
# Copyright (c) 2015, erpx and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from marketplace_connector.marketplace_connector.doctype.frappeclient import FrappeClient
from marketplace_connector.marketplace_connector.doctype.shopee_shop_setting.shopee_connector.client import Client

# from woocommerce_setting.woocommerce import API

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
from frappe import utils

import hmac
import time
import hashlib
import requests


class SyncMethod(Document):
	pass


# datetime.datetime.strptime(s, "%d/%m/%Y").timestamp()

# utils.now()
# utils.today()

# add_days(date, days);   // add n days to a date
# frappe.datetime.add_months(date, months); // add n months to a date
# frappe.datetime.month_end(date);  // returns the first day from the month of the given date
# frappe.datetime.month_start(date); // returns the last day from the month of the given date
# frappe.datetime.get_day_diff(begin, end); // returns the days between 2 dates


# frappe.db.get_value(“Global Defaults”, None, “default_company”)
# frappe.db.get_single_value("Global Defaults", "default_company")

# enqueue("styling.sync_method.sync_so_po", doc=doc,sync_doc=sync_form,supplier=customer_check[0][1])



# wcapi = API(
#	 url="http://example.com",
#	 consumer_key="ck_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
#	 consumer_secret="cs_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
#	 version="wc/v3"
# )

# woocommerce order status
# Options: pending, processing, on-hold, completed, cancelled, refunded, failed and trash



@frappe.whitelist()
def shopee_get_category():
	shopid = int("466657322")
	partnerid = int("2000675")
	api_key = str("516579454446565462706e505543517679614371736f456c665a54587a794c45")
	shopeeclient = Client(shopid, partnerid, api_key)

	shopeeCategory = shopeeclient.item.get_categories()

	frappe.throw(str(shopeeCategory))

@frappe.whitelist()
def shopee_authorize_token(shop_setting):
	shopid = int("466657322")
	partnerid = int("2000675")
	api_key = str("516579454446565462706e505543517679614371736f456c665a54587a794c45")
	shopeeclient = Client(shopid, partnerid, api_key)

	shopeeCategory = shopeeclient.item.get_categories()

	frappe.throw(str(shopeeCategory))

@frappe.whitelist()
def generate_access_token_4_hours(shop_setting):
	
	timest = int(time.time())
	path = "/api/v2/public/get_token_by_resend_code"
	host = "https://partner.shopeemobile.com"
	code = shop_setting.refresh_code
	partner_id = 2000675
	redirect="https://devahok.crativate.com/"
	partner_key = "516579454446565462706e505543517679614371736f456c665a54587a794c45"
	base_string = "%s%s%s"%(partner_id, str(timest), partner_key)
	hash_token = hmac.new( partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
	body = {"resend_code":code}
	headers = { "Content-Type": "application/json"}
	url = host + path + "?partner_id={}&timestamp={}&sign={}".format(partner_id, timest, hash_token)
	resp = requests.post(url, json=body, headers=headers)
	ret = json.loads(resp.content)
	if (not resp.error):
		shop_setting.access_code = ret.get("access_token")
		shop_setting.refresh_code = ret.get("refresh_token")
	else: 
		frappe.throw(resp.error)

@frappe.whitelist()
def get_refresh_token():
	# # def api1 generator url
	timest = int(time.time())
	get_store = frappe.db.sql("""
		SELECT sss.`name` FROM `tabShopee Shop Setting` sss
		WHERE sss.`enable_sync` = 1
	""")
	if get_store :
		for gs in get_store :
			shop_setting = frappe.get_doc("Shopee Shop Setting", gs[0])
			if (refresh_token):
				generate_access_token_4_hours(shop_setting)

@frappe.whitelist()
def generate_url_untuk_order_id():
	# # def api1 generator url
	timest = int(time.time())
	path = "/api/v2/shop/auth_partner"
	host = "https://partner.shopeemobile.com"
	partner_id = 2000675
	# partner_id = 3863
	redirect="https://devahok.crativate.com/"
	partner_key = "516579454446565462706e505543517679614371736f456c665a54587a794c45"
	token = partner_key+redirect
	hash_token = hashlib.sha256(token.encode()).hexdigest()
	url = host+path+"?id={}&redirect={}&token={}".format(partner_id,redirect,hash_token)

	# test_host = "https://partner.uat.shopeemobile.com/api/v2/shop/auth_partner"
	# test_id = 100958
	# test_key = "27fc6a405e1443e4853f9915ef65babb3c60b0dec6cab25450757405e1abb1bf"
	# test_token = hashlib.sha256((test_key+redirect).encode("utf-8")).hexdigest()
	# url = test_host+"?id={}&token={}&redirect={}".format(test_id,test_token,redirect)
	# print(url)
	# resp = requests.get(url)
	# print(resp.content)


@frappe.whitelist()
def hourly_get_marketplace_orders():

	# ambil semua store yang enable
	get_store = frappe.db.sql("""
		SELECT sss.`name` FROM `tabShopee Shop Setting` sss
		WHERE sss.`enable_sync` = 1
	""")

	if get_store :
		for gs in get_store :
			shopee_setting = frappe.get_doc("Shopee Shop Setting", gs[0])
			if shopee_setting.sync_berapa_hari == "1 hari" :
				today_date = utils.today()
				enqueue("marketplace_connector.marketplace_connector.doctype.sync_method.enqueue_marketplace_orders", date=today_date, shop_setting = gs[0])

			elif shopee_setting.sync_berapa_hari == "2 hari" :
				today_date = utils.today()
				enqueue("marketplace_connector.marketplace_connector.doctype.sync_method.enqueue_marketplace_orders", date=today_date, shop_setting = gs[0])

				before_date = str(add_days(utils.today(), -1))
				enqueue("marketplace_connector.marketplace_connector.doctype.sync_method.enqueue_marketplace_orders", date=before_date, shop_setting = gs[0])

			elif shopee_setting.sync_berapa_hari == "3 hari" :
				today_date = utils.today()
				enqueue("marketplace_connector.marketplace_connector.doctype.sync_method.enqueue_marketplace_orders", date=today_date, shop_setting = gs[0])

				before_date = str(add_days(utils.today(), -1))
				enqueue("marketplace_connector.marketplace_connector.doctype.sync_method.enqueue_marketplace_orders", date=before_date, shop_setting = gs[0])

				before_before_date = str(add_days(utils.today(), -2))
				enqueue("marketplace_connector.marketplace_connector.doctype.sync_method.enqueue_marketplace_orders", date=before_before_date, shop_setting = gs[0])



@frappe.whitelist()
def enqueue_marketplace_orders(date=None, shop_setting=None):
	count = 0
	time_from = 0
	time_to = 0
	curr_date = date
	today = str(curr_date)
	day_sebelumnya = str(add_days(curr_date, -1));
	today_morning = day_sebelumnya + " 23:59:59"
	today_evening = today + " 23:59:59"
	today_morning_woo = today + "T00:00:00"
	today_evening_woo = today + "T23:59:59"

	time_from = int(time.mktime(datetime.datetime.strptime(str(today_morning), "%Y-%m-%d %H:%M:%S").timetuple()))
	time_to = int(time.mktime(datetime.datetime.strptime(str(today_evening), "%Y-%m-%d %H:%M:%S").timetuple()))

	# check setting
	shopee_setting = frappe.get_doc("Shopee Shop Setting", shop_setting)
	if shopee_setting.enable_sync :

		# get credential
		shopid = int(shopee_setting.shop_id)
		partnerid = int(shopee_setting.partner_id)
		api_key = str(shopee_setting.partner_key)
		shopeeclient = Client(shopid, partnerid, api_key)

		# di looping 5x
		pagination_entry = 100
		pagination_offset = 0
		temp_continue = True

		for looping in range(25) :
			if temp_continue == False :
				# frappe.throw(str("result"))
				break

			elif temp_continue == True :
				result = shopeeclient.order.get_order_list(shopid = shopid, create_time_from = time_from, create_time_to = time_to, pagination_entries_per_page = pagination_entry, pagination_offset = pagination_offset)
				# frappe.throw(str(result))

				if result["orders"] :
					
					for i in result["orders"] :

						print(str(i["ordersn"]))

						# cari dulu apakah ada
						get_morder = frappe.get_value("Marketplace Orders", {"name" : i["ordersn"]}, "name")

						# ada
						if get_morder :

							get_marketplace_order = frappe.get_doc("Marketplace Orders", get_morder)

							if get_marketplace_order.order_status != i["order_status"] :

								get_docu = frappe.get_doc("Marketplace Orders", i["ordersn"])
								get_docu.order_status = i["order_status"]

								get_docu.shop_name = shopee_setting.shop_name
								get_docu.shop_setting = shopee_setting.name

								child_result = shopeeclient.order.get_order_detail(shopid = shopid,ordersn_list = [i["ordersn"]])
								if child_result["orders"] :
									for a in child_result["orders"] :
										get_docu.shipping_carrier = a["shipping_carrier"]
										get_docu.tracking_no = a["tracking_no"]
										get_docu.days_to_ship = a["days_to_ship"]

								get_docu.flags.ignore_permission = True
								get_docu.save()


						# tidak ada
						else :
							new_docu = frappe.new_doc("Marketplace Orders")
							new_docu.marketplace = "Shopee"
							new_docu.order_id = i["ordersn"]
							new_docu.order_status = i["order_status"]

							new_docu.shop_name = shopee_setting.shop_name
							new_docu.shop_setting = shopee_setting.name

							new_docu.posting_date = curr_date


							child_result = shopeeclient.order.get_order_detail(shopid = shopid,ordersn_list = [i["ordersn"]])
							result_escrow = shopeeclient.order.get_order_escrow_detail(shopid = shopid,ordersn = i["ordersn"])
							if child_result["orders"] :
								for a in child_result["orders"] :
									new_docu.customer = a["buyer_username"]
									new_docu.customer_name = a["recipient_address"]["name"].replace(">","").replace("<","").replace("'","").replace('"',"")
									alamat_penerima = a["recipient_address"]["full_address"]
									patokan = ", ID,"
									if patokan in alamat_penerima :
										new_docu.recipient_address = alamat_penerima.replace(", ID,", ", Indonesia,")
									else :
										new_docu.recipient_address = alamat_penerima
									# new_docu.recipient_address = "Indonesia"
									new_docu.recipient_phone = a["recipient_address"]["phone"]
									new_docu.recipient_city = a["recipient_address"]["city"]
									new_docu.note = a["message_to_seller"]
									new_docu.total_amount = a["total_amount"]
									new_docu.currency = a["currency"]
									new_docu.shipping_carrier = a["shipping_carrier"]
									new_docu.tracking_no = a["tracking_no"]
									new_docu.days_to_ship = a["days_to_ship"]
									
									variant_sku = ""
									item_sku = ""
									additional_discount = 0
									jumlah_item = 0
									jumlah_setelah_diskon = 0
									jumlah_sebelum_diskon = 0
									total_sebelum_diskon = 0
									total_setelah_diskon = 0
									harga_item_setelah_diskon = 0
									array_harga_itemnya = {}
									array_qty_itemnya = {}
									for j in a["items"] :
										
										if j["promotion_type"] == "bundle_deal" :
											if j["variation_sku"] :
												item_sku = str(j["variation_sku"])
											else :
												item_sku = str(j["item_sku"])
											if result_escrow["order"]["activity"] :
												for actv in result_escrow["order"]["activity"] :
													for a_item in actv["items"] :
														if str(a_item["item_id"]) == str(j["item_id"]) :
															harga_item_setelah_diskon = float(a_item["original_price"])
														jumlah_item += float(a_item["quantity_purchased"])
													total_sebelum_diskon = float(actv["original_price"])
													total_setelah_diskon = float(actv["discounted_price"])
													additional_discount = total_sebelum_diskon - total_setelah_diskon
												
												new_child = new_docu.append("items", {})
												new_child.item_sku = str(item_sku)
												new_child.item_name = j["item_name"]
												new_child.variant = j["variation_name"]
												new_child.qty = str(j["variation_quantity_purchased"])
												new_child.price_list_rate = str(j["variation_original_price"])
												new_child.rate = str(harga_item_setelah_diskon)

												new_docu.additional_discount = additional_discount
										else :
											
											if j["variation_sku"] :
												item_sku = str(j["variation_sku"])
											else :
												item_sku = str(j["item_sku"])
											
											new_child = new_docu.append("items", {})
											new_child.item_sku = str(item_sku)
											new_child.item_name = j["item_name"]
											new_child.variant = j["variation_name"]
											new_child.qty = str(j["variation_quantity_purchased"])
											new_child.price_list_rate = str(j["variation_original_price"])
											new_child.rate = str(j["variation_discounted_price"])

							new_docu.flags.ignore_permission = True
							new_docu.save()

				temp_continue = result["more"]
				pagination_offset += 100
		frappe.msgprint('sync berhasil')


@frappe.whitelist()
def create_sinv_marketplace_orders(doc, method):

	status = True
	dataItemOrder = frappe.get_list('Marketplace Orders Item', {'parent': doc.name}, ["item_sku"])
	
	for m in dataItemOrder:
		if status:
			item_check = frappe.get_list("Item", {'item_code': m['item_sku']} )
			if len(item_check) > 0:
				pass
			else:
				status = False
		else:
			pass
	
	count = 0
	shopee_setting = frappe.get_doc("Shopee Shop Setting", doc.shop_setting)

	shopid = int(shopee_setting.shop_id)
	partnerid = shopee_setting.partner_id
	api_key = shopee_setting.partner_key
	shopeeclient = Client(shopid, partnerid, api_key)

	if doc.order_status == "READY_TO_SHIP" or doc.order_status == "COMPLETED" or doc.order_status == "SHIPPED" or doc.order_status == "TO_CONFIRM_RECEIVE" :
		

		
		cari_data_invoice = frappe.get_value("Sales Invoice", {"marketplace_id" : doc.order_id}, "name")
		if cari_data_invoice :
			frappe.db.sql(""" UPDATE `tabSales Invoice` sinv SET sinv.`nomor_resi` = "{}", sinv.`kurir` = "{}" WHERE sinv.`name` = "{}" """.format(str(doc.tracking_no),str(doc.shipping_carrier), str(cari_data_invoice)))
			frappe.db.commit()

			doc.status_sync = "Berhasil"
			doc.sinv_no = cari_data_invoice

		else :

			try :
				# cek customer
				cari_data_customer = frappe.get_value("Customer", str(doc.customer_name).strip()+" - ("+str(doc.customer).strip()+")", "name")
				if cari_data_customer :
					# customer sudah terdaftar
					count = 0
				else :
					
					
					# create new customer
					new_cust = frappe.new_doc("Customer")
					new_cust.customer_group = str(shopee_setting.customer_group)
					new_cust.customer_name = str(doc.customer_name).strip()+" - ("+str(doc.customer).strip()+")"
					
					new_cust.territory = "All Territories"
					new_cust.customer_type = "Individual"
					new_cust.flags.ignore_permission = True
					new_cust.save()
					# frappe.throw("masuk create customer")
					
					# create new address
					new_add = frappe.new_doc("Address")
					new_add.address_title = str(doc.customer_name).strip()+" - ("+str(doc.customer).strip()+")"
					new_add.address_type = "Personal"
					new_add.address_line1 = doc.recipient_address
					new_add.city = doc.recipient_city
					new_add.country = "Indonesia"
					new_add.is_primary_address = 1
					new_add.phone = doc.recipient_phone
					new_add.links = []
					add_child = new_add.append('links', {})
					add_child.link_doctype = "Customer"
					add_child.link_name = str(doc.customer_name).strip()+" - ("+str(doc.customer).strip()+")"
					new_add.flags.ignore_permission = True
					new_add.save()


				# create sales invoice
				customer_name = str(doc.customer_name).strip()+" - ("+str(doc.customer).strip()+")"

				# edit SO 
				if shopee_setting.make_so == 1 :
					cek_so = frappe.get_value("Sales Order",{"marketplace_id": doc.order_id}, "name")
					if cek_so:
						check = 'oke'
					else:
						today = date.today()
						docSO = frappe.new_doc('Sales Order')
						docSO.customer = customer_name
						docSO.order_type = 'Sales'
						docSO.delivery_date = add_days(today, +3)
						docSO.marketplace = 'Shopee'
						docSO.shop_name = doc.shop_name
						docSO.marketplace_id = doc.order_id

						for item in doc.items:
							row = docSO.append('items', {})
							row.item_code = item.item_sku
							row.qty = float(item.qty)
						
						docSO.flags.ignore_permission=True
						docSO.save()
						doc.so_no = docSO.name
				if status:
					new_sales_order = frappe.new_doc("Sales Invoice")

					new_sales_order.customer = customer_name
					new_sales_order.customer_group = str(shopee_setting.customer_group)
					new_sales_order.update_stock = 1
					new_sales_order.set_posting_time = 1
					new_sales_order.order_via = "Shopee"
					new_sales_order.ignore_pricing_rule = 1

					new_sales_order.posting_date = doc.posting_date
					new_sales_order.naming_series = "SINV-"
					new_sales_order.marketplace = "Shopee"
					new_sales_order.marketplace_id = doc.order_id
					new_sales_order.nomor_resi = doc.tracking_no
					new_sales_order.kurir = doc.shipping_carrier
					new_sales_order.shop_name = doc.shop_name


					# new_sales_order.delivery_date = order_delivery_date
					default_set_company = frappe.get_doc("Global Defaults")
					company = default_set_company.default_company
					found_company = frappe.get_doc("Company",{"name":company})
					company_abbr = found_company.abbr

					new_sales_order.company = company

					for item in doc.items:

						# cari data item
						cari_data_item = frappe.get_value("Item", {"name" : item.item_sku}, "name")
						if not cari_data_item :

							if shopee_setting.create_new_item == 1 :

								new_item = frappe.new_doc("Item")
								new_item.item_code = item.item_sku
								new_item.item_name = item.item_name
								new_item.description = item.item_name

								get_stock_setting = frappe.get_single("Stock Settings")

								if shopee_setting.default_uom :
									new_item.stock_uom = shopee_setting.default_uom
								else :
									new_item.stock_uom = get_stock_setting.stock_uom

								if shopee_setting.default_item_group :
									new_item.item_group = shopee_setting.default_item_group
								else :
									new_item.item_group = get_stock_setting.item_group

								new_item.flags.ignore_permissions = True
								new_item.save()

						new_sales_order.append("items",{
							"item_code": str(item.item_sku),
							"item_name": str(item.item_name),
							"qty": float(item.qty),
							"rate": float(item.rate),
							"price_list_rate": float(item.price_list_rate),
							"warehouse": shopee_setting.warehouse
						})

					## get data escrow
					# print(i.order_id)
					result_escrow = shopeeclient.order.get_order_escrow_detail(shopid = int(shopid),ordersn = doc.order_id)
					test_res = {
						shopid,
						partnerid,
						api_key
					}
					# frappe.throw(str(result_escrow))
					if result_escrow :
						actual_shipping_fee = 0
						shipping_fee_rebate = 0
						voucher_seller = 0

						ship_fee = 0

						new_array_escrow = result_escrow["order"]["income_details"]

						if float(new_array_escrow["actual_shipping_cost"]) != 0 :
							actual_shipping_fee = float(new_array_escrow["actual_shipping_cost"]) * -1
							shipping_fee_rebate = float(new_array_escrow["shipping_fee_rebate"])

							ship_fee = actual_shipping_fee - shipping_fee_rebate

						voucher_seller = float(new_array_escrow["voucher_seller"])

						doc.estimated_shipping_fee = ship_fee
						doc.voucher_applied = voucher_seller

						# penambahan additional discount
						if doc.additional_discount :
							voucher_seller = voucher_seller + float(doc.additional_discount)

						# ongkir
						if doc.estimated_shipping_fee > 0 :
							new_sales_order.append("taxes",{
								"charge_type": "Actual",
								"account_head": shopee_setting.shipping_account,
								"description" : "Ongkos Kirim",
								"tax_amount" : float(doc.estimated_shipping_fee)

							})

						new_sales_order.apply_discount_on = "Grand Total"
						new_sales_order.discount_amount = float(voucher_seller)
						new_sales_order.base_discount_amount = float(voucher_seller)

					new_sales_order.flags.ignore_permission = True
					new_sales_order.save()

					doc.sinv_no = new_sales_order.name
					
					doc.status_sync = "Berhasil"

			except frappe.exceptions.ValidationError as err :

				doc.status_sync = "Gagal"
				frappe.throw(str(err))

								
		





@frappe.whitelist(allow_guest = True)
def get_shopee_logistic():

	# frappe.throw(str(get_url()))

	shopee_setting = frappe.get_single("Shopee Setting")
	shopid = int(shopee_setting.shop_id)
	partnerid = int(shopee_setting.partner_id)
	api_key = str(shopee_setting.partner_key)

	shopeeclient = Client(shopid, partnerid, api_key)

	result = shopeeclient.logistic.get_logistics(shopid = shopid)

	# frappe.throw(str(result["categories"]))

	count = 0
	if result["logistics"] :

		for i in result["logistics"] :
			# frappe.throw(str(i["has_children"]))

			if i["enabled"] == True :
				
				cek_logistic = frappe.get_value("Shopee Logistic", str(i["logistic_id"]), "name")

				if cek_logistic : 
					count = 0
				else :
					new_cat = frappe.new_doc("Shopee Logistic")
					new_cat.logistic_id = str(i["logistic_id"])
					new_cat.logistic_name = i["logistic_name"]
					new_cat.flags.ignore_permission = True
					new_cat.save()



@frappe.whitelist(allow_guest = True)
def get_shopee_item_category_child():

	# frappe.throw(str(get_url()))

	shopee_setting = frappe.get_single("Shopee Setting")
	shopid = int(shopee_setting.shop_id)
	partnerid = int(shopee_setting.partner_id)
	api_key = str(shopee_setting.partner_key)

	shopeeclient = Client(shopid, partnerid, api_key)

	result = shopeeclient.item.get_categories(shopid = shopid,language = "en")

	# frappe.throw(str(result["categories"]))

	count = 0
	if result["categories"] :

		for i in result["categories"] :
			# frappe.throw(str(i["has_children"]))

			if i["has_children"] == False :
				
				cek_category_id = frappe.get_value("Shopee Item Category", str(i["category_id"]), "name")

				if cek_category_id : 
					count = 0
				else :
					new_cat = frappe.new_doc("Shopee Item Category")
					new_cat.category_id = str(i["category_id"])
					new_cat.category_name = i["category_name"]
					new_cat.flags.ignore_permission = True
					new_cat.save()



@frappe.whitelist(allow_guest = True)
def get_shop_id_shopee():
	shopee_setting = frappe.get_single("Shopee Setting")
	shopid = int(shopee_setting.shop_id)
	partnerid = int(shopee_setting.partner_id)
	api_key = str(shopee_setting.partner_key)

	shopeeclient = Client(shopid, partnerid, api_key)

	result = shopeeclient.shop.get_shop_info(shopid = shopid,)

	frappe.throw(str(result))




@frappe.whitelist(allow_guest = True)
def add_item_test():

	# frappe.msgprint("Test jalan")

	doc = frappe.get_doc("Item", "SPT SNEAKERS")

	if doc.share_shopee :

		if doc.gambar_pertama :

			if doc.shopee_item_id :
				count = 0

				# frappe.throw("salah masuk")
			else :
	
				count = 0
				# check setting
				shopee_setting = frappe.get_single("Shopee Setting")
				# woocommerce_setting = frappe.get_single("Woocommerce Setting")

				if shopee_setting.enable_sync :

					# frappe.throw("masuk sini")

					# shopee category
					if doc.shopee_item_category :
						count = 0
					else :
						frappe.throw("Please Choose Shopee Category")

					# shopee weight
					if doc.weight_per_unit > 0 :
						count = 0
					else :
						frappe.throw("Please Input Weight of Unit")

					# shopee rate
					if doc.standard_rate > 0 :
						count = 0
					else :
						frappe.throw("Please Input Standard Selling Rate")

					# shopee brand
					if doc.brand :
						count = 0
					else :
						frappe.throw("Please Input Brand")


					# shopee logistic
					if doc.shopee_logistic :
						count = 0
					else :
						frappe.throw("Please Input Shopee Logistic")

					# panjang description
					panjang_description = len(doc.description)
					if panjang_description > 3000 :
						frappe.throw("Description More than 3000 words")
					if panjang_description < 20 :
						frappe.throw("Description Less than 20 words")


					# # kondisi sudah terpenuhi
					category_id = int(doc.shopee_item_category)
					name = doc.item_name
					description = doc.description
					
					price = doc.standard_rate
					stock = 1
					item_sku = doc.item_code
					img_url = str(get_url()) + str(doc.gambar_pertama)
					images = [{ "url" : img_url }]
					brand_shopee_id = frappe.get_doc("Brand", doc.brand).brand_id_shopee
					attributes = [{"attributes_id" : int(brand_shopee_id), "value" : doc.brand}]
					logistics = []
					for i in doc.shopee_logistic :
						logistics.append({"logistic_id": int(i.logistic_id), "enabled": True})
					weight = doc.weight_per_unit
					days_to_ship = 2
					wholesales = []
					if doc.shopee_wholesales :
						for i in doc.shopee_wholesales :
							wholesales.append({ "min": int(i.min_qty), "max": int(i.max_qty), "unit_price" : i.price_per_unit })
					condition = "NEW"

					# wholesales or not
					array_data = {}
					if doc.shopee_wholesales :
						array_data = {
							"category_id": category_id,
							"name": name,
							"description": description,
							"price": price,
							"stock": stock,
							"item_sku": item_sku,
							"images": images,
							"attributes": attributes,
							"logistics": logistics,
							"weight": weight,
							"days_to_ship": days_to_ship,
							"wholesales": wholesales,
							"condition": condition
						}
					else :
						array_data = {
							"category_id": category_id,
							"name": name,
							"description": description,
							"price": price,
							"stock": stock,
							"item_sku": item_sku,
							"images": images,
							"attributes": attributes,
							"logistics": logistics,
							"weight": weight,
							"days_to_ship": days_to_ship,
							"condition": condition
						}

					# check setting
					shopee_setting = frappe.get_single("Shopee Setting")

					if shopee_setting.enable_sync :

						# get credential
						shopid = int(shopee_setting.shop_id)
						partnerid = int(shopee_setting.partner_id)
						api_key = str(shopee_setting.partner_key)
						shopeeclient = Client(shopid, partnerid, api_key)

						result = shopeeclient.item.add(shopid = shopid,product_data = array_data)

						frappe.throw(result)



@frappe.whitelist(allow_guest = True)
def add_item_to_marketplace(doc,method):

	# frappe.msgprint("Test jalan")

	if doc.share_shopee :

		if doc.gambar_pertama :

			if doc.shopee_item_id == "" :
	
				count = 0
				# check setting
				shopee_setting = frappe.get_single("Shopee Setting")
				# woocommerce_setting = frappe.get_single("Woocommerce Setting")

				if shopee_setting.enable_sync :

					# shopee category
					if doc.shopee_item_category :
						count = 0
					else :
						frappe.throw("Please Choose Shopee Category")

					# shopee weight
					if doc.weight_per_unit > 0 :
						count = 0
					else :
						frappe.throw("Please Input Weight of Unit")

					# shopee rate
					if doc.strandard_rate > 0 :
						count = 0
					else :
						frappe.throw("Please Input Standard Selling Rate")

					# shopee brand
					if doc.brand :
						count = 0
					else :
						frappe.throw("Please Input Brand")


					# shopee logistic
					if doc.shopee_logistic :
						count = 0
					else :
						frappe.throw("Please Input Shopee Logistic")


					# # kondisi sudah terpenuhi
					category_id = doc.shopee_item_category
					name = doc.item_name
					description = doc.description
					price = doc.strandard_rate
					stock = 0
					item_sku = doc.item_code
					img_url = str(get_url()) + str(doc.gambar_pertama)
					images = [{ "url" : img_url }]
					brand_shopee_id = frappe.get_doc("Brand", doc.brand).brand_id_shopee
					attributes = [{"attributes_id" : brand_shopee_id, "value" : doc.brand}]
					logistics = []
					for i in doc.shopee_logistic :
						logistics.append({"logistic_id": i.logistic_id, "enabled": True})
					weight = doc.weight_per_unit
					days_to_ship = 2
					wholesales = []
					if doc.shopee_wholesales :
						for i in doc.shopee_wholesales :
							wholesales.append({ "min": i.min_qty, "max": i.max_qty, "unit_price" : i.price_per_unit })
					condition = "NEW"

					# wholesales or not
					array_data = {}
					if doc.shopee_wholesales :
						array_data = {
							"category_id": category_id,
							"name": name,
							"description": description,
							"price": price,
							"stock": stock,
							"item_sku": item_sku,
							"images": images,
							"attributes": attributes,
							"logistics": logistics,
							"weight": weight,
							"days_to_ship": days_to_ship,
							"wholesales": wholesales,
							"condition": condition
						}
					else :
						array_data = {
							"category_id": category_id,
							"name": name,
							"description": description,
							"price": price,
							"stock": stock,
							"item_sku": item_sku,
							"images": images,
							"attributes": attributes,
							"logistics": logistics,
							"weight": weight,
							"days_to_ship": days_to_ship,
							"condition": condition
						}

					# check setting
					shopee_setting = frappe.get_single("Shopee Setting")

					if shopee_setting.enable_sync :

						# get credential
						shopid = int(shopee_setting.shop_id)
						partnerid = int(shopee_setting.partner_id)
						api_key = str(shopee_setting.partner_key)
						shopeeclient = Client(shopid, partnerid, api_key)

						result = shopeeclient.item.add(shopid = shopid,product_data = array_data)

						frappe.throw(result)



	
	






