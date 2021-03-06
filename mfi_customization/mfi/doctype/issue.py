# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import today,getdate

def validate(doc,method):
	email_validation(doc)
	# machine_reading=""
	for d in doc.get("current_reading"):
		# machine_reading=d.machine_reading
		d.total=( int(d.get('reading') or 0)  + int(d.get('reading_2') or 0))
		if d.idx>1:
			frappe.throw("More than one row not allowed")
	if doc.status=="Closed":
		for t in frappe.get_all('Task',filters={'issue':doc.name},fields=['name','status']):
			if t.status != 'Completed':
				frappe.throw("Please Complete <b>Issue '{0}'</b>".format(t.name))
		if len(frappe.get_all('Task',filters={'issue':doc.name},fields=['name','status']))==0:
			if doc.get('current_reading') and len(doc.get('current_reading'))==0:
				frappe.throw("Please add Asset readings before closing issue")
	last_reading=today()
	if doc.asset and len(doc.get("last_readings"))==0:
		# doc.set("last_readings", [])
		fltr={"project":doc.project,"asset":doc.asset,"reading_date":("<=",last_reading)}
		# if machine_reading:
		# 	fltr.update({"name":("!=",machine_reading)})
		for d in frappe.get_all("Machine Reading",filters=fltr,fields=["name","reading_date","asset","black_and_white_reading","colour_reading","total","machine_type"],limit=1,order_by="reading_date desc,name desc"):
			doc.append("last_readings", {
				"date" : d.get('reading_date'),
				"type" : d.get('machine_type'),
				"asset":d.get('asset'),
				"reading":d.get('black_and_white_reading'),
				"reading_2":d.get('colour_reading'),
				"total":( int(d.get('black_and_white_reading') or 0)  + int(d.get('colour_reading') or 0))
				})

def on_change(doc,method):
	validate_reading(doc)

def email_validation(doc):
	if doc.email_conact and "@" not in 	doc.email_conact:
		frappe.throw("Email Not Valid")

@frappe.whitelist()
def make_task(source_name, target_doc=None):
	return get_mapped_doc("Issue", source_name, {
		"Issue": {
			"doctype": "Task"
		}
	}, target_doc)

@frappe.whitelist()
def get_asset_list(doctype, txt, searchfield, start, page_len, filters):
	location=''
	if filters.get('location'):
		location="where location='{0}'".format(filters.get('location'))

	return frappe.db.sql("""select name,asset_name
		from `tabAsset`  {location}"""
		.format(location=location))

# @frappe.whitelist()
# def get_asset_in_issue(doctype, txt, searchfield, start, page_len, filters):
# 	cond1=''
# 	cond2=''
# 	if filters.get("customer"):
# 			print(filters.get("customer"),"***************")
# 			cond2+="where customer ='{0}'".format(filters.get("customer"))

# 	if filters.get("location"):
# 			cond1+="where location='{0}'".format(filters.get("location"))
		
# 	data = frappe.db.sql("""select asset from `tabAsset Serial No` where asset IN (select name from `tabAsset` {0} and project = (select name
# 		from `tabProject`  {1}))
# 		""".format(cond1,cond2))
# 	print(data)
# 	return data
@frappe.whitelist()
def get_asset_in_issue(doctype, txt, searchfield, start, page_len, filters):
	fltr1 = {}
	fltr2 = {}
	asst = {}
	lst = []
	if filters.get('customer'):
		fltr1.update({'customer':filters.get('customer')})
	if filters.get("location"):
		fltr2.update({'location':filters.get('location')})
	if txt:
		fltr2.update({'name':("like", "{0}%".format(txt))})
	for i  in frappe.get_all('Project',fltr1,['name']):
		fltr2.update({'project':i.get('name'),'docstatus':1})
		for ass in frappe.get_all('Asset',fltr2,['name']):
			if ass.name not in lst:
				lst.append(ass.name)
	return [(d,) for d in lst]	


@frappe.whitelist()
def get_serial_no_list(doctype, txt, searchfield, start, page_len, filters):
 	if txt:
 		filters.update({"name": ("like", "{0}%".format(txt))})
 	return frappe.get_all("Asset Serial No",filters=filters,fields = ["name"], as_list=1)

@frappe.whitelist()
def get_customer(serial_no,asset):
	project = frappe.get_value('Asset',{'serial_no':serial_no},'project')
	customer = frappe.db.get_value('Project',{'name':project},'customer')
	name =  frappe.db.get_value('Customer',{'name':customer},'name')
	return name

@frappe.whitelist()
def get_location(doctype, txt, searchfield, start, page_len, filters):
	lst = []
	fltr = {}
	if txt:
			fltr.update({"location": ("like", "{0}%".format(txt))})
	for i in frappe.get_all('Project',filters,['name']):
		fltr.update({'project':i.get('name')})
		for a in frappe.get_all('Asset',fltr,['location']):
			if a.location not in lst:
				lst.append(a.location)
	return [(d,) for d in lst]	


@frappe.whitelist()
def get_asset_on_cust(doctype, txt, searchfield, start, page_len, filters):
		fltr = {}
		asst = {}
		lst = []
		if filters.get('customer'):
			fltr.update({'customer':filters.get('customer')})
		if txt:
			asst.update({'name':("like", "{0}%".format(txt))})
		# asst.update()
		for i  in frappe.get_all('Project',fltr,['name']):
			asst.update({'project':i.get('name'),'docstatus':1})
			for ass in frappe.get_all('Asset',asst,['name']):
				if ass.name not in lst:
					lst.append(ass.name)
		return [(d,) for d in lst]	
		


@frappe.whitelist()
def get_asset_serial_on_cust(doctype, txt, searchfield, start, page_len, filters):
		fltr = {}
		asst = {}
		lst = []
		if filters.get('customer'):
			fltr.update({'customer':filters.get('customer')})
		if txt:
			asst.update({'serial_no':("like", "{0}%".format(txt))})
		# asst.update()
		for i  in frappe.get_all('Project',fltr,['name']):
			asst.update({'project':i.get('name'),'docstatus':1})
			for ass in frappe.get_all('Asset',asst,['serial_no']):
				if ass.serial_no not in lst:
					lst.append(ass.serial_no)
		return [(d,) for d in lst]	

@frappe.whitelist()
def get_serial_on_cust_loc(doctype, txt, searchfield, start, page_len, filters):
	# data = frappe.db.sql("""select name from `tabProject` """)
	fltr1 = {}
	fltr2 = {}
	lst = []
	if filters.get('customer'):
		fltr1.update({'customer':filters.get('customer')})
	if filters.get('location'):
		fltr2.update({'location':filters.get('location')})
	if txt:
		fltr2.update({'serial_no':txt})
	for i in frappe.get_all('Project',fltr1,['name']):
		fltr2.update({'project':i.get('name'),'docstatus':1})
		for j in frappe.get_all('Asset',fltr2,['serial_no']):
			if j.serial_no not in lst:
					lst.append(j.serial_no)
	return [(d,) for d in lst]	

def set_reading_from_issue_to_task(doc,method):
	for tsk in frappe.get_all("Task",{"issue":doc.name}):
		task_doc=frappe.get_doc('Task',{'name':tsk.name})
		duplicate=[]
		for d in doc.get('current_reading'):
			for pr in task_doc.get('current_reading'):
				if d.type== pr.type and d.asset == pr.asset and d.reading == pr.reading:
					duplicate.append(d.idx)
		for d in doc.get('current_reading'):
			if d.idx not in duplicate:
				task_doc.append("current_reading", {
				"date" : d.get('date'),
				"type" : d.get('type'),
				"asset":d.get('asset'),
				"reading":d.get('reading'),
				"reading_2":d.get('reading_2')
				})
				task_doc.save()

def validate_reading(doc):
	for cur in doc.get('current_reading'):
		cur.total=( int(cur.get('reading') or 0)  + int(cur.get('reading_2') or 0))
		if doc.get('last_readings'):
			for lst in doc.get('last_readings'):
				lst.total=( int(lst.get('reading') or 0)  + int(lst.get('reading_2') or 0))
				if int(lst.total)>int(cur.total):
					frappe.throw("Current Reading Must be Greater than Last Reading")
				if getdate(lst.date)>getdate(cur.date):
					frappe.throw("Current Reading <b>Date</b> Must be Greater than Last Reading")