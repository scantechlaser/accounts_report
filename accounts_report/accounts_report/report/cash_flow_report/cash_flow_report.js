// Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Cash Flow Report"] = $.extend({},
		erpnext.financial_statements);

	console.log(frappe.query_reports["Cash Flow Report"]);
	for (var i = frappe.query_reports["Cash Flow Report"]["filters"].length - 1; i >= 0; i--) {
		
		if (frappe.query_reports["Cash Flow Report"]["filters"][i].label=='Periodicity') {

			frappe.query_reports["Cash Flow Report"]["filters"].splice(i, 1);
		}
	}

	// The last item in the array is the definition for Presentation Currency
	// filter. It won't be used in cash flow for now so we pop it. Please take
	// of this if you are working here.
	// frappe.query_reports["Cash Flow Report"]["filters"].pop();

	frappe.query_reports["Cash Flow Report"]["filters"].push({
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
				},{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check"
		}
		);
});