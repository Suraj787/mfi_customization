# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
import	 datetime


def execute(filters=None):
	columns = get_columns()
	data  = get_data(filters)
	return columns, data

def get_columns(filters = None):
	
	return[	{
			"label":"Task",
			"fieldname":"name",
			"fieldtype":"Link",
			"options":"Task"	

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

#calculate call to fix and call to resolution in hours with holiday validation - 05/08/21[Anuradha]
def get_working_hrs(call_to, creation, completion_date_time, company):
	holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
	where h1.parent = h2.name and h1.holiday_date between %s and %s
	and h2.company = %s""", (creation, completion_date_time, company))[0][0]
	if holidays:
		days = call_to.days - holidays
	else:
		days = call_to.days
	hrs = call_to.seconds//3600
	minutes = int(call_to.seconds % 3600 / 60.0)
	daily_hrs_data = frappe.db.get_all("Support Hours", {'parent': 'Support Setting', 'company':company}, ['start_time', 'end_time', 'lunch_start_time', 'lunch_end_time'])
	if daily_hrs_data:
		daily_hrs = daily_hrs_data[0].get('end_time') - daily_hrs_data[0].get('start_time')  
		lunch_hr=datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

		if daily_hrs_data[0].get('lunch_end_time') and daily_hrs_data[0].get('lunch_start_time'):
			lunch_hr = daily_hrs_data[0].get('lunch_end_time') - daily_hrs_data[0].get('lunch_start_time')
		daily_hrs = daily_hrs - lunch_hr
		daily_hrs = daily_hrs.seconds//3600
		daily_hrs = daily_hrs if daily_hrs else 8
		if days != 0 :
			total_hours = (days * daily_hrs) + hrs
		else:
			total_hours = hrs
	else:
		frappe.msgprint("Please set start time and end time, lunch_start time and lunch_end time in Support Setting for '{0}'".format(company))
	return ("<b>hours : </b> "+str(total_hours)+ ", <b>min : </b> "+str(minutes)),total_hours

def get_data(filters):
	data = []
	call_assign_date = ""
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
			resolution_date =""
			attended_date= ""
			call_to_fix =""
			call_resolution_time=""
			if tk.get('completion_date_time'):
				resolution_date =  tk.get('completion_date_time')
				resolution_date = resolution_date.strftime("%d/%m/%Y, %I:%M:%S %p")
			if tk.get('attended_date_time'):
				attended_date =  tk.get('attended_date_time')
				attended_date = attended_date.strftime("%d/%m/%Y, %I:%M:%S %p")
			if tk.get('creation') :
				logging = tk.get('creation')
				logging = logging.strftime("%d/%m/%Y, %I:%M:%S %p")
				
			response_time=""
			response_time_int_value=0
			#Calculating the diff and converting time in fours			
			if tk.get('creation') and tk.get('attended_date_time'):
				response_time_diff = (tk.get('attended_date_time')- tk.get("creation"))
				# hrs1 = ((response_time_diff.seconds//60)%60)/60
				# response_time = round(((response_time_diff.days * 24) + (((response_time_diff.seconds//3600)) + hrs1)),2)
				response_time,response_time_int_value=get_working_hrs(response_time_diff, tk.get('creation'), tk.get('attended_date_time'), i.get('company') or "MFI MAROC SARL")
			
	
			if tk.get('completion_date_time') and tk.get('creation'):
				call_to=tk.get('completion_date_time') - tk.get('creation')
				call_to_fix = get_working_hrs(call_to, tk.get('creation'), tk.get('completion_date_time'), i.get('company') or "MFI MAROC SARL")[0]
			
			if tk.get('completion_date_time') and tk.get('attended_date_time'):
				call_resolution=tk.get('completion_date_time') - tk.get('attended_date_time')
				call_resolution_time = get_working_hrs(call_resolution, tk.get('attended_date_time'), tk.get('completion_date_time'), i.get('company') or "MFI MAROC SARL")[0]

			#applying filters according to condition set
			if tk.get('attended_date_time') != None:
				call_assign_date = (tk.get('attended_date_time')).strftime("%d/%m/%Y")
			if lgc_value == '>' and  int(digit) <= response_time_int_value:
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
			elif lgc_value == '<' and  int(digit) >= response_time_int_value and response_time_int_value >= 0  and call_resolution_time:

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
			elif lgc_value == '' and response_time_int_value >= 0 and call_resolution_time:

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