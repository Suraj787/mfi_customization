# Copyright (c) 2022, bizmap technologies and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from datetime import datetime
import calendar
from dateutil.relativedelta import relativedelta
def execute(filters=None):
    data = prepare_data(filters)
    columns=get_columns(filters) +  additional_columns(filters)
    #columns1=additional_columns(filters) 
    return columns, data
	
	
def get_columns(filters=None):
        return[
          {
	     "label": "ACCOUNT CODE",
	     "fieldtype": "Link",
	     "fieldname": "customer",
	     'width':150,
	     "options":"customer"
	},
	{
	
	     "label": "Customer Name",
	     "fieldtype": "Data",
	     "fieldname": "customer_name",
	     'width':150,
	     "options":"Customer"
	
	},
	{
	  "label":"Asset",
	  "fieldtype":"Link",
	  "fieldname":"name",
	  'width':150,
	  "options":"Asset"
	  
	},
	{
	
	     "label": "Invoice Cycle",
	     "fieldtype": "Data",
	     "fieldname": "invoice_cycle",
	     'width':120
	},
	{
	     "label":"Agreement Start Date",
	     "fieldtype":"Date",
	     "fieldname":"expected_start_date",
	     "width":160
	   
	},
	{
	
	     "label":"Agreement Expiry Date",
	     "fieldtype":"Date",
	     "fieldname":"expected_end_date",
	     "width":160
	     
	},
	{
	
	     "label":"Wastage Agreed",
	     "fieldtype":"float",
	     "fieldname":"wastage_agreed_",
	     "width":160
	     
	
	},
	{
	
	     "label":"Mono Reading",
	     "fieldtype":"float",
	     "fieldname":"",
	     "width":120
	     
	
	},
	{
	
	     "label":"Colour Reading",
	     "fieldtype":"float",
	     "fieldname":"",
	     "width":120
	     
	
	},
	{
	
	     "label":"Rate",
	     "fieldtype":"float",
	     "fieldname":"",
	     "width":120
	     
	
	},
	{
	
	     "label":"Ammount",
	     "fieldtype":"float",
	     "fieldname":"",
	     "width":120
	     
	
	},
	{
	
	     "label":"Status",
	     "fieldtype":"Data",
	     "fieldname":"",
	     "width":120
	     
	
	}
	
]


def prepare_data(filters):
    data =[]
    fltr={}
    if filters.get("name"):
       fltr.update({"name":filters.get("name")})
    for i in     frappe.get_all('Project',filters=fltr,fields=['name','customer','invoice_cycle',"expected_start_date","expected_end_date","wastage_agreed_"]):
        row={}
        row.update(i)
        row.update({"customer":i.customer,"customer_name":frappe.db.get_value("Customer",{"name":i.customer},"customer_name"),"invoice_cycle":i.invoice_cycle,"expected_start_date":i.expected_start_date,
     "expected_end_date":i.expected_end_date,"name":frappe.db.get_value("Asset",{"project":i.name},"name")})
        data.append(row)
        invoice_shedule_date=frappe.db.sql(f"""SELECT date from `tabInvoice Schedule` where parent="{filters.get("name")}" ORDER BY date """,as_dict=1)
        for p in  invoice_shedule_date:
            print(p.date)
            for k in frappe.db.sql(f"""SELECT SUM(total) from `tabMachine Reading` where asset="{frappe.db.get_value("Asset",{"project":filters.get("name")},"name")}" AND reading_date<='{p.date +relativedelta(months=1)}' """,as_dict=1):
                row.update({f'{p.date}':k['SUM(total)']})
    return data

def additional_columns(filters):
    columns1=[]
    fltr={}
    row={}
    if filters.get("name"):
       fltr.update({"name":filters.get("name")})
       invoice_shedule_date=frappe.db.sql(f"""SELECT date from `tabInvoice Schedule` where parent="{filters.get("name")}" ORDER BY date """,as_dict=1)
       for j in  invoice_shedule_date:
           columns1.append({'fieldname':f'{j.date}','label':j.date.strftime("%B-%Y-%d"),'fieldtype':'Data','width':150})
    return columns1
       

	

