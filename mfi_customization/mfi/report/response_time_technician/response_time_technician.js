// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Response Time Technician"] = {
	"filters": [
		{
			"label":"Technician Name",
			"fieldname":"techn_name",
			"fieldtype":"Link",
			"options":"User"	

		},
		{
			"fieldname": "from_date",
			"label": __("Assign Date From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
			"reqd": 0
		},
		{
			"fieldname": "to_date",
			"label": __("Assign Date To"),
			"default": frappe.datetime.get_today(),
			"fieldtype": "Date",
			"reqd": 0
		},{
			"label":"Company",
			"fieldname":"c_name",
			"fieldtype":"Link",
			"options":"Company"	,
			"reqd": 1
	
		}

	]
};
