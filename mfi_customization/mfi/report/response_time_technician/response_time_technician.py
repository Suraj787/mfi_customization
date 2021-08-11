# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data
def get_columns(filters = None):
    return[
            {
            "label":"Month",
            "fieldname":"month",
            "fieldtype":"Data"  

        },{
            "label":"Technician Name",
            "fieldname":"techn_name",
            "fieldtype":"Data"  

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
            "label":"Repetitive",
            "fieldname":"asset_cnt",
            "fieldtype":"Data"  

        }]

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
    for ur in frappe.get_all("User",fltr1):
        row={
                "techn_name":ur.name,
            }
        
        gt4_count=0
        lt4_count=0
        gt8_count=0
        gt48_count=0
        month =[]
        mon_st =""
        asset_cnt =0
        fltr.update({'completed_by':ur.name})
        for tk in frappe.get_all("Task",fltr,['attended_date_time','assign_date','asset','completed_by', 'issue']):
            if tk.get('attended_date_time') and tk.get('assign_date'):
                response_time_diff = (tk.get("attended_date_time") - tk.get('assign_date')) 
                company = fltr.get('company') if fltr.get('company') else frappe.db.get_value('Issue', {'name': tk.issue}, 'company') or "MFI MAROC SARL"
                response_time = get_working_hrs(response_time_diff, tk.get('assign_date'), tk.get('attended_date_time'), company)
                if response_time > 4:
                    gt4_count+=1
                if response_time < 4:
                    lt4_count+=1
                if response_time > 8:
                    gt8_count+=1
                if response_time > 8:
                    gt48_count+1
                asset_cnt = len(frappe.get_all("Task",{'completed_by':ur.name,'asset':tk.asset}))
                month.append(tk.get("assign_date").strftime("%B"))
        for i in set(month):
            mon_st += "{0},".format(i)  
                    
        mon_st = mon_st.rstrip(',')
        row.update({
            "month":mon_st,
            "gt4":gt4_count,
            "lt4":lt4_count,
            "gt8":gt8_count,
            "gt48":gt48_count,
            "asset_cnt":asset_cnt
        })
        if len(frappe.get_all("Task",{'completed_by':ur.name})) > 0:
            data.append(row)
    return data