# Copyright (c) 2023, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime

def execute(filters=None):
	columns  = get_column()
	data	 = get_data(filters)
	return columns, data

def get_column(filters = None):
	return[
		{
			"label":"Date",
			"fieldname":"assign_date",
			"fieldtype":"Date"	

		},
		{
			"label":"Task",
			"fieldname":"task",
			"fieldtype":"Data"	

		},
		{
			"label":"Technician Name",
			"fieldname":"technician_name",
			"fieldtype":"Data"	

		},
		{
			"label":"Asset",
			"fieldname":"asset",
			"fieldtype":"Link",
			"options": "Asset"

		},
		{
			"label":"Start Time",
			"fieldname":"start_time",
			"fieldtype":"Datetime"	

		},
		{
			"label":"End Time",
			"fieldname":"end_time",
			"fieldtype":"Datetime"
		},
		{
			"label":"Time Taken to Travel",
			"fieldname":"time_taken_to_travel",
			"fieldtype":"Time"
		}

]
def get_data(filters):
	data = []
	fltr = {}
	if filters.get("technician_name"):
		fltr.update({"technician_name":filters.get("technician_name")})
	for t in frappe.get_all('Task',fltr, ['name','assign_date','technician_name','asset','working_start_time','working_end_time']):
		if filters.get("assign_date"):
			date_object = datetime.strptime(filters.get("assign_date"), '%Y-%m-%d').date()
			if date_object == (t.assign_date).date():
				row = {
						"task":t.name,
						"assign_date":t.assign_date,
						"technician_name":t.technician_name,
						"asset":t.asset,
						"start_time":t.working_start_time,
						"end_time":t.working_end_time
				}
				if t.working_end_time and t.working_start_time :
					time_taken_to_travel = t.working_end_time - t.working_start_time
					if time_taken_to_travel:
						row.update({"time_taken_to_travel":time_taken_to_travel})
				data.append(row)
		else:
			row = {
					"task":t.name,
					"assign_date":t.assign_date,
					"technician_name":t.technician_name,
					"asset":t.asset,
					"start_time":t.working_start_time,
					"end_time":t.working_end_time
			}
			if t.working_end_time and t.working_start_time :
				time_taken_to_travel = t.working_end_time - t.working_start_time
				if time_taken_to_travel:
					row.update({"time_taken_to_travel":time_taken_to_travel})
			data.append(row)
		
		
	return data
		