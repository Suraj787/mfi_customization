// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Pending Spares"] = {
	"filters": [{
		"label":"Client Name",
		"fieldname":"client_name",
		"fieldtype":"Link",
		"options":"Customer"	
	},{
		"label":"Company Name",
		"fieldname":"company_name",
		"fieldtype":"Link",
		"options":"Company"	,
		"reqd": 1
	}

	]
};
