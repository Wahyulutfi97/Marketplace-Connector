from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Marketplace Connector"),
			"items": [
				{
					"type": "doctype",
					"name": "Marketplace Orders",
					"description":_("Marketplace Orders"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Shopee Setting",
					"description":_("Shopee Setting"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Shopee Shop Setting",
					"description":_("Shopee Setting"),
					"onboard": 1,
				},
				{
					"type": "doctype",
					"name": "Sync Manual",
					"description":_("Sync Manual"),
					"onboard": 1,
				},
				
			]
		},

		
	]