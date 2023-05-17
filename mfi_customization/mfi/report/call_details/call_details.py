# Copyright (c) 2023, bizmap technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns  = get_columns()
	data	 = get_data(filters)
	return columns, data

def get_columns(filters = None):
	
	return[
		{
			"label":"No. of Calls",
			"fieldname":"no_of_calls",
			"fieldtype":"Data"	
		},
		{
			"label":"No. of PM's",
			"fieldname":"no_of_pm",
			"fieldtype":"Data"	
		},
		{
			"label":"No. of Installations",
			"fieldname":"no_of_installations",
			"fieldtype":"Data"	
		},
		{
			"label":"No. of Call Completed",
			"fieldname":"no_of_call_completed",
			"fieldtype":"Data"	
		},
		{
			"label":"No. of Pending Calls",
			"fieldname":"no_of_pending_calls",
			"fieldtype":"Data"	
		},
		{
			"label":"No. of Repeat Calls",
			"fieldname":"no_of_repeat_calls",
			"fieldtype":"Data"	
		},
		{
			"label":"List of Required Spares",
			"fieldname":"list_of_required_spares",
			"fieldtype":"Data"	
		}


		]

def get_data(filters):
	data = []
	fltr = {}
	if filters.get('from_date') and filters.get('to_date') :
		row = frappe.db.sql("""SELECT  
		(SELECT COUNT(*) FROM `tabTask` WHERE assign_date between '{0}' and '{1}') as no_of_calls,
		(SELECT COUNT(*) FROM `tabTask` WHERE type_of_call='PM' and assign_date between '{0}' and '{1}') as no_of_pm,
		(SELECT COUNT(*) FROM `tabTask` WHERE type_of_call ='Ins' and assign_date between '{0}' and '{1}') as no_of_installations,
		(SELECT COUNT(*) FROM `tabTask` WHERE status ='Completed' and assign_date between '{0}' and '{1}') as no_of_call_completed,
		(SELECT COUNT(*) FROM `tabTask` WHERE status in ('Open','Pending Review','Overdue','Working') and assign_date between '{0}' and '{1}') as no_of_pending_calls,
		(SELECT COUNT(*) FROM `tabTask` WHERE repetitive_call =1 and assign_date between '{0}' and '{1}') as no_of_repeat_calls,
		(SELECT COUNT(name) from `tabMaterial Request` where task IS NOT NULL and transaction_date between '{0}' and '{1}') as list_of_required_spares
		FROM (SELECT DISTINCT name FROM `tabTask`) t 
		""".format(filters.get('from_date'), filters.get('to_date')), as_dict=1)

		data.append(row[0])
	return data
		