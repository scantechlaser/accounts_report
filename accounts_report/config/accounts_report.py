from __future__ import unicode_literals
import frappe
from frappe import _
# from frappe.desk.moduleview import get

def get_data():

	# mydata = get
	# frappe.msgprint(ksjaksjskd)
	return [
		{
			"label": _("Accounts Custom Reports"),
			"items": [
				{
					"type": "report",
					"name":"Account Ledger Report In Coulmn",
					"doctype": "account_report",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name":"Balance Sheet Report",
					"doctype": "account_report",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name":"General Ledger Report",
					"doctype": "account_report",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name":"Journal Register Report",
					"doctype": "account_report",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name":"Profit and Loss Statement Report",
					"doctype": "account_report",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name":"Cash Flow Report",
					"doctype": "account_report",
					"is_query_report": True,
				},
				{
					"type": "report",
					"name":"GP Ratio",
					"doctype": "account_report",
					"is_query_report": True,
				}
			]
		},
		{
			"label": _("Help"),
			"icon": "fa fa-facetime-video",
			"items": [
				{
					"type": "help",
					"label": _("Chart of Accounts"),
					"youtube_id": "DyR-DST-PyA"
				},
				{
					"type": "help",
					"label": _("Opening Accounting Balance"),
					"youtube_id": "kdgM20Q-q68"
				},
				{
					"type": "help",
					"label": _("Setting up Taxes"),
					"youtube_id": "nQ1zZdPgdaQ"
				}
			]
		}
	]
