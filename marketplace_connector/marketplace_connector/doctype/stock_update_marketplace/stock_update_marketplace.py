# -*- coding: utf-8 -*-
# Copyright (c) 2021, PT DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class StockUpdateMarketplace(Document):
	pass
	# def on_submit(self):
	# 	if self.marketplace == "Tokopedia":
	# 		# frappe.msgprint("coba")
	# 		for d in self.get('item_stock_tokopedia'):
	# 			isi=[]
	# 			app_id = frappe.get_value("Tokopedia Setting",{"name": self.tokopedia_toko}, "app_id")
	# 			token = frappe.get_value("Tokopedia Setting",{"name": self.tokopedia_toko}, "token")
	# 			shop_id = frappe.get_value("Tokopedia Setting",{"name": self.tokopedia_toko}, "shop_id")
	# 			data = Product.get_product_info_sku(app_id,d.item,token)
	# 			total = data['data'][0]['stock']['value'] + d.diff_stock
	# 			ds = {
	# 				"sku": d.item,
	# 				"new_stock": int(total)
	# 			}
	# 			isi.append(ds)
	# 			# frappe.msgprint(str(isi))
	# 			Price.update_stock(app_id,shop_id,token,isi)

	# def on_cancel(self):
	# 	if self.marketplace == "Tokopedia":
	# 		# frappe.msgprint("coba")
	# 		for d in self.get('item_stock_tokopedia'):
	# 			isi=[]
	# 			app_id = frappe.get_value("Tokopedia Setting",{"name": self.tokopedia_toko}, "app_id")
	# 			token = frappe.get_value("Tokopedia Setting",{"name": self.tokopedia_toko}, "token")
	# 			shop_id = frappe.get_value("Tokopedia Setting",{"name": self.tokopedia_toko}, "shop_id")
	# 			data = Product.get_product_info_sku(app_id,d.item,token)
	# 			total = data['data'][0]['stock']['value'] - d.diff_stock
	# 			ds = {
	# 				"sku": d.item,
	# 				"new_stock": int(total)
	# 			}
	# 			isi.append(ds)
	# 			# frappe.msgprint(str(isi))
	# 			Price.update_stock(app_id,shop_id,token,isi)
