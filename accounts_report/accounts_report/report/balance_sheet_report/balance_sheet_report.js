// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt


frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Balance Sheet Report"] = erpnext.financial_statements;


	frappe.query_reports["Balance Sheet Report"]["filters"].splice(3, 1);
	frappe.query_reports["Balance Sheet Report"]["filters"].splice(2, 1);
	frappe.query_reports["Balance Sheet Report"]["filters"].splice(1, 1);
	

	frappe.query_reports["Balance Sheet Report"]["filters"].push({
				"fieldname": "fiscal_year",
				"label": __("Fiscal Year"),
				"fieldtype": "Link",
				"options": "Fiscal Year",
				"default": frappe.defaults.get_user_default("fiscal_year"),
				"reqd": 1,
				"on_change": function(query_report) {
					var fiscal_year = query_report.get_values().fiscal_year;
					if (!fiscal_year) {
						return;
					}
					frappe.model.with_doc("Fiscal Year", fiscal_year, function(r) {
						var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
						frappe.query_report_filters_by_name.from_date.set_input(fy.year_start_date);
						frappe.query_report_filters_by_name.to_date.set_input(fy.year_end_date);
						query_report.trigger_refresh();
					});
				}
			});


	frappe.query_reports["Balance Sheet Report"]["filters"].push({
					"fieldname": "periodicity",
					"label": __("Periodicity"),
					"fieldtype": "Select",
					"options": [
						{ "value": "Monthly", "label": __("Monthly") },
						{ "value": "Quarterly", "label": __("Quarterly") },
						{ "value": "Half-Yearly", "label": __("Half-Yearly") },
						{ "value": "Yearly", "label": __("Yearly") }
					],
					"default": "Yearly",
					"reqd": 1
				});

	frappe.query_reports["Balance Sheet Report"]["filters"].push({
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check",
		"default": 1
	});

	frappe.query_reports["Balance Sheet Report"]["filters"].push({
						"fieldname": "from_date",
						"label": __("From Date"),
						"fieldtype": "Date",
						"default": frappe.defaults.get_user_default("year_start_date"),
					});
	frappe.query_reports["Balance Sheet Report"]["filters"].push({
						"fieldname": "to_date",
						"label": __("To Date"),
						"fieldtype": "Date",
						"default": frappe.defaults.get_user_default("year_end_date"),
					});
	// frappe.query_reports["Balance Sheet Report"]["filters"].pop(1);

	// console.log();
});

// frappe.require("assets/erpnext/js/financial_statements.js", function() {

// frappe.query_reports["Balance Sheet Report"] = erpnext.financial_statements;
// 	frappe.query_reports["Balance Sheet Report"] = {

// onload: function(report) {
// 		// dropdown for links to other financial statements
// 		erpnext.financial_statements.filters = get_filters()

// 		report.page.add_inner_button(__("Balance Sheet"), function() {
// 			var filters = report.get_values();
// 			frappe.set_route('query-report', 'Balance Sheet', {company: filters.company});
// 		}, __('Financial Statements'));
// 		report.page.add_inner_button(__("Profit and Loss"), function() {
// 			var filters = report.get_values();
// 			frappe.set_route('query-report', 'Profit and Loss Statement', {company: filters.company});
// 		}, __('Financial Statements'));
// 		report.page.add_inner_button(__("Cash Flow Statement"), function() {
// 			var filters = report.get_values();
// 			frappe.set_route('query-report', 'Cash Flow', {company: filters.company});
// 		}, __('Financial Statements'));
// 	},
// 		"filters": [{
// 					"fieldname": "company",
// 					"label": __("Company"),
// 					"fieldtype": "Link",
// 					"options": "Company",
// 					"default": frappe.defaults.get_user_default("Company"),
// 					"reqd": 1
// 				},
// 				{
// 					"fieldname": "fiscal_year",
// 					"label": __("Fiscal Year"),
// 					"fieldtype": "Link",
// 					"options": "Fiscal Year",
// 					"default": frappe.defaults.get_user_default("fiscal_year"),
// 					"reqd": 1,
// 					"on_change": function(query_report) {
// 						var fiscal_year = query_report.get_values().fiscal_year;
// 						if (!fiscal_year) {
// 							return;
// 						}
// 						frappe.model.with_doc("Fiscal Year", fiscal_year, function(r) {
// 							var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
// 							frappe.query_report_filters_by_name.from_date.set_input(fy.year_start_date);
// 							frappe.query_report_filters_by_name.to_date.set_input(fy.year_end_date);
// 							query_report.trigger_refresh();
// 						});
// 					}
// 				},
// 				{
// 					"fieldname": "periodicity",
// 					"label": __("Periodicity"),
// 					"fieldtype": "Select",
// 					"options": [
// 						{ "value": "Monthly", "label": __("Monthly") },
// 						{ "value": "Quarterly", "label": __("Quarterly") },
// 						{ "value": "Half-Yearly", "label": __("Half-Yearly") },
// 						{ "value": "Yearly", "label": __("Yearly") }
// 					],
// 					"default": "Monthly",
// 					"reqd": 1
// 				},
// 				{
// 					"fieldname": "presentation_currency",
// 					"label": __("Currency"),
// 					"fieldtype": "Select",
// 					"options": ""				},
// 				{
// 				"fieldname": "accumulated_values",
// 				"label": __("Accumulated Values"),
// 				"fieldtype": "Check",
// 				"default": 1
// 			},
// 			{
// 						"fieldname": "from_date",
// 						"label": __("From Date"),
// 						"fieldtype": "Date",
// 						"default": frappe.defaults.get_user_default("year_start_date"),
// 					},
// 					{
// 						"fieldname": "to_date",
// 						"label": __("To Date"),
// 						"fieldtype": "Date",
// 						"default": frappe.defaults.get_user_default("year_end_date"),
// 					}
// 			]
// 			}
	
// });

