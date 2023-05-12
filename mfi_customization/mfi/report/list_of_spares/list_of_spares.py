# Copyright (c) 2023, bizmap technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	frappe.log_error('get_cols')
	return[
		"Item Code" + "Link/Item:150",
		"Item Name" + ":Data:150",
		"Required By" + ":Date:150 0",
		"Quantity" + ":Data:150",
		"UOM" + ":Data:100",
	]	

def get_data(filters=None):
	frappe.log_error('get_data')
	data=[]
	mr_list=frappe.get_all("Material Request")
	for mr in mr_list:
		is_inclusive_tax = False
		mr_doc = frappe.get_doc("Material Request",mr.name)
		# pe = frappe.get_doc("Payment Entry",{'party':purchase_invoice_doc.supplier})
		for item in mr_doc.items:
			item_code = item.item_code if item.item_code else ""
			item_name = item.item_name if item.item_name else ""
			required_by = item.schedule_date if item.schedule_date else ""
			quantity = item.qty if item.qty else ""
			uom = item.uom if item.uom else ""
			row = [
					item_code,
					item_name,
					required_by,
					quantity,
					uom
			]
			data.append(row)
	return data
		