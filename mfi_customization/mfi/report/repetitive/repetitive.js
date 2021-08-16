// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Repetitive"] = {
	"filters": [
		{
			"label":"Serial Number",
			"fieldname":"serial_no",
			"fieldtype":"Link",
			'options':'Asset Serial No'	

		},
		{
			"label":"Customer",
			"fieldname":"customer",
			"fieldtype":"Link",
			'options':'Customer'	

		},
		{
			"label":"Company",
			"fieldname":"company",
			"fieldtype":"Link",
			"options":"Company"	,
			"reqd": 1

		},
		{
			"fieldname": "from_date",
			"label": __("In Date From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
			"reqd": 1
			},
			{
			"fieldname": "to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
			},

			
	]
};
