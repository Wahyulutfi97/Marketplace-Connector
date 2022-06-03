# -*- coding: utf-8 -*-
# Copyright (c) 2021, PT DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

import os
import requests
import json
import subprocess
import datetime

# mengambil order per 5 menit
@frappe.whitelist()
def sync_per_5_menit():
	# mengambil tanggal hari ini
	today = datetime.datetime.today().strftime('%Y-%m-%d')

	# toko yang di ambil adalah toko yang enable _sync nya di centang
	dataToko = frappe.get_list('Shopee Shop Setting', {'enable_sync': 1}, ["shop_id","partner_id","partner_key","shop_name"])
	for i in dataToko:

		# mengambil tanggal dan nama toko 
		tanggal_sync = today
		store_name = i.shop_name
		marketplace = 'Shopee'

		sitename = str(frappe.utils.get_url()).replace("https://", "").replace("http://", "").replace("/","")

		# frappe.throw(sitename)

		os.chdir("/home/hok/erp/frappe-bench")
		os.system(""" bench --site {} execute marketplace_connector.marketplace_connector.doctype.sync_method.enqueue_marketplace_orders --kwargs '{{"date":"{}", "shop_setting":"{}"}}' """.format(sitename, tanggal_sync, store_name))

class SyncManual(Document):
	
	def sync_manual(self):
		if not self.tanggal_sync :
			frappe.throw("Tanggal Sync belum dipilih")

		if not self.marketplace :
			frappe.throw("Marketplace belum dipilih")

		if not self.store_name :
			frappe.throw("Store Name belum dipilih")

		sitename = str(frappe.utils.get_url()).replace("https://", "").replace("http://", "").replace("/","")

# 		# frappe.throw(sitename)

		os.chdir("/home/hok/erp/frappe-bench")
		os.system(""" bench --site {} execute marketplace_connector.marketplace_connector.doctype.sync_method.enqueue_marketplace_orders --kwargs '{{"date":"{}", "shop_setting":"{}"}}' """.format(sitename, self.tanggal_sync, self.store_name))

		