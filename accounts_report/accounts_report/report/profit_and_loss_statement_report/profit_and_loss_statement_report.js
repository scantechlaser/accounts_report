// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt


frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Profit and Loss Statement Report"] = $.extend({},
		erpnext.financial_statements);

	// console.log(frappe.query_reports["Profit and Loss Statement Report"]["filters"]);

	for (var i = frappe.query_reports["Profit and Loss Statement Report"]["filters"].length - 1; i >= 0; i--) {
		
		if (frappe.query_reports["Profit and Loss Statement Report"]["filters"][i].label=='Periodicity') {

			frappe.query_reports["Profit and Loss Statement Report"]["filters"].splice(i, 1);
		}
	}
console.log(frappe.query_reports["Profit and Loss Statement Report"]["filters"]);
	frappe.query_reports["Profit and Loss Statement Report"]["filters"].push(
		{
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "MultiSelect",
			get_data: function() {
				var projects = frappe.query_report.get_filter_value("project") || "";

				const values = projects.split(/\s*,\s*/).filter(d => d);
				const txt = projects.match(/[^,\s*]*$/)[0] || '';
				let data = [];

				frappe.call({
					type: "GET",
					method:'frappe.desk.search.search_link',
					async: false,
					no_spinner: true,
					args: {
						doctype: "Project",
						txt: txt,
						filters: {
							"name": ["not in", values]
						}
					},
					callback: function(r) {
						data = r.results;
					}
				});
				return data;
			}
		},
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check"
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
				}
	);
});
