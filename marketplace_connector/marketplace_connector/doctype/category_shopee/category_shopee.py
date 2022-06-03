# -*- coding: utf-8 -*-
# Copyright (c) 2021, PT DAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CategoryShopee(Document):

	def validate(self):
		pass
		# row = self.append('shopee_attributes', {})
		# row.attribute_id = "test"
		# row.attribute_name = "oke"
		# row.attribute_value = 'tommy\ntimmy'
		# frappe.msgprint(self.meta.get_field(fieldname).op/tions)
