# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import date_diff, add_days, getdate
import datetime


def execute(filters=None):
	type_of_call_list={}
	for call_type in frappe.get_all("Type of Call"):
		type_of_call_list[call_type.name]=((call_type.name).lower()).replace(" ", "_")
	columns  = get_columns(filters,type_of_call_list)
	data	 = get_data(filters,type_of_call_list)
	return columns, data

def get_columns(filters,type_of_call):
	
	columns=[{
			"label":"Support Technician Name",
			"fieldname":"support_tech",
			"fieldtype":"Data"	
		}]

	columns.extend([{"label":d,"fieldname":type_of_call[d],"fieldtype":"Data"} for d in type_of_call])
	columns.extend([
		{
			"label":"Resolved",
			"fieldname":"resolved",
			"fieldtype":"Data"	

		},
		{
			"label":"Pending Calls",
			"fieldname":"pending_calls",
			"fieldtype":"Data"	

		},
		{
			"label":"Productivity",
			"fieldname":"productivity",
			"fieldtype":"Data"	
		},
		{
			"label":"Avg. Productivity",
			"fieldname":"avg_productivity",
			"fieldtype":"Data"	
		},
		
	])
	return columns

def get_data(filters,type_of_call):
		data = []
		tsk_fltr = {}
	
		if filters.get('from_date') and filters.get('to_date') :
			tsk_fltr.update({'assign_date':['between',(filters.get('from_date'),filters.get('to_date'))]})
		if filters.get("company"):
			tsk_fltr.update({'company':filters.get("company")})
		
		for usr in frappe.get_all("User",["first_name","last_name","email","name","full_name"]):
			row = {}
			call_dict={}
			resolved_call_cnt=0
			pending_calls_cnt=0
			cancelled_call=0
			productivity=0

			for d in type_of_call:
				call_dict[type_of_call[d]]=0
				
			tsk_fltr.update({'completed_by':usr.name})

			for tk in frappe.get_all('Task',tsk_fltr,['completed_by','"completion_date_time"','attended_date_time','status','completion_date_time','type_of_call','assign_date','issue']):
				if tk.get("status") == 'Completed':

					# resolve calls
					resolved_call_cnt += 1

					for issue in frappe.get_all("Issue",{"name":tk.issue,'status':'Closed'}):

						# call count
						if tk.type_of_call:
							call_dict[type_of_call[tk.type_of_call]]+=1

						
				# pending calls
				if tk.get("status") in ['Open','Pending Review','Overdue','Working','Awaiting for Material']:
					pending_calls_cnt += 1

				# cancelled calls
				if tk.get("status") == 'Cancelled':
					cancelled_call += 1
			
			for call in type_of_call:
				productivity+=(call_dict[type_of_call[call]]*frappe.db.get_value("Type of Call",call,'waitage'))
			
			row.update({
				'support_tech': usr.get("full_name"),
				'resolved': resolved_call_cnt,
				'pending_calls': pending_calls_cnt,
				'productivity':productivity,
				'avg_productivity':productivity/len(type_of_call)
			})

			row.update(call_dict)
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
	minutes = int(call_to.seconds % 3600 / 60.0)
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
	if minutes :
		total_hours = float(str(total_hours)+"."+str(minutes))
		return total_hours
	else:
		return total_hours


def get_holiday_dates(company):
	holidayList=[]
	for hl in frappe.get_all("Holiday List",{"company":company}):
		holidayDoc=frappe.get_doc('Holiday List',hl.name)
		for d in holidayDoc.get('holidays'):
			holidayList.append(d.holiday_date)
	return holidayList