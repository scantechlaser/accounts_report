# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "accounts_report"
app_title = "Accounts Report"
app_publisher = "Scantechalaser.com"
app_description = "Account Customize Report"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "it@scantechlaser.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/accounts_report/css/accounts_report.css"
# app_include_js = "/assets/accounts_report/js/accounts_report.js"

# include js, css files in header of web template
# web_include_css = "/assets/accounts_report/css/accounts_report.css"
# web_include_js = "/assets/accounts_report/js/accounts_report.js"

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
# get_website_user_home_page = "accounts_report.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "accounts_report.install.before_install"
# after_install = "accounts_report.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "accounts_report.notifications.get_notification_config"

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

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"accounts_report.tasks.all"
# 	],
# 	"daily": [
# 		"accounts_report.tasks.daily"
# 	],
# 	"hourly": [
# 		"accounts_report.tasks.hourly"
# 	],
# 	"weekly": [
# 		"accounts_report.tasks.weekly"
# 	]
# 	"monthly": [
# 		"accounts_report.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "accounts_report.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "accounts_report.event.get_events"
# }

