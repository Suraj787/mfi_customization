# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import  getdate,today,add_days,flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data
def get_columns(filters = None):
    return[
            {
            "label":"Month",
            "fieldname":"month",
            "fieldtype":"Data" ,
            "width":110 

        },{
            "label":"Technician Name",
            "fieldname":"techn_name",
            "fieldtype":"Data",
            "width":190

        },{
            "label":">4",
            "fieldname":"gt4",
            "fieldtype":"Data"  

        },{
            "label":"<4",
            "fieldname":"lt4",
            "fieldtype":"Data"  

        },{
            "label":">8",
            "fieldname":"gt8",
            "fieldtype":"Data"  

        },{
            "label":">48",
            "fieldname":"gt48",
            "fieldtype":"Data"  

        },{
            "label":"Total Assigned Task",
            "fieldname":"asset_cnt",
            "fieldtype":"Int" ,
            "width":80

        },
        	{
			"label":"Repetitive",
			"fieldname":"repetitive",
			"fieldtype":"Data"	
		},
        ]

#calculate response_time_diff in hours with holiday validation - 05/08/21[Anuradha]
def get_working_hrs(call_to, assign_date, attended_date_time, company):
    holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
    where h1.parent = h2.name and h1.holiday_date between %s and %s
    and h2.company = %s""", (assign_date, attended_date_time, company))[0][0]
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

def get_data(filters):
    data=[]
    fltr = {}
    fltr1 ={}
    if filters.get("techn_name"):
        fltr1.update({"email":filters.get("techn_name")})
    if filters.get("from_date") and filters.get("to_date"):
        fltr.update({'assign_date':['between',(filters.get('from_date'),filters.get('to_date'))]})
    if filters.get("c_name"):
        fltr.update({"company":filters.get("c_name")})
    for ur in frappe.get_all("User",fltr1,["name","full_name"]):
        
        row={
                "techn_name":ur.full_name,
            }
        
        gt4_count=0
        lt4_count=0
        gt8_count=0
        gt48_count=0
        month =[]
        mon_st =""
        fltr.update({'completed_by':ur.name,"type_of_call":"CM"})
        repetitive=0
        for ast in frappe.get_all("Asset",{"company":filters.get("company"),"name":["IN",get_asset_list(fltr)]},['name','customer','serial_no','item_code','project']):
            repetitive+=get_count(ast.name,ast.item_code,filters)
        for tk in frappe.get_all("Task",fltr,['attended_date_time','assign_date','asset','completed_by', 'issue']):
            if tk.get('attended_date_time') and tk.get('assign_date'):
                response_time_diff = (tk.get("attended_date_time") - tk.get('assign_date')) 
                company = fltr.get('company') if fltr.get('company') else frappe.db.get_value('Issue', {'name': tk.issue}, 'company') or "MFI MAROC SARL"
                response_time = get_working_hrs(response_time_diff, tk.get('assign_date'), tk.get('attended_date_time'), company)
                if response_time >= 4.01:
                    gt4_count+=1
                if response_time <= 4:
                    lt4_count+=1
                if response_time >= 8:
                    gt8_count+=1
                if response_time >= 48:
                    gt48_count+1
                
                month.append(tk.get("assign_date").strftime("%B"))
        for i in set(month):
            mon_st += "{0},".format(i)  
        asset_cnt = len(frappe.get_all("Task",{"type_of_call":"CM",'completed_by':ur.name,"company":fltr.get('company'),"status":("!=","Cancelled"),'assign_date':['between',(filters.get('from_date'),filters.get('to_date'))]}))      
        mon_st = mon_st.rstrip(',')
        row.update({
            "month":mon_st,
            "gt4":gt4_count,
            "lt4":lt4_count,
            "gt8":gt8_count,
            "gt48":gt48_count,
            "asset_cnt":asset_cnt,
            'repetitive':repetitive
        })
        if len(frappe.get_all("Task",{'completed_by':ur.name})) > 0:
            data.append(row)
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

	return count


def get_asset_list(filters):
	return [d.asset for d in frappe.get_all('Task',filters,['asset'])]

    