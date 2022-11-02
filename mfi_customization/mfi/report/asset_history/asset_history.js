// Copyright (c) 2022, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Asset History"] = {

    "filters": [{
            "fieldname": "task",
            "label": __("Task"),
            "fieldtype": "Link",
            "options": "Task",
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
        },
        {
            "fieldname": "asset",
            "label": __("Asset"),
            "fieldtype": "Link",
            "options": "Asset",
        },



    ]
};
