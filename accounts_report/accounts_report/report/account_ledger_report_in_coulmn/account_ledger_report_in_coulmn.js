// Copyright (c) 2016, Scantechalaser.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Account Ledger Report In Coulmn"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"voucher_no",
			"label": __("Voucher No"),
			"fieldtype": "Data",
		},
		{
			"fieldtype": "Break",
		},
		{
			"fieldname":"account_type",
			"label": __("Account Type"),
			"fieldtype": "Link",
			"options": "Account",
			"default": "",
			"reqd": 1
		}
	]
}
