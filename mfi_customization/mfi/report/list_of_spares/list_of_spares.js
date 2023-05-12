// Copyright (c) 2023, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["List of Spares"] = {
	"filters": [
		{
            fieldname: 'creation',
            label: __('Creation'),
            fieldtype: 'Date',
            default: frappe.datetime.get_today()
        },
	]
};
