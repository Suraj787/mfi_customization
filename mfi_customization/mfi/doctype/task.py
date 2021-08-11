# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils.data import getdate,today
from frappe.model.mapper import get_mapped_doc
from frappe.permissions import add_user_permission

def validate(doc,method):
	# machine_reading=""
	for d in doc.get("current_reading"):
		# machine_reading=d.machine_reading
		if d.idx>1:
			frappe.throw("More than one row not allowed")

	last_reading=today()
	if doc.asset and  len(doc.get("last_readings"))==0:
		# doc.set("last_readings", [])
		fltr={"project":doc.project,"asset":doc.asset,"reading_date":("<=",last_reading)}
		# if machine_reading:
			# fltr.update({"name":("!=",machine_reading)})
		for d in frappe.get_all("Machine Reading",filters=fltr,fields=["name","reading_date","asset","black_and_white_reading","colour_reading","total","machine_type"],limit=1,order_by="reading_date desc,name desc"):
			doc.append("last_readings", {
				"date" : d.get('reading_date'),
				"type" : d.get('machine_type'),
				"asset":d.get('asset'),
				"reading":d.get('black_and_white_reading'),
				"reading_2":d.get('colour_reading'),
				"total":( int(d.get('black_and_white_reading') or 0)  + int(d.get('colour_reading') or 0))
				})

	set_field_values(doc)

	if doc.get('__islocal'):
		for d in frappe.get_all("Task",{"issue":doc.issue}):
			frappe.throw("Task <b>{0}</b> Already Exist Against This Issue".format(doc.name))
	else:
		create_user_permission(doc)
		
def after_insert(doc,method):
	if doc.get('issue'):
		frappe.db.set_value('Issue',doc.get('issue'),'status','Assigned')
	if doc.failure_date_and_time and doc.issue:
		doc.failure_date_and_time=frappe.db.get_value("Issue",doc.issue,"failure_date_and_time")
	if doc.issue:
		doc.description=frappe.db.get_value("Issue",doc.issue,"description")

	
	create_user_permission(doc)

	# docperm = frappe.new_doc("DocShare")
	# docperm.update({
	# 		"user": doc.completed_by,
	# 		"share_doctype": 'Task',
	# 		"share_name": doc.name ,
	# 		"read": 1,
	# 		"write": 1
	# 	})
	# docperm.save(ignore_permissions=True)
	
def on_change(doc,method):
	if doc.get("issue"):
		set_reading_from_task_to_issue(doc)
	validate_reading(doc)
	create_machine_reading(doc)
	if doc.issue and doc.status != 'Open':
		frappe.db.set_value("Issue",doc.issue,'status',doc.status)	
		if doc.status == 'Completed':
			validate_if_material_request_is_not_submitted(doc)
			attachment_validation(doc)
			issue=frappe.get_doc("Issue",doc.issue)
			issue.status="Task Completed"
			issue.set("task_attachments",[])
			for d in doc.get("attachments"):
				issue.append("task_attachments",{
					"attach":d.attach
				})
			issue.save()
		elif doc.status=="Working" and doc.attended_date_time:	
			frappe.db.set_value("Issue",doc.issue,'first_responded_on',doc.attended_date_time)		

def after_delete(doc,method):
	for t in frappe.get_all('Asset Repair',filters={'task':doc.name}):
		frappe.delete_doc('Asset Repair',t.name)

def set_field_values(doc):
	if doc.get("issue"):
		issue = frappe.get_doc("Issue",{"name":doc.get("issue")})		
		if doc.get("completed_by"):
			issue.assign_to = doc.get("completed_by")
		if doc.get("assign_date"):
			issue.assign_date = doc.get("assign_date")
		issue.save()
	
