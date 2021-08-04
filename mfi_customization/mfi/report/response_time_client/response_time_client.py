# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re

def execute(filters=None):
	columns = get_columns()
	data  = get_data(filters)
	return columns, data

def get_columns(filters = None):
	
	return[	{
			"label":"Task",
			"fieldname":"name",
			"fieldtype":"Data"	

		},
			{
			"label":"Response Time (hours)",
			"fieldname":"response_time",
			"fieldtype":"Data"	

		},{
			"label":"Call Logging",
			"fieldname":"creation",
			"fieldtype":"Data"	

		},{
			"label":"Call Assign Date",
			"fieldname":"call_assign_date",
			"fieldtype":"Data"	

		},{
			"label":"Call Attended",
			"fieldname":"call_attended",
			"fieldtype":"Data"	

		},
		{
			"label":"Call Resolved Date Time",
			"fieldname":"call_resolution_date",
			"fieldtype":"Data"	

		},{
			"label":"Client Name",
			"fieldname":"client_name",
			"fieldtype":"Data"	

		},{
			"label":"Machine Model",
			"fieldname":"machine_model",
			"fieldtype":"Data"	

		},{
			"label":"Serial Number",
			"fieldname":"serial_no",
			"fieldtype":"Data"	

		},{
			"label":"Nature of Problem",
			"fieldname":"nature_of_prob",
			"fieldtype":"Data"	

		},{
			"label":"Call To Fix",
			"fieldname":"call_to_fix",
			"fieldtype":"Data",
			"width":180	

		},{
			"label":"Resolution time",
			"fieldname":"call_resolution_time",
			"fieldtype":"Data",
			"width":180		

		}
		]

def get_data(filters):
	data = []
	response_time = 0
	call_assign_date = 0
	fltr = ""
	lgc_value = ""
	digit = 0
	fltr2 = {}
	row ={}

	if filters.get("response_time"):
		fltr = filters.get("response_time")
		lgc_value = fltr[0]
		digit = fltr[1:]
	
		
	if filters.get("client_name"):
		fltr2.update({"customer":filters.get("client_name")})
	if filters.get("c_name"):
		fltr2.update({"company":filters.get("c_name")})

	for i in frappe.get_all('Issue',fltr2,['name','company','failure_date_and_time','response_date_time','resolution_date','customer','asset','serial_no','issue_type']):
		
		for tk in frappe.db.get_all('Task',{'issue':i.get("name")},['completion_date_time','issue','name','creation','assign_date','attended_date_time']):
			resolution_date =0
			attended_date= 0
			call_to_fix =""
			call_resolution_time=""
			if tk.get('completion_date_time'):
				resolution_date =  tk.get('completion_date_time')
				resolution_date = resolution_date.strftime("%m/%d/%Y, %H:%M:%S")
			if tk.get('attended_date_time'):
				attended_date =  tk.get('attended_date_time')
				attended_date = attended_date.strftime("%m/%d/%Y, %H:%M:%S")
			if tk.get('creation') :
				logging = tk.get('creation')
				logging = logging.strftime("%m/%d/%Y, %H:%M:%S")
				
			
			#Calculating the diff and converting time in fours			
			if tk.get('creation') and tk.get('attended_date_time'):
				response_time_diff = (tk.get('attended_date_time')- tk.get("creation"))
				hrs1 = ((response_time_diff.seconds//60)%60)/60
				response_time = round(((response_time_diff.days * 24) + (((response_time_diff.seconds//3600)) + hrs1)),2)
			
			else:
				response_time = 0
	
			if tk.get('completion_date_time') and tk.get('creation'):
				call_to=tk.get('completion_date_time') - tk.get('creation')
				call_to_fix=("<b>days:</b>"+str(call_to.days)+"  <b>hours:</b>"+str(call_to.seconds//3600)+" <b>minutes:</b>"+str((call_to.seconds//60)%60))
			
			if tk.get('completion_date_time') and tk.get('attended_date_time'):
				call_resolution=tk.get('completion_date_time') - tk.get('attended_date_time')
				call_resolution_time=("<b>days:</b>"+str(call_resolution.days)+"  <b>hours:</b>"+str(call_resolution.seconds//3600)+" <b>minutes:</b>"+str((call_resolution.seconds//60)%60))

			#applying filters according to condition set
			if tk.get('attended_date_time') != None:
				call_assign_date = (tk.get('attended_date_time')).strftime("%d/%m/%Y")
			if lgc_value == '>' and  int(digit) <= response_time:
				row = {
				'name': tk.get('name'),
				'response_time': response_time,
				'creation':logging,
				'call_assign_date':call_assign_date ,
				'call_attended': attended_date,
				'call_resolution_date': resolution_date,
				'client_name':i.get("customer"),
				'machine_model':i.get("asset"),
				'serial_no':i.get("serial_no"),
				'nature_of_prob': i.get("issue_type"),
				'call_to_fix':call_to_fix,
				'call_resolution_time':call_resolution_time
						}
				data.append(row)
			elif lgc_value == '<' and  int(digit) >= response_time and response_time >= 0  and call_resolution_time:

				row = {
				'name': tk.get('name'),
				'response_time': response_time,
				'creation':logging,
				'call_assign_date':call_assign_date ,
				'call_attended': attended_date,
				'call_resolution_date':resolution_date,
				'client_name':i.get("customer"),
				'machine_model':i.get("asset"),
				'serial_no':i.get("serial_no"),
				'nature_of_prob': i.get("issue_type"),
				'call_to_fix':call_to_fix,
				'call_resolution_time':call_resolution_time
						}
				data.append(row)

			#if no condition filter is applied
			elif lgc_value == '' and response_time >= 0 and call_resolution_time:

				row = {
				'name': tk.get('name'),
				'response_time': response_time,
				'creation':logging,
				'call_assign_date':call_assign_date ,
				'call_attended': attended_date,
				'call_resolution_date': resolution_date,
				'client_name':i.get("customer"),
				'machine_model':i.get("asset"),
				'serial_no':i.get("serial_no"),
				'nature_of_prob': i.get("issue_type"),
				'call_to_fix':call_to_fix,
				'call_resolution_time':call_resolution_time
						}
				data.append(row)
			

	return data