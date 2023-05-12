// Copyright (c) 2023, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Attendance Log of Engineers"] = {
	"filters": [
		{
			"label":"Technician Name",
			"fieldname":"technician_name",
			"fieldtype":"Link",
			"options":"User"	
		},
		{
		   "fieldname": "assign_date",
			"label": __("Assign Date"),
			"fieldtype": "Date",
			"reqd": 0
		}

	]
};