@frappe.whitelist()
def make_material_req(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.company=frappe.db.get_value("Employee",{"user_id":frappe.session.user},"company")
	doclist = get_mapped_doc("Task", source_name, {
		"Task": {
			"doctype": "Material Request",
			"name":"custom_task"
		}
	}, target_doc,set_missing_values )

	return doclist


@frappe.whitelist()
def make_asset_movement(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
	   customer = frappe.db.get_value("Task", source_name,'customer')
	   company = frappe.db.get_value("Project",{"customer":customer},'company')
	   target.purpose = "Transfer"
	   target.company = company
	   target.task=source_name



	doclist = get_mapped_doc("Task", source_name, {
		"Task": {
			"doctype": "Asset Movement",
			
		}
	}, target_doc ,set_missing_values, ignore_permissions=ignore_permissions)

	return doclist

@frappe.whitelist()
def set_readings(project,asset,target_doc=None):
	
	reading_list=[]
	for d in frappe.get_all('Asset Readings',filters={'parent':project,'asset':asset,'parenttype':'Project'},fields=['date','type','asset','reading','reading_2']):
		
		reading_list.append({
			'date':d.date,
			'type':d.type,
			'asset':d.asset,
			'black_white':d.get("reading"),
			'colour':d.get("reading_2")
		})
	
	return reading_list


def set_item_from_material_req(doc,method):
	if doc.get('task_') and doc.status=="Issued":
		task=frappe.get_doc('Task',doc.get('task_'))
		items=[]
		for t in task.get('refilled__items'):
			items.append(t.item)
		for d in doc.get('items'):
			if d.get('item_code') not in items:
				task.append("refilled__items", {
							"item": d.get('item_code'),
							"warehouse": d.get('warehouse'),
							"qty": d.get('qty')
						})
		task.material_request=doc.name
		task.save()

@frappe.whitelist()
def get_tech(doctype, txt, searchfield, start, page_len, filters):
	tch_lst = []
	fltr = {}
	dct = {}
	if txt:
			fltr.update({"full_name": ("like", "{0}%".format(txt))})
	for i in frappe.get_roles(filters.get("user")):
		
		for ss in frappe.db.get_all('Support Setting Table',{'back_office_team_role':i},['technician_role','back_office_team_role']):
			for usr in frappe.get_all('User',fltr,['name','full_name']):
				if ss.get('technician_role') in frappe.get_roles(usr.get("name")) and not usr.get("name") == 'Administrator':
					
					if usr.name not in tch_lst:
						tch_lst.append(usr.name)
						dct.update({usr.full_name:usr.name})
	
	return [(y,d) for d,y in dct.items()]


@frappe.whitelist()
def check_material_request_status(task):
	flag = False
	
	for i in frappe.get_all('Material Request',{'task_':task},['status']):
		if i.get('status') not in ['Stopped','Cancelled','Issued']:
			flag = True
	return flag
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
def get_asset_in_task(doctype, txt, searchfield, start, page_len, filters):
	cond1 = ''
	cond2 = ''
	cond3 = ''
	if txt:
		cond3 = "and name = '{0}'".format(txt)
	if filters.get("customer"):
			cond2+="where customer ='{0}'".format(filters.get("customer"))

	if filters.get("location"):
			cond1+="and location='{0}'".format(filters.get("location"))
		
	data = frappe.db.sql("""select asset from `tabAsset Serial No` 
			where asset IN (select name from 
			`tabAsset` where docstatus = 1  {0} 
			and project = (select name
			from `tabProject`  {1} {2}))
		""".format(cond1,cond2,cond3))
	return data

@frappe.whitelist()
def get_serial_no_list(doctype, txt, searchfield, start, page_len, filters):
 	if txt:
 		filters.update({"name": ("like", "{0}%".format(txt))})
		
 	return frappe.get_all("Asset Serial No",filters=filters,fields = ["name"], as_list=1)


@frappe.whitelist()
def get_serial_on_cust_loc(doctype, txt, searchfield, start, page_len, filters):
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
def get_customer(serial_no,asset):
	project = frappe.get_value('Asset',{'serial_no':serial_no},'project')
	customer = frappe.db.get_value('Project',{'name':project},'customer')
	name =  frappe.db.get_value('Customer',{'name':customer},'name')
	return name
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


def create_machine_reading(doc):
	for d in doc.get('current_reading'):
		if len(frappe.get_all("Machine Reading",{"task":doc.name,"project":doc.project,"asset":d.get('asset'),"reading_date":d.get('date')}))<1:
			mr=frappe.new_doc("Machine Reading")
			mr.reading_date=d.get('date')
			mr.asset=d.get('asset')
			mr.black_and_white_reading=d.get("reading")
			mr.colour_reading=d.get("reading_2")
			mr.machine_type=d.get('type')
			mr.total=d.get("total")
			mr.project=doc.project
			mr.task=doc.name
			mr.save()
			# d.machine_reading=mr.name
	
def set_reading_from_task_to_issue(doc):
	issue_doc=frappe.get_doc('Issue',{'name':doc.get("issue")})
	for d in doc.get('current_reading'):
		if issue_doc.get("current_reading") and len(issue_doc.get("current_reading"))>0:
			for isu in doc.get("current_reading"):
				isu.date=d.get('date')
				isu.type=d.get('type')
				isu.asset=d.get('asset')
				isu.reading=d.get('reading')
				isu.reading_2=d.get('reading_2')
				issue_doc.save()
		else:
			issue_doc.append("current_reading",{
				"date":d.get('date'),
				"type":d.get('type'),
				"asset":d.get('asset'),
				"reading":d.get('reading'),
				"reading_2":d.get('reading_2')
			})
	if doc.get("asset"):
		issue_doc.asset = doc.get("asset")
	if doc.get("serial_no"):
		issue_doc.serial_no = doc.get("serial_no")
	issue_doc.save()

def validate_reading(doc):
	for cur in doc.get('current_reading'):
		cur.total=( int(cur.get('reading') or 0)  + int(cur.get('reading_2') or 0))
		for lst in doc.get('last_readings'):
			lst.total=( int(lst.get('reading') or 0)  + int(lst.get('reading_2') or 0))
			if int(lst.total)>int(cur.total):
				frappe.throw("Current Reading Must be Greater than Last Reading")
			if getdate(lst.date)>getdate(cur.date):
				frappe.throw("Current Reading <b>Date</b> Must be Greater than Last Reading")

def validate_if_material_request_is_not_submitted(doc):
	for mr in frappe.get_all("Material Request",{"task":doc.name,"docstatus":0}):
		frappe.throw("Material Request is not completed yet. Name <b>{0}</b>".format(mr.name))

def attachment_validation(doc):
	if not doc.attachments or  len(doc.attachments)==0:
		frappe.throw("Cann't Completed Task Without Attachment")
	
def create_user_permission(doc):
	if len(frappe.get_all("User Permission",{"allow":"Task","for_value":doc.name,"user":doc.completed_by}))==0:
		for d in frappe.get_all("User Permission",{"allow":"Task","for_value":doc.name}):
			frappe.delete_doc("User Permission",d.name)
		add_user_permission("Task",doc.name,doc.completed_by)

	for emp in frappe.get_all("Employee",{"user_id":doc.completed_by},['material_request_approver']):
		if emp.material_request_approver:
			for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
				if emp2.user_id:
					add_user_permission("Task",doc.name,emp2.user_id)
