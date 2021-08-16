// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Call Data Monthly"] = {
	"filters": [
		{
			"label":"Support Technician Name",
			"fieldname":"support_tech",
			"fieldtype":"Link",
			"options":"User"	

		},{
			"label":"Company",
			"fieldname":"c_name",
			"fieldtype":"Link",
			"options":"Company"	,
			"reqd": 1

		},{
			"label":"Type of Calls",
			"fieldname":"type_of_call",
			"fieldtype":"Link",
			"options":"Type of Call",
			"reqd": 0

		},{
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
		},

	]
};
