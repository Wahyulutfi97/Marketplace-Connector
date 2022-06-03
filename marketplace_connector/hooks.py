# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "marketplace_connector"
app_title = "Marketplace Connector"
app_publisher = "PT DAS"
app_description = "App for managing marketplace"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "digitalasiasolusindo@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/marketplace_connector/css/marketplace_connector.css"
# app_include_js = "/assets/marketplace_connector/js/marketplace_connector.js"

# include js, css files in header of web template
# web_include_css = "/assets/marketplace_connector/css/marketplace_connector.css"
# web_include_js = "/assets/marketplace_connector/js/marketplace_connector.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "marketplace_connector.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "marketplace_connector.install.before_install"
# after_install = "marketplace_connector.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "marketplace_connector.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# },

	# "Orders Management": {
	# 	"validate": ["marketplace_connector.marketplace_connector.doctype.sync_method.calculate_order_status", "marketplace_connector.marketplace_connector.doctype.sync_method.update_shipped_completed_shopee"],
		
	# },
	"Marketplace Orders": {
		"validate": ["marketplace_connector.marketplace_connector.doctype.sync_method.create_sinv_marketplace_orders"],
		
	},
	# "Item": {
		# "validate": ["marketplace_connector.marketplace_connector.doctype.sync_method.add_item_to_marketplace"]
	# }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	#"all": [
	#	"marketplace_connector.tasks.all"
	#],
	#"daily": [
	#	"marketplace_connector.marketplace_connector.doctype.sync_method.get_order_list_shopee"
	#],
	"hourly": [
		"marketplace_connector.marketplace_connector.doctype.sync_method.hourly_get_marketplace_orders"
	],
	#"weekly": [
	#	"marketplace_connector.tasks.weekly"
	#]
	#"monthly": [
	#	"marketplace_connector.tasks.monthly"
	#]
	#"cron": {
	#	"* */4 * * *": [
	#		"marketplace_connector.marketplace_connector.doctype.sync_method.get_refresh_token"
	#	]
	#}
}

# Testing
# -------

# before_tests = "marketplace_connector.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "marketplace_connector.event.get_events"
# }

