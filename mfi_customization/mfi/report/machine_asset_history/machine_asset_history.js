// Copyright (c) 2022, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Machine Asset History"] = {
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

      

    ],
     "formatter":function(value, row, column, data, default_formatter){
                     value = default_formatter(value, row, column, data);
                     
        if (column.id == "mr.actual_coverage") {
            var val=value.replace(/%/,'')
            console.log("+++",val)
            if (val>5){
            value = "<p style='background-color:#b6f5a6!important;'>" + value + "</p>";
        }
        if (val<5){
            value = "<p style='background-color:##f5a2a2!important;'>" + value + "</p>";
        }
        }
              return value;
    }
};
