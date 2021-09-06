# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns  = get_column()
	data	 = get_data(filters)
	return columns, data

def get_column(filters = None):
	return[
		{
			"label":"Call Date",
			"fieldname":"call_date",
			"fieldtype":"Data"	

		},
		{
			"label":"Customer Name",
			"fieldname":"client_name",
			"fieldtype":"Data"	,
			"width":190

		},
		{
			"label":"Asset Code",
			"fieldname":"asset_code",
			"fieldtype":"Data"	

		},
		{
			"label":"Serial Number",
			"fieldname":"serial_no",
			"fieldtype":"Data"	

		},
		{
			"label":"Nature of Problem",
			"fieldname":"nature_of_problem",
			"fieldtype":"Data"	

		},{
			"label":"Spare Needed",
			"fieldname":"spare_needed",
			"fieldtype":"Data"	

		}

]
def get_data(filters):
	data = []
	fltr = {}
	if filters.get("client_name"):
		fltr.update({"customer":filters.get("client_name")})
	if filters.get("company_name"):
		fltr.update({"company":filters.get("company_name")})

	for issue in frappe.get_all('Issue',fltr,['name','subject','customer','issue_type','asset_name','failure_date_and_time','serial_no','name_of_the_customer']):
		if not issue.failure_date_and_time == None:
			call_date = issue.failure_date_and_time.strftime("%d-%m-%Y")
		
		for tk in frappe.get_all('Task',{'issue':issue.get('name')},['name']):
			s = ""
			for rs in frappe.get_all('Repair Items',{'parent':tk.get('name')},['item']):
				if not s:
					s += "{0} ".format(rs.get('item'))	
				else:
					s += ",{0} ".format(rs.get('item'))
				print(tk.get('name'))
				print(rs.get('item'))
				print(s)
		row = {
				"call_date":call_date,
				"client_name":issue.name_of_the_customer,
				"serial_no":issue.serial_no,
				"nature_of_problem":issue.issue_type,
				"asset_code":issue.asset_name,
				"spare_needed":s
			}
		data.append(row)
		
	return data
		