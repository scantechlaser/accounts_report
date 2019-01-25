// Copyright (c) 2016, Scantechalaser.com and contributors
// For license information, please see license.txt
/* eslint-disable */

// frappe.query_reports["GP Ratio"] = {
// 	"filters": [

// 	]
// }



frappe.require("assets/erpnext/js/financial_statements.js", function() {


	// frappe.query_reports["GP Ratio"] = [];
	// frappe.query_reports["GP Ratio"] = erpnext.financial_statements;
	frappe.query_reports["GP Ratio"] = $.extend({},
		erpnext.financial_statements);


	// console.log(frappe.query_reports["GP Ratio"]);

	frappe.query_reports["GP Ratio"]["filters"].splice(6, 1);
	frappe.query_reports["GP Ratio"]["filters"].splice(5, 1);
	frappe.query_reports["GP Ratio"]["filters"].splice(4, 1);
	frappe.query_reports["GP Ratio"]["filters"].splice(3, 1);
	frappe.query_reports["GP Ratio"]["filters"].splice(2, 1);
	frappe.query_reports["GP Ratio"]["filters"].splice(1, 1);
	

	frappe.query_reports["GP Ratio"]["filters"].push({
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
			},
			{
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
				},
				{
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check",
		"default": 1
	},
	{
						"fieldname": "from_date",
						"label": __("From Date"),
						"fieldtype": "Date",
						"default": frappe.defaults.get_user_default("year_start_date"),
					},
					{
						"fieldname": "to_date",
						"label": __("To Date"),
						"fieldtype": "Date",
						"default": frappe.defaults.get_user_default("year_end_date"),
					},
					{
				
					"fieldname": "presentation_currency",
					"label": __("Currency"),
					"fieldtype": "Select",
					"options": ""				}


	);

});


frappe.query_reports["GP Ratio"] = {
  
    "formatter":function (row, cell, value, columnDef, dataContext, default_formatter) {
        value = default_formatter(row, cell, value, columnDef, dataContext);
      
       // if (columnDef.id != "Customer" && columnDef.id != "Payment Date" && dataContext["Rental Payment"] > 100) {
            value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
       // }
       return value;
    }
}


