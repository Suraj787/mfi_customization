# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import date_diff, add_days, getdate


def execute(filters=None):
	columns  = get_columns()
	data	 = get_data(filters)
	return columns, data

def get_columns(filters = None):
	
	return[{
			"label":"Helpdesk",
			"fieldname":"helpdesk",
			"fieldtype":"Data"	

		},{
			"label":"Support Technician Name",
			"fieldname":"support_tech",
			"fieldtype":"Data"	

		},{
			"label":"Productivity",
			"fieldname":"productivity",
			"fieldtype":"Data"	

		},{
			"label":"Number of calls",
			"fieldname":"no_of_calls",
			"fieldtype":"Data"	

		},{
			"label":"Average Wait Time (Days)",
			"fieldname":"avg_wait_time",
			"fieldtype":"Data"	

		},{
			"label":"Resolved",
			"fieldname":"resolved",
			"fieldtype":"Data"	

		},{
			"label":"Pending Calls",
			"fieldname":"pending_calls",
			"fieldtype":"Data"	

		},{
			"label":"Productivity Per Day (%)",
			"fieldname":"prod_per_day",
			"fieldtype":"Data"	

		},{
			"label":"Average Time On Call",
			"fieldname":"average_time_on_call",
			"fieldtype":"Data"	

		}

		]


def get_data(filters):
		data = []
		fltr = {}
		fltr2 = {}
		fltr3 = {}
		assign_issue_cnt = 0
		unassign_issue_cnt = 0
		total_issue_cnt = len(frappe.get_all("Issue"))
		if filters.get("support_tech"):
			fltr.update({'email':filters.get("support_tech")})
		if filters.get('from_date') and filters.get('to_date') :
			fltr2.update({'assign_date':['between',(filters.get('from_date'),filters.get('to_date'))]})
		if filters.get("c_name"):
			fltr3.update({'company':filters.get("c_name")})
			fltr2.update({'company':filters.get("c_name")})
		for i in frappe.get_all('Issue',fltr3,['name','customer']):	
			for tk in frappe.get_all('Task',{'issue':i.get("name")},['completed_by','assign_date','attended_date_time']):
				assign_issue_cnt+=1
								

		
		unassign_issue_cnt = total_issue_cnt - assign_issue_cnt

		
		data.append({'helpdesk': unassign_issue_cnt})

		# waitage = frappe.db.get_value("Productive Waitage",filters.get("type_of_call"),'waitage')
		
		
		
		for usr in frappe.get_all("User",fltr,["first_name","last_name","email"]):
			row = {}
			cnt = 0
			avg_wt = 0
			avg_wait_time = 0
			resolved_call_cnt = 0
			total_calls_cnt = 0
			pending_calls_cnt = 0
			on_call_cnt = 0
			avg_on_call_cnt = 0
			avg_time_on_call = 0
			prod_per_day = 0
			productivity_by_wtg = 0
			response_time_diff = 0
			company = fltr3.get("company") if fltr3.get("company") else ( i.get('company') if  i.get('company') else 'MFI MAROC SARL')

			fltr2.update({"completed_by":usr.get("email")})
			fltr2.update({'type_of_call':filters.get("type_of_call")})
			no_of_day_productivity = date_diff(filters.get("to_date"),filters.get("from_date"))
			type_of_call = len(frappe.get_all("Task",{'type_of_call':filters.get("type_of_call")}))
			for tk2 in frappe.get_all('Task',fltr2,['completed_by','"completion_date_time"','attended_date_time','status','completion_date_time']):
				total_calls_cnt += 1
				company = fltr3.get("company") if fltr3.get("company") else ( frappe.db.get_value("Issue", {'name':tk2.issue}, 'company') if tk2.issue else 'MFI MAROC SARL')
				if tk2.get('completion_date_time') and tk2.get('attended_date_time'):
					response_time_diff = (tk2.get("completion_date_time") - tk2.get('attended_date_time')) 
					hrs = get_working_hrs(response_time_diff,tk2.get('attended_date_time'), tk2.get('completion_date_time'), company)
					productivity_by_wtg+=round(( float(type_of_call)* float(frappe.db.get_value("Type of Call",filters.get("type_of_call"),"waitage")) *  float(hrs)),2)
					# response_time = round(((response_time_diff.days * 24) + (((response_time_diff.seconds//3600)) + hrs)),2) 
					# productivity_by_wtg11 = round((float(response_time) * float(type_of_call) * float(waitage)),2)
				if tk2.get("attended_date_time") and tk2.get("assign_date"):
					cnt += 1
					avg_wt +=  date_diff(tk2.get("attended_date_time"), tk2.get("assign_date"))
				if tk2.get("completion_date_time") and tk2.get("assign_date"):
					on_call_cnt += 1
					avg_on_call_cnt +=  date_diff(tk2.get("completion_date_time"), tk2.get("assign_date"))
				if tk2.get("status") == 'Completed':
					resolved_call_cnt += 1
				if tk2.get("status") in ['Open','Pending Review','Overdue','Working']:
					pending_calls_cnt += 1
				
			if no_of_day_productivity != 0:
				prod_per_day = round(((resolved_call_cnt/no_of_day_productivity) * 100),2)
				
			if cnt != 0:
				avg_wait_time = (avg_wt/cnt)
			if on_call_cnt != 0:
				avg_time_on_call = (avg_on_call_cnt/on_call_cnt)
			
			row.update({
				'no_of_calls':total_calls_cnt,
				'support_tech': usr.get("first_name"),
				'avg_wait_time': avg_wait_time,
				'resolved': resolved_call_cnt,
				'pending_calls': pending_calls_cnt,
				'prod_per_day': prod_per_day,
				'average_time_on_call': avg_time_on_call,
				'productivity':productivity_by_wtg

			})
			
			if len(frappe.get_all("Task",{'completed_by':usr.email})) > 0 and total_calls_cnt>=1:
				data.append(row)
		
		return data


def get_working_hrs(call_to,opening_date_time, attended_time, company):
	holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
	where h1.parent = h2.name and h1.holiday_date between %s and %s
	and h2.company = %s""", (opening_date_time, attended_time, company))[0][0]
	total_hours=0
	if holidays:
		days = call_to.days - holidays
	else:
		days = call_to.days
	hrs = call_to.seconds//3600
	daily_hrs_data = frappe.db.get_all("Support Hours", {'parent': 'Support Setting', 'company':company}, ['start_time', 'end_time'])
	if daily_hrs_data:
		daily_hrs = daily_hrs_data[0].get('end_time') - daily_hrs_data[0].get('start_time')  
		daily_hrs = daily_hrs.seconds//3600
		daily_hrs = daily_hrs if daily_hrs else 9
		if days != 0 :
			total_hours = (days * daily_hrs) + hrs
		else:
			total_hours = hrs
	else:
		frappe.msgprint("Please set start time and end time in Support Setting for '{0}'".format(company))
	
	return total_hours