// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Issue Status"] = {
	"filters": [
		{
			"label":"Company",
			"fieldname":"company",
			"fieldtype":"Link",
			"options":"Company"	,
			"reqd": 1

		}
	]
};
