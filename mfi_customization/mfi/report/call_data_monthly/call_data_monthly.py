# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import date_diff, add_days, getdate, flt
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
		{
			"label":"Achivment",
			"fieldname":"achivment",
			"fieldtype":"Data"	
		},
		{
			"label":"Repetitive",
			"fieldname":"repetitive",
			"fieldtype":"Data"	
		},
		
	])
	return columns

def get_data(filters,type_of_call):
		data = []
		tsk_fltr = {}
		no_of_working_days=0
		if filters.get('from_date') and filters.get('to_date') :
			day_diff=date_diff(getdate(filters.get('to_date')),getdate(filters.get('from_date')))
			no_of_working_days=day_diff-get_no_of_holidays(filters.get('from_date'), filters.get('to_date'),filters.get("company"))
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
				
			tsk_fltr.update({'completed_by':usr.name,"asset":("!=","")})
			repetitive=0
			for ast in frappe.get_all("Asset",{"company":filters.get("company"),"name":["IN",get_asset_list(tsk_fltr)]},['name','customer','serial_no','item_code','project']):
				repetitive+=get_count(ast.name,ast.item_code,filters)

			for tk in frappe.get_all('Task',tsk_fltr,['completed_by','"completion_date_time"','attended_date_time','status','completion_date_time','type_of_call','assign_date','issue']):
				if tk.get("status") == 'Completed':

					# resolve calls
					resolved_call_cnt += 1

					# call count
					if tk.type_of_call:
						call_dict[type_of_call[tk.type_of_call]]+=1

						
				# pending calls
				if tk.get("status") in ['Open','Pending Review','Overdue','Working','Awaiting for Material','Open']:
					pending_calls_cnt += 1

				# cancelled calls
				if tk.get("status") == 'Cancelled':
					cancelled_call += 1
			
			for call in type_of_call:
				productivity+=(call_dict[type_of_call[call]]*frappe.db.get_value("Type of Call",call,'waitage'))
			achivment=flt(productivity/no_of_working_days, 2)/flt(frappe.db.get_value("Support Setting","Support Setting","achievement_factor"))
			row.update({
				'support_tech': usr.get("full_name"),
				'resolved': resolved_call_cnt,
				'pending_calls': pending_calls_cnt,
				'productivity':productivity,
				'avg_productivity':flt(productivity/no_of_working_days, 2),
				'achivment':str(flt(achivment*100,2))+"%",
				'repetitive':repetitive
			})

			row.update(call_dict)
			data.append(row)
		
		return data

def get_no_of_holidays(from_date, to_date, company):
	holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
	where h1.parent = h2.name and h1.holiday_date between %s and %s
	and h2.company = %s""", (from_date, to_date, company))[0][0]
	if holidays:
		return holidays

def get_count(asset,item_code,filters):
	count=0
	records=frappe.get_all("Machine Reading",{"asset":asset,"reading_date":['between',(filters.get('from_date'),filters.get('to_date'))]},["colour_reading","black_and_white_reading"])
	
	for i,d in enumerate(records):
		colour_diff=0
		bw_diff=0
		if i!=0:
			colour_diff=flt(records[i-1].colour_reading)-flt(records[i].colour_reading)
			bw_diff=flt(records[i-1].black_and_white_reading)-flt(records[i].black_and_white_reading)
			if frappe.db.get_value("Item",item_code,'avg_duty_cycle')>colour_diff or frappe.db.get_value("Item",item_code,'avg_duty_cycle')>bw_diff:
				count+=1

	return count


def get_asset_list(filters):
	return [d.asset for d in frappe.get_all('Task',filters,['asset'])]


