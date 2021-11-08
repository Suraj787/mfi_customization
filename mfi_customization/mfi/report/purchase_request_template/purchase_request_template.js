// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Request Template"] = {
	"filters": [
		{
			"label":"Item",
			"fieldname":"item",
			"fieldtype":"Link",
			"options":"Item",
			"reqd": 0,
			get_query:function(){
				if (frappe.query_report.get_filter_value('item_group_list') && frappe.query_report.get_filter_value('brand_list')){
					return {    
						filters:
							{
								'item_group': ["in",frappe.query_report.get_filter_value('item_group_list')],
								'brand': ["in",frappe.query_report.get_filter_value('brand_list')]
								
							}
						
					}
				}
				else if (frappe.query_report.get_filter_value('item_group_list')){
					return {    
						filters:
							{
								'item_group': ["in",frappe.query_report.get_filter_value('item_group_list')]
							}
						
					}
				}
				else if (frappe.query_report.get_filter_value('brand_list')){
					return {    
						filters:
							{
								'brand': ["in",frappe.query_report.get_filter_value('brand_list')]
							}
						
					}
				}
			},
			on_change: () => {
				var item = frappe.query_report.get_filter_value('item');
				if (item){
					var item_list=frappe.query_report.get_filter_value('item_list');
					if (item_list){
					frappe.query_report.set_filter_value('item_list',item_list+','+item);
					}
					else{
					frappe.query_report.set_filter_value('item_list',item);
				}
				}
				
			}
		},
		{
			"fieldname":"item_list",
			"label": __("Item List"),
			"fieldtype": "Data",
			"read_only":0
		},
		{
			"fieldname":"clear_item",
			"label": __("Clear Item Filter"),
			"fieldtype": "Button",
			onclick:()=>{
				frappe.query_report.set_filter_value('item_list','');
				frappe.query_report.set_filter_value('item','');
			}
		},
		{
			"label":"Item Group",
			"fieldname":"item_group",
			"fieldtype":"Link",
			"options":"Item Group",
			"reqd": 0,
			on_change: () => {
				var item_group = frappe.query_report.get_filter_value('item_group');
				if (item_group){
					var item_group_list=frappe.query_report.get_filter_value('item_group_list');
					if (item_group_list){
					frappe.query_report.set_filter_value('item_group_list',item_group_list+','+item_group);
					}
					else{
					frappe.query_report.set_filter_value('item_group_list',item_group);
				}
				}
				
			}
		},
		{
			"fieldname":"item_group_list",
			"label": __("Item Group List"),
			"fieldtype": "Data",
			"read_only":1
		},
		{
			"fieldname":"clear_item_group",
			"label": __("Clear Item Group Filter"),
			"fieldtype": "Button",
			onclick:()=>{
				frappe.query_report.set_filter_value('item_group_list','');
				frappe.query_report.set_filter_value('item_group','');
			}
		},
		{
			"label":"Brand",
			"fieldname":"brand",
			"fieldtype":"Link",
			"options":"Brand",
			"reqd": 0,
			on_change: () => {
				var brand = frappe.query_report.get_filter_value('brand');
				if (brand){
					var brand_list=frappe.query_report.get_filter_value('brand_list');
					if (brand_list){
					frappe.query_report.set_filter_value('brand_list',brand_list+','+brand);

					}
					else{
					frappe.query_report.set_filter_value('brand_list',brand);
				}
				}
				
			}
		},
		{
			"fieldname":"brand_list",
			"label": __("Brand List"),
			"fieldtype": "Data",
			"read_only":1,
		},
		{
			"fieldname":"clear_brand",
			"label": __("Clear Brand Filter"),
			"fieldtype": "Button",
			onclick:()=>{
				frappe.query_report.set_filter_value('brand_list','');
				frappe.query_report.set_filter_value('brand','');
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
