// Copyright (c) 2016, Scantechalaser.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Employee Ledger Report"] = {
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
		// {
		// 	"fieldname":"voucher_no",
		// 	"label": __("Voucher No"),
		// 	"fieldtype": "Data",
		// },
		// {
		// 	"fieldname":"project",
		// 	"label": __("Project"),
		// 	"fieldtype": "Link",
		// 	"options": "Project"
		// },
		{
			"fieldtype": "Break",
		},
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Link",
			"options": "Party Type",
			"default": "Employee",
			on_change: function() {
				frappe.query_report_filters_by_name.party.set_value("");
			}
		},
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "Dynamic Link",
			"get_options": function() {
				var party_type = frappe.query_report_filters_by_name.party_type.get_value();
				var party = frappe.query_report_filters_by_name.party.get_value();
				if(party && !party_type) {
					frappe.throw(__("Please select Party Type first"));
				}
				return party_type;
			},
			on_change: function() {
				var party_type = frappe.query_report_filters_by_name.party_type.get_value();
				var party = frappe.query_report_filters_by_name.party.get_value();
				if(!party_type || !party) {
					frappe.query_report_filters_by_name.party_name.set_value("");
					return;
				}
				var fieldname = erpnext.utils.get_party_name(party_type) || "name";
				frappe.db.get_value(party_type, party, fieldname, function(value) {
					frappe.query_report_filters_by_name.party_name.set_value(value[fieldname]);
				});

				if (party_type === "Customer" || party_type === "Supplier") {
					frappe.db.get_value(party_type, party, "tax_id", function(value) {
						frappe.query_report_filters_by_name.tax_id.set_value(value["tax_id"]);
					});
				}
			}
		},
		{
			"fieldname":"party_name",
			"label": __("Party Name"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname":"tax_id",
			"label": __("Tax Id"),
			"fieldtype": "Data",
			"hidden": 1
		},
		// ,
		// {
		// 	"fieldname":"group_by_voucher",
		// 	"label": __("Group by Voucher"),
		// 	"fieldtype": "Check",
		// 	"default": 1
		// },
		{
			"fieldname":"iou_account_check",
			"label": __("If Want IOU Account Details"),
			"fieldtype": "Check",
		}
	]
}
