// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Response Time Client"] = {
	"filters": [
// 		{
// 				"label":"Response Time (hours)",
// 				"fieldname":"response_time",
// 				"fieldtype":"Select",
// 				"options":"\n>1\n<1\n>2\n<2\n>4\n<4\n>8\n>48"	

			// },
			// {
			// 	"label":"Customer Name",
			// 	"fieldname":"client_name",
			// 	"fieldtype":"Link",
			// 	"options":"Customer"	

			// },
			{
				"label":"Company Name",
				"fieldname":"c_name",
				"fieldtype":"Link",
				"options":"Company"	,
				"reqd": 1

			},{
				"fieldname": "from_date",
				"label": __("Assign Date From"),
				"fieldtype": "Date",
				"default": frappe.datetime.add_days(frappe.datetime.get_today(), -90),
				"reqd": 1
			},{
				"fieldname": "to_date",
				"label": __("Assign Date To"),
				"default": frappe.datetime.get_today(),
				"fieldtype": "Date",
				"reqd": 1
			},

	]
};
