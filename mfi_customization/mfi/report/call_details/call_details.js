// Copyright (c) 2023, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Call Details"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("Assign Date From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -90),
			"reqd": 0
		},{
			"fieldname": "to_date",
			"label": __("Assign Date To"),
			"default": frappe.datetime.get_today(),
			"fieldtype": "Date",
			"reqd": 0
		}

	]
};
