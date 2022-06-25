// Copyright (c) 2022, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["SLA Table"] = {
	"filters": [
           {
			"label":"Project",
			"fieldname":"name",
			"fieldtype":"Link",
			"options":"Project"	
		}
	]
};
