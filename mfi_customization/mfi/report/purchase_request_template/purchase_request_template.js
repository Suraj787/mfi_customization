// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Request Template"] = {
	"filters": [
		{
			"fieldname":"item_list",
			"label": __("Item"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				if ((frappe.query_report.get_filter_value('item_group_list')).length>0 && (frappe.query_report.get_filter_value('brand_list')).length>0){
					return frappe.db.get_link_options('Item', txt, {
						item_group: ["in",frappe.query_report.get_filter_value('item_group_list')],
						brand: ["in",frappe.query_report.get_filter_value('brand_list')]
					});
				}
				else if ((frappe.query_report.get_filter_value('item_group_list')).length>0){
					return frappe.db.get_link_options('Item', txt, {
						item_group: ["in",frappe.query_report.get_filter_value('item_group_list')]
					});
				}
				else if ((frappe.query_report.get_filter_value('brand_list')).length>0){
					return frappe.db.get_link_options('Item', txt, {
						brand: ["in",frappe.query_report.get_filter_value('brand_list')]
					});
				}
				else{
					return frappe.db.get_link_options('Item', txt);
				}
			
			},
		},
		{
			"fieldname":"clear_item",
			"label": __("Clear Item Filter"),
			"fieldtype": "Button",
			onclick:()=>{
				frappe.query_report.set_filter_value('item_list',[]);
			}
		},
		{
			"label":"Item Group",
			"fieldname":"item_group_list",
			"fieldtype": "MultiSelectList",
			"options":"Item Group",
			"reqd": 0,
			get_data: function(txt) {
				return frappe.db.get_link_options('Item Group', txt);
			}
		},
		{
			"fieldname":"clear_item_group",
			"label": __("Clear Item Group Filter"),
			"fieldtype": "Button",
			onclick:()=>{
				frappe.query_report.set_filter_value('item_group_list',[]);
			}
		},
		{
			"label":"Brand",
			"fieldname":"brand_list",
			"fieldtype": "MultiSelectList",
			"options":"Brand",
			"reqd": 0,
			get_data: function(txt) {
				return frappe.db.get_link_options('Brand', txt);
			}
		},
		{
			"fieldname":"clear_brand",
			"label": __("Clear Brand Filter"),
			"fieldtype": "Button",
			onclick:()=>{
				frappe.query_report.set_filter_value('brand_list',[]);
			}
		},
		{
			"label":"Company",
			"fieldname":"company",
			"fieldtype":"Link",
			"options":"Company",
			"reqd": 1
		},
		{
			"label":"Price List",
			"fieldname":"price_list",
			"fieldtype":"Link",
			"options":"Price List",
			"reqd": 1,
			get_query:function(){
					return {    

						filters:
							{
								'company': frappe.query_report.get_filter_value('company'),
								"buying":1
							}
							
						
					}
				
			}
		},
	]
};
