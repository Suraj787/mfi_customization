# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime ,timedelta, date
import calendar
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from frappe.model.mapper import get_mapped_doc
import json
import datetime
from datetime import datetime, timedelta

# def validate(doc,method):
   # make_issues_on_PM_call_interval(doc)

def make_issues_on_PM_call_interval(doc):
   expected_end_date = datetime.strptime(doc.expected_end_date, '%Y-%m-%d')
   expected_start_date = datetime.strptime(doc.expected_start_date, '%Y-%m-%d')
   if expected_end_date and doc.pm_call_interval > 0 and datetime.today() <= expected_end_date:
      expected_end_date = datetime.strptime(doc.expected_end_date, '%Y-%m-%d')
      expected_start_date = datetime.strptime(doc.expected_start_date, '%Y-%m-%d')
      till_end_date = (expected_end_date- expected_start_date).days
      date_list = [expected_start_date + timedelta(days=x) for x in range(0,till_end_date,doc.pm_call_interval)]
      if date.today() in [dt.date() for dt in date_list]:
         for a in doc.machine_readings:
            if a.asset and not check_duplicate_issue(doc, a.asset):
               issue_doc = frappe.new_doc('Issue')
               issue_doc.subject = "PM Call Interval"
               issue_doc.customer = doc.customer
               issue_doc.asset = a.asset
               issue_doc.location = frappe.get_value('Asset',{'name':a.asset},'location')
               issue_doc.type_of_call = "PM"
               issue_doc.issue_type = "Preventive"
               issue_doc.failure_date_and_time = datetime.today()
               issue_doc.raise_by_contact = frappe.get_value('Customer',{'name':doc.customer},'customer_name')
               issue_doc.project = doc.name
               issue_doc.status = "Open"
               issue_doc.serial_no = frappe.get_value('Asset',{'name':a.asset},'serial_no')
               issue_doc.save()

def check_duplicate_issue(doc, asset):
    return  frappe.db.get_all("Issue", filters={
            'subject' : "PM Call Interval",
            'customer' : doc.customer,
            'asset' : asset,
            'project':doc.name,
            'name': ['!=', doc.name]
        }, limit=1)


# @frappe.whitelist()
# def fetch_asset_maintenance_team(maintenance_team):
#     doc=frappe.get_doc('Asset Maintenance Team',maintenance_team)
#     resp={
#         'manager':doc.maintenance_manager,
#         'name':doc.maintenance_manager_name,
#     }
#     team=[]
#     for d in doc.get('maintenance_team_members'):
#         team.append({'member':d.get('team_member'),
#                     'name':d.get('full_name'),
#                     'role':d.get('maintenance_role')})
#     resp.update({'team_members_list':team})
#     return resp

# @frappe.whitelist()
# def make_asset_delivery_note(source_name, target_doc=None):
#     def set_missing_values(source,target):
#         if source.customer:
#             target.customer_name=frappe.db.get_value("Customer",source.customer,"customer_name")
#         if source.sales_order:
#             sales_order_doc=frappe.get_doc("Sales Order",source.sales_order)
#             for d in sales_order_doc.get("asset_quotation_selection"):
#                 if frappe.db.get_value("Item",d.asset,'is_fixed_asset'):
#                     target.append("asset_models",{
#                         "asset_model":frappe.db.get_value("Item",d.asset,'stock_item'),
#                         "model_name":d.asset_name,
#                         "qty":d.qty
#                     })
#     return get_mapped_doc("Project", source_name, {
#         "Project": {
#             "doctype": "Asset Delivery Note"
#         }
#     }, target_doc,set_missing_values)

# def validate(doc,method):
#     if doc.sales_order:
#         for d in frappe.get_all("Sales Order",{"name":doc.sales_order},['total_contract_amount']):
#             doc.estimated_costing=d.total_contract_amount

# @frappe.whitelist()
# def make_asset_task(doc):
#     doc = json.loads(doc)
#     existed_task_list = [t.name for t in frappe.db.get_all("Task", {'project': doc.get('name'), "type_of_call" :"Installation"} ,'name')]
#     if existed_task_list:
#         frappe.msgprint("Task <b>'{0}'</b> already exist.".format(",".join(map(str,existed_task_list))))
#     else:
#         asset_list = [a.name for a in frappe.db.get_all("Asset", {'project': doc.get('name')} ,'name')]
#         if asset_list :
#             out = []
#             for asset in asset_list:
#                 task_doc = frappe.new_doc("Task")
#                 task_doc.subject = "Installation-"+asset
#                 task_doc.type_of_call = "Installation"
#                 task_doc.project = doc.get('name')
#                 task_doc.completed_by = "s.karuturi@groupmfi.com"
#                 task_doc.customer= doc.get('customer')
#                 task_doc.save() 
#                 out.append(task_doc)
#             return [p.name for p in out]

@frappe.whitelist()
def date_invoice_cycle(expected_end_date,invoicing_starts_from,invoice_cycle_option):
    monthlylist=[]
    yearlylist=[]
    quarterlylist =[]
    half_yearlist =[]
    endate=str(expected_end_date)
    endate_strp =datetime. strptime(endate, "%Y-%m-%d")
    endateformating = datetime(endate_strp.year,endate_strp.month,endate_strp.day)
    invoicing_start_date = str(invoicing_starts_from)
    invoicing_strp=datetime. strptime(invoicing_start_date,"%Y-%m-%d")
    invoce_startformating=datetime(invoicing_strp.year,invoicing_strp.month,invoicing_strp.day)
    [monthlylist.append(monthly.date()) for monthly in rrule.rrule(rrule.MONTHLY,dtstart=invoce_startformating,until=endateformating)]
    [yearlylist.append(yearly.date())for yearly in rrule.rrule(rrule.YEARLY,dtstart=invoce_startformating,until=endateformating)]
    if invoce_startformating> endateformating:
       frappe.throw("Invoicing Starts from date can't before Expected End Date")
    if invoice_cycle_option == "Quarterly":
       add_quarter_Months = relativedelta(months=3)
       while invoce_startformating <= endateformating:
          quarterlylist.append(invoce_startformating.date())
          invoce_startformating += add_quarter_Months
    if invoice_cycle_option == "Half Yearly":
       add_half_year_Month = relativedelta(months=6)
       while invoce_startformating <= endateformating:
          half_yearlist.append(invoce_startformating.date())
          invoce_startformating += add_half_year_Month
    
    
    return monthlylist,yearlylist,quarterlylist ,half_yearlist

@frappe.whitelist()
def contract_period(expected_start_date,contract_period):
    start_date=str(expected_start_date)
    start_strp=datetime. strptime(start_date,"%Y-%m-%d")
    stratformate=datetime(start_strp.year,start_strp.month,start_strp.day)
    current = stratformate + relativedelta(months=(int(contract_period)))
    return current.date()

    
    
