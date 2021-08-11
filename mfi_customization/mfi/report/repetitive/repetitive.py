# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from frappe.utils import  getdate,today,add_days,flt
import frappe


def execute(filters=None):
	columns  = get_column()
	data	 = get_data(filters)
	return columns, data
def get_column(filters = None):
	return[
		{
			"label":"Client Name",
			"fieldname":"customer",
			"fieldtype":"Link",
			"options":"Customer",
			"width":180	

		},{
			"label":"Serial Number",
			"fieldname":"serial_no",
			"fieldtype":"Link",
			"options":"Asset Serial No",
			"width":150	

		},{
			"label":"Machine Model",
			"fieldname":"machine_model",
			"fieldtype":"Link",
			"options":"Asset",
			"width":120	

		},
		{
			"label":"Number Of Calls",
			"fieldname":"calls",
			"fieldtype":"Data",
			"width":120		

		}


]


def get_data(filters):
	data = []
	# fltr1 = {}
	# fltr2 = {}
	# if filters.get("serial_no"):
	# 		fltr1.update({'serial_no':filters.get("serial_no")})
	# if filters.get("client_name"):
	# 		fltr1.update({'customer':filters.get("client_name")})
	# if filters.get("from_date") and filters.get("to_date"):
	# 	fltr2.update({'failure_date_and_time':['between',(filters.get('from_date'),filters.get('to_date'))]})
	# for tk in frappe.get_all("Task",fltr2,['failure_date_and_time','asset','name']):
	# 	fltr1.update({'name':tk.get('asset')})
	fltr={}
	if filters.get("serial_no"):
		fltr.update({"serial_no":filters.get("serial_no")})
	if filters.get("company"):
		fltr.update({"company":filters.get("company")})
	if filters.get("company"):
		fltr.update({"company":filters.get("company")})
	for ast in frappe.get_all("Asset",fltr,['name','customer','serial_no','item_code','project']):
		count=get_count(ast.name,ast.item_code,filters)
		if count>=1:
			data.append({
					"customer":frappe.db.get_value("Project",ast.project,"customer"),
					"serial_no":ast.get('serial_no'),
					"machine_model":ast.name,
					"calls":count
			})
	
	return data

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
	# for cu_rd in frappe.get_all("Asset Readings",{"parenttype":"Task","parentfield":"current_reading","parent":name},['asset','date','reading_2','reading']):
	# 	for ls_rd in frappe.get_all("Asset Readings",filters={"parenttype":"Task","parentfield":"last_readings","parent":name,"asset":cu_rd.asset},fields=['asset','date','reading_2','reading'],order_by="date desc",limit=1):
	# 		days_diff=(getdate(cu_rd.date)-getdate(ls_rd.date)).days
	# 		reading_diff=int(cu_rd.reading or 0)-int(ls_rd.reading or 0)
	# 		reading2_diff=int(cu_rd.reading_2 or 0)-int(ls_rd.reading_2 or 0)

	# 		if days_diff >= 1 and days_diff <= 30 and frappe.db.get_value("Item",item_code,'avg_duty_cycle')>reading2_diff or frappe.db.get_value("Item",item_code,'avg_duty_cycle')>reading_diff:
	# 			count+=1
	return count
				
	
	
	
	