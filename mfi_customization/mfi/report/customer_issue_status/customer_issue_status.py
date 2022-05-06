# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	data = prepare_data(filters)
	columns = get_columns(filters)
	return columns, data

def get_columns(filters=None):
	return [
	{
	"label": "Ticket no",
	"fieldtype": "Data",
	"fieldname": "ticket",
	'width':120
	},
	{
	"label": "Call assigned to",
	"fieldtype": "Data",
	"fieldname": "call_assigned",
	'width':160
	},
	{
	"label": "ML - Number",
	"fieldtype": "Data",
	"fieldname": "ml_number",
	'width':110
	},
	
	{
	"label": "Customer",
	"fieldtype": "Link",
	"fieldname": "customer",
	'width':110,
	"options":"Customer"
	},
	
	{
	"label": "Location",
	"fieldtype": "Data",
	"fieldname": "location",
	'width':110
	},
	{
	"label": "Nature of complaint",
	"fieldtype": "Data",
	"fieldname": "complaint",
	'width':100
	},
	{
	"label": "Model",
	"fieldtype": "Data",
	"fieldname": "model",
	'width':100
	},
	{
	"label": "Serial No",
	"fieldtype": "Data",
	"fieldname": "serial_no",
	'width':100
	},
	{
	"label": "Counter Black & White",
	"fieldtype": "Data",
	"fieldname": "counter_bw",
	'width':120
	},
	{
	"label": "Counter color",
	"fieldtype": "Data",
	"fieldname": "counter_color",
	'width':150
	},
	{
	"label": "Total Counter",
	"fieldtype": "Data",
	"fieldname": "total_counter",
	'width':150
	},
	{
	"label": "Area Manager",
	"fieldtype": "Data",
	"fieldname": "manager",
	'width':150
	},
	{
	"label": "Status",
	"fieldtype": "Data",
	"fieldname": "status",
	'width':150
	},
	{
	"label": "Description",
	"fieldtype": "Data",
	"fieldname": "description",
	'width':150
	}
]

def prepare_data(filters):
	data=[]
	fltr={}
	if filters.get("company"):
		fltr.update({"company":filters.get("company")})
	if filters.get("customer"):
	        fltr.update({"customer":filters.get("customer")})
	   	
	for i in frappe.get_all('Issue',filters=fltr,fields=['name','status','description','asset','project','location','serial_no','issue_type','customer']):
		row={}
		row.update(i)
		row.update({"ticket":i.name,"location":i.location,"complaint":i.issue_type,"ml_number":i.asset,})
		if i.project:
			row.update({'manager':frappe.db.get_value('Project',i.project,'manager_name')})
		for t in frappe.get_all('Task',filters={'issue':i.name},fields=['name','issue','completed_by','asset','location','issue_type','project']):
			row.update({"call_assigned":t.completed_by})
			for a in frappe.get_all('Asset Readings',filters={'parent':t.name,'asset':t.asset},fields=['reading','reading_2','type']):
				row.update({'counter_bw':a.reading or '-','model':a.type,'counter_color':a.reading_2 or '-','total_counter':int(a.reading or 0)+ int(a.reading_2 or 0)})
		data.append(row)
		
		
	return data




















