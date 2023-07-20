# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
import json
from frappe.utils import time_diff_in_hours, now_datetime
from frappe.utils.data import today
from frappe.model.mapper import get_mapped_doc
from frappe.permissions import add_user_permission
from frappe.core.doctype.communication.email import make
from mfi_customization.mfi.doctype.project import get_customer_emails
from mfi_customization.mfi.doctype.issue import set_company


def validate(doc,method):
	set_company(doc)
	set_actual_time(doc)
	send_task_completion_email(doc)
	send_task_escalation_email(doc)
	# machine_reading=""
	for d in doc.get("current_reading"):
		# machine_reading=d.machine_reading
		if d.idx>1:
			frappe.throw("More than one row not allowed")

	last_reading=today()
	#last_reading child table row will be less then 2 idx(3 row) then it will insert
	if doc.asset and len(doc.get("last_readings"))<=3 and doc.status == 'Open':
		doc.set("last_readings", [])
		l = []
		for c_r in doc.current_reading:
			l.append(c_r.total)
		fltr={"project":doc.project,"asset":doc.asset,"reading_date":("<=",last_reading)}
		mr_all = frappe.get_all("Machine Reading",filters=fltr,fields=["name","reading_date","asset","black_and_white_reading","colour_reading","total","machine_type"],limit=4,order_by="reading_date desc,name desc")
		for d in range(len(mr_all)-1):
			if len(mr_all)>0 and mr_all[d]['total']!= l[0] and int(mr_all[d]['total'])>0 and doc.type_of_call == "Toner":
				print(f"\n\n\n\n\nttttt,{int(mr_all[d]['total'])}\n\n\n\n\n")
				print(f"\n\n\n\n\nttttt+++++++++11111111,{int(mr_all[d+1]['total'])}\n\n\n\n\n")
				doc.append("last_readings", {
					"date" : mr_all[d]['reading_date'],
					"type" : mr_all[d]['machine_type'],
					"asset":mr_all[d]['asset'],
					"reading":mr_all[d]['black_and_white_reading'],
					"reading_2":mr_all[d]['colour_reading'],
					"total":( int(mr_all[d]['black_and_white_reading'] or 0)  + int(mr_all[d]['colour_reading'] or 0)),
					"yeild": int(mr_all[d]['total']) - int(mr_all[d+1]['total']) or 0,
					"actual_coverage": str(round(5000/(int(mr_all[d]['total']) - int(mr_all[d+1]['total']))*5, 2)) + '%',
					"rated_yield": 5000
				 	})

			else:
				doc.append("last_readings", {
					"date" : mr_all[d]['reading_date'],
					"type" : mr_all[d]['machine_type'],
					"asset":mr_all[d]['asset'],
					"reading":mr_all[d]['black_and_white_reading'],
					"reading_2":mr_all[d]['colour_reading'],
					"total":( int(mr_all[d]['black_and_white_reading'] or 0)  + int(mr_all[d]['colour_reading'] or 0)),
					"yeild": 0
					})


	set_field_values(doc)
	
# 	assign_task_validation(doc)

	if doc.get('__islocal'):
		for d in frappe.get_all("Task",{"issue":doc.issue}):
			frappe.throw("Task <b>{0}</b> Already Exist Against This Issue".format(doc.name))
	else:
		create_user_permission(doc)
		create_user_issue_permission(doc)
		

	validate_link_fileds(doc)
	update_technician_productivity_matrix(doc)
# 	resolution_time(doc)
	set_assigned_on_task(doc)
	
	# set_escalate(doc)




def before_insert(doc,method):
	send_task_assignment_email(doc)


def set_actual_time(doc):
	if doc.completion_date_time and doc.attended_date_time:
		doc.actual_time = time_diff_in_hours(doc.completion_date_time ,doc.attended_date_time)

def send_task_completion_email(doc):
	"""
	Send email notification to helpdesk and client when task status is set to 'Completed'
	"""
	if doc.status == "Completed" and doc.completed_sent == 0:
		subject = f"""Issue {doc.issue} has been resolved"""

		# send email notification to helpdesk
		helpdesk_email_body = f"""Task ticket number {doc.name}, {doc.customer_name_} has been successfully completed."""
		recipients = frappe.db.get_value("Company", doc.company, "support_email")

		if doc.type_of_call == "Toner":
			recipients = frappe.db.get_value("Company", doc.company, "toner_support_email")
		make(subject = subject, content=helpdesk_email_body, recipients=recipients,
				send_email=True, sender="erp@groupmfi.com")

		#send email notification to client
		attachments = get_attachment(doc)
		print("attachments", attachments)
		client_email_body = f"""Your Ticket number {doc.issue} has been successfully closed"""
		recipients = get_customer_emails(doc.project)
		make(subject = subject, content=client_email_body, recipients=recipients,
			attachments= attachments,
				send_email=True, sender="erp@groupmfi.com")

		doc.completed_sent=1
		frappe.msgprint("Task completion email has been sent")

def get_attachment(doc):
	"""check print settings are attach the pdf"""

	print_settings = frappe.get_doc("Print Settings", "Print Settings")
	if (doc.docstatus == 0 and not print_settings.allow_print_for_draft) or (
		doc.docstatus == 2 and not print_settings.allow_print_for_cancelled
	):

		# ignoring attachment as draft and cancelled documents are not allowed to print
		status = "Draft" if doc.docstatus == 0 else "Cancelled"
		frappe.throw(
			_(
				"""Not allowed to attach {0} document, please enable Allow Print For {0} in Print Settings"""
			).format(status),
			title=_("Error in Notification"),
		)
	else:
		return [
			{
				"print_format_attachment": 1,
				"doctype": doc.doctype,
				"name": doc.name,
				"print_format": "Tracking Sheet",
				"print_letterhead": print_settings.with_letterhead,
				"lang": frappe.db.get_value("Print Format", "Tracking Sheet", "default_print_language")
			}
		]


def send_task_escalation_email(doc):
	if not frappe.db.get_value("Task", doc.name, "escalation"):
		if doc.escalation:
			subject = f"Task has been escalated"

			# send email notification to helpdesk
			helpdesk_email_body = f"""Task ticket number {doc.name} has been
								Escalated By {doc.technician_name} for Follow Up."""
			recipients = frappe.db.get_value("Company", doc.company, "support_email")
			if doc.type_of_call == "Toner":
				recipients = frappe.db.get_value("Company", doc.company, "toner_support_email")

			make(subject = subject, content=helpdesk_email_body, recipients=recipients,
					send_email=True, sender="erp@groupmfi.com")

			# send email notification to client
			# client_email_body = f"""Task Ticket Number {doc.issue} has been Escalated By
			# 					{doc.technician_name} for Follow Up. Any inconvenience is highly regrated."""
			# recipients = get_customer_emails(doc.project)
			# make(subject = subject, content=client_email_body, recipients=recipients,
			# 		send_email=True, sender="erp@groupmfi.com")

			frappe.msgprint("Task escalation email has been sent")


def after_insert(doc,method):
	if doc.get('issue'):
		frappe.db.set_value('Issue',doc.get('issue'),'status','Assigned')

	if doc.failure_date_and_time and doc.issue:
		doc.failure_date_and_time=frappe.db.get_value("Issue",doc.issue,"failure_date_and_time")
	if doc.issue:
		doc.description=frappe.db.get_value("Issue",doc.issue,"description")


	create_user_permission(doc)
	create_user_issue_permission(doc)



	# docperm = frappe.new_doc("DocShare")
	# docperm.update({
	#       "user": doc.completed_by,
	#       "share_doctype": 'Task',
	#       "share_name": doc.name ,
	#       "read": 1,
	#       "write": 1
	#   })
	# docperm.save(ignore_permissions=True)

def send_task_assignment_email(task):
	if task.completed_by:
		assign_subject = f"""Engineer assigned to issue ticket {task.issue}"""
		# body = f"""Task ticket no. {task.issue} has been assigned to our Engineer {task.technician_name}, kindly
		# 			expect him/her as soon as possible"""
		# recipients = get_customer_emails(task.project)
		# make(subject = assign_subject,content=body, recipients=recipients,
		# 	send_email=True, sender="erp@groupmfi.com")

		body = f"""Ticket no. {task.issue}, {task.customer_name_} has been assigned to our Engineer {task.technician_name}"""
		recipients = frappe.db.get_value("Company", task.company, "support_email")
		if task.type_of_call == "Toner":
			body = f"""Ticket no. {task.issue}, {task.customer_name_} with type of call "Toner" has been assigned to our Engineer {task.technician_name}"""
			recipients = frappe.db.get_value("Company", task.company, "toner_support_email")

		make(subject = assign_subject,content=body,recipients=recipients,
			send_email=True, sender="erp@groupmfi.com")

		frappe.msgprint("Task assignment email has been sent")


def on_change(doc,method):
	if doc.get("issue") and doc.status=='Completed':
		set_reading_from_task_to_issue(doc)
	validate_reading(doc)
	existed_mr=[]
	for d in doc.get('current_reading'):
		existed_mr = frappe.get_all("Machine Reading",{"task":doc.name,"project":doc.project, 'row_id':d.get('name')}, 'name')
	if existed_mr :
		update_machine_reading(doc, existed_mr)
	else:
		create_machine_reading(doc)
	if doc.get("issue"):
		issue=frappe.get_doc("Issue",doc.issue)
		issue.response_date_time=doc.attended_date_time
		if doc.issue and doc.status != 'Open':
			issue.status=doc.status
			if doc.status == 'Completed':
				validate_if_material_request_is_not_submitted(doc)
				validate_current_reading(doc)
				signature_validation(doc)
				rating_validation(doc)
				issue.customer_rating = doc.customer_rating
				issue.customer_signature = doc.customer_signature
				# attachment_validation(doc)

				issue.status="Task Completed"
				issue.set("task_attachments",[])
				for d in doc.get("attachments"):
					issue.append("task_attachments",{
						"attach":d.attach
					})

			elif doc.status=="Working" and doc.attended_date_time:
				issue.first_responded_on=doc.attended_date_time
		issue.save(ignore_permissions=True)
	escalation_section(doc)
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
		issue.save(ignore_permissions=True)

@frappe.whitelist()
def make_material_req(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.company=frappe.db.get_value("Employee",{"user_id":frappe.session.user},"company")
	doclist = get_mapped_doc("Task", source_name, {
		"Task": {
			"doctype": "Material Request",
			"name":"custom_task",
			"company":"company"
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
		task.save(ignore_permissions=True)

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
@frappe.validate_and_sanitize_search_inputs
def get_assign_user(doctype, txt, searchfield, start, page_len, filters):
	territory = frappe.db.get_value("User Permission", {'user':filters.get('user'), 'allow':'Territory'}, 'for_value')
	if filters.get("type_of_call") == 'Toner':
		user_list = [u.user for u in  frappe.db.get_all("User Permission",{'allow':'Territory', 'for_value':territory}, 'user') if "Toner Approval 1" in frappe.get_roles(u.user)]
		query = f""" select u.name, u.full_name from `tabUser` u where u.name in {tuple(user_list)} and u.{searchfield} like "%{txt}%" """
		return frappe.db.sql(query)
	else:
		user_list = [u.user for u in  frappe.db.get_all("User Permission",{'allow':'Territory', 'for_value':territory}, 'user') if "Technicians" in frappe.get_roles(u.user)]
		query = f""" select u.name, u.full_name from `tabUser` u where u.name in {tuple(user_list)} and u.{searchfield} like "%{txt}%" """
		return frappe.db.sql(query)


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
		for i in frappe.get_all('Project',fltr,['name']):
			asst.update({'project':i.get('name'),'docstatus':1})
			for ass in frappe.get_all('Asset',asst,['name']):
				if ass.name not in lst:
					lst.append(ass.name)
		return [(d,) for d in lst]


def create_machine_reading(doc):
	for d in doc.get('current_reading'):
		if len(frappe.get_all("Machine Reading",{"task":doc.name,"project":doc.project,"asset":d.get('asset'),"reading_date":d.get('date')}))<1:
			if doc.type_of_call =="Toner":
				mr=frappe.new_doc("Machine Reading")
				mr.reading_date=d.get('date')
				mr.asset=d.get('asset')
				mr.black_and_white_reading=d.get("reading")
				mr.colour_reading=d.get("reading_2")
				mr.machine_type=d.get('type')
				mr.total=d.get("total") or 0
				mr.project=doc.project
				mr.task=doc.name
				mr.row_id = d.name
				mr.item = doc.get('toner_type')
				mr.append("items",{
						"item_code":doc.get('toner_type')
					})
				mr.save(ignore_permissions=True)
			else:
				mr=frappe.new_doc("Machine Reading")
				mr.reading_date=d.get('date')
				mr.asset=d.get('asset')
				mr.black_and_white_reading=d.get("reading")
				mr.colour_reading=d.get("reading_2")
				mr.machine_type=d.get('type')
				mr.total=d.get("total")
				mr.project=doc.project
				mr.task=doc.name
				mr.row_id = d.name
				if doc.type_of_call =="Installation":
					mr.reading_type = "Installation"
				mr.save(ignore_permissions=True)
			# d.machine_reading=mr.name
def update_machine_reading(doc, existed_mr):
	for d in doc.get('current_reading'):
		for mr in existed_mr:
			mr_doc=frappe.get_doc("Machine Reading", mr)
			mr_doc.reading_date=d.get('date')
			mr_doc.asset=d.get('asset')
			mr_doc.black_and_white_reading=d.get("reading")
			mr_doc.colour_reading=d.get("reading_2")
			mr_doc.machine_type=d.get('type')
			mr_doc.total=d.get("total")
			mr_doc.save(ignore_permissions=True)

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
				issue_doc.save(ignore_permissions=True)
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
	issue_doc.save(ignore_permissions=True)

def validate_reading(doc):
    user_roles= frappe.get_roles(frappe.session.user)
    curr = []
    last = []
    curr_date = []
    last_date = []
    if "Call Coordinator" not in user_roles or "Administrator" in user_roles:
        for cur in doc.get('current_reading'):
            print(f'\n\n\n\n\ntask{cur.get("reading")},{cur.get("reading_2")}\n\n\n\n\n')
            cur.total=( int(cur.get('reading') or 0)  + int(cur.get('reading_2') or 0))
            curr.append(cur.total)
            curr_date.append(cur.date)
            for lst in doc.get('last_readings'):
                lst.total=( int(lst.get('reading') or 0)  + int(lst.get('reading_2') or 0))
                last.append(lst.total)
                last_date.append(lst.date)
    if len(curr)>0 and len(last)>0:
        print(f'\n\n\n\n\n122{curr},{last}\n\n\n\n\n')
        frappe.log_error(f'\n\n\n\n\n122{curr},{last}\n\n\n\n\n')
        # if doc.issue_type != 'Error message':
        if int(last[0])>=int(curr[0]) and int(last[0])>0 and int(curr[0])>0:
            frappe.throw("Current Reading Must be Greater than Last Reading")

    if len(curr_date)>0 and len(last_date)>0:
        if last_date[0] != today:
            if last_date[0]>curr_date[0] and int(last[0])>0 and int(curr[0])>0:
                frappe.throw("Current Reading <b>Date</b> Must be Greater than Last Reading")

#def validate_reading(doc):
#	for cur in doc.get('current_reading'):
#		cur.total=( int(cur.get('reading') or 0)  + int(cur.get('reading_2') or 0))
#		for lst in doc.get('last_readings'):
#			lst.total=( int(lst.get('reading') or 0)  + int(lst.get('reading_2') or 0))
#			if int(lst.total)>=int(cur.total):
#				frappe.throw("Current Reading Must be Greater than Last Reading")
#			if getdate(lst.date)>=getdate(cur.date):
#				frappe.throw("Current Reading <b>Date</b> Must be Greater than Last Reading")

def validate_if_material_request_is_not_submitted(doc):
	for mr in frappe.get_all("Material Request",{"task":doc.name,"workflow_state":['not in', ['Approved', 'Rejected']]}):
		frappe.throw("Material Request is not completed yet. Name <b>{0}</b>".format(mr.name))

# def attachment_validation(doc):
# 	if not doc.attachments or  len(doc.attachments)==0:
# 		frappe.throw("Cann't Completed Task Without Attachment")

def signature_validation(doc):
	if (not doc.customer_signature or doc.customer_signature is None) and doc.type_of_call != 'Toner':
		frappe.throw("Can't Completed Task Without Signature")

def rating_validation(doc):
	if (not doc.customer_rating or doc.customer_rating is None) and doc.type_of_call != 'Toner':
		frappe.throw("Can't Completed Task Without Rating")


def create_user_permission(doc):
	if len(frappe.get_all("User Permission",{"allow":"Task","for_value":doc.name,"user":doc.completed_by}))==0:
		for d in frappe.get_all("User Permission",{"allow":"Task","for_value":doc.name}):
			frappe.delete_doc("User Permission",d.name)
		add_user_permission("Task",doc.name,doc.completed_by)
		add_user_permission("Issue",doc.issue,doc.completed_by)

	for emp in frappe.get_all("Employee",{"user_id":doc.completed_by},['material_request_approver']):
		if emp.material_request_approver:
			for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
				if emp2.user_id:
					add_user_permission("Task",doc.name,emp2.user_id)
	if 'Task' not in frappe.db.get_all('DocShare',{'user':doc.completed_by,'share_name':doc.name}, 'share_doctype', pluck='share_doctype') or doc.name not in frappe.db.get_all('DocShare',{'share_doctype':'Task','user':doc.completed_by}, 'share_name', pluck='share_name') or doc.completed_by not in frappe.db.get_all('DocShare',{'share_doctype':'Task','share_name':doc.name}, 'user', pluck='user'):
		share = frappe.new_doc('DocShare')
		share.share_doctype = 'Task'
		share.share_name = doc.name
		share.user = doc.completed_by
		share.read = 1
		share.write = 1
		
		share.save(ignore_permissions=True)

def create_user_issue_permission(doc):
		if len(frappe.get_all("User Permission",{"allow":"Issue","for_value":doc.issue,"user":doc.completed_by}))==0:
			for d in frappe.get_all("User Permission",{"allow":"Issue","for_value":doc.issue}):
				frappe.delete_doc("User Permission",d.name)
			add_user_permission("Issue",doc.issue,doc.completed_by)

		for emp in frappe.get_all("Employee",{"user_id":doc.completed_by},['material_request_approver']):
			if emp.material_request_approver:
				for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
					if emp2.user_id:
						add_user_permission("Issue",doc.issue,emp2.user_id)


# def create_share(doc,method=None):
# 	frappe.log_error('AFter Save function trigger')
# 	print("..............................create_share")
	
# def assign_task_validation(doc):
# 	if doc.status=="Working":
# 		for d in frappe.get_all("Task",{"status":"Working","completed_by":doc.completed_by,"name":("!=",doc.name)}):
# 			frappe.throw("Task <b>{0}</b> is already in working".format(d.name))

def validate_link_fileds(doc):
	if doc.get('issue'):
		issue=frappe.get_doc("Issue",doc.get('issue'))
		# validate_customer(doc,issue)
		# validate_location(doc)
		validate_asset(doc,issue)
		validate_serial_no(doc,issue)

def link_issue_attachments(task, method):
	if task.issue:
		issue=frappe.get_doc("Issue",task.issue)
		attachments = frappe.get_all("File", {"attached_to_doctype":"Issue", "attached_to_name":issue.name})
		if attachments:
			for attachment in attachments:
				file = frappe.get_doc("File", attachment.name)
				duplicate_file = frappe.get_doc(
					{
						"doctype": "File",
						"file_name": file.file_name,
						"attached_to_doctype": "Task",
						"attached_to_name": task.name,
						"content": file.get_content(),
					}
				)
				duplicate_file.save(ignore_permissions=True)


def validate_customer(doc,issue):
	if doc.customer and issue.customer and doc.customer != issue.customer:
		frappe.throw("Please Enter Valid Customer,Which exists in Issue {0}".format(issue.get('name')))



def validate_asset(doc,issue):
	if doc.asset and issue.asset and doc.asset != issue.asset:
		frappe.throw("Please Enter Valid Asset,Which exists in Issue {0}".format(issue.get('name')))

	if doc.asset and doc.asset not in get_asset(doc.customer,doc.location):
		frappe.throw("Please Enter Valid Asset")

def validate_serial_no(doc,issue):
	if doc.serial_no and issue.serial_no and doc.serial_no != issue.serial_no:
		frappe.throw("Please Enter Valid Serial No,Which exists in Issue {0}".format(issue.get('name')))

	if doc.serial_no and doc.serial_no not in get_serial_no(doc.customer,doc.location,doc.asset):
		frappe.throw("Please Enter Valid Serial No")

def validate_location(doc):
	if doc.location and doc.location not in get_location_validation(doc.customer):
		frappe.throw("Please Enter Valid Location")

@frappe.whitelist()
def get_serial_no(customer,location,asset):
	fltr1 = {}
	fltr2 = {}
	lst = []
	if customer:
		fltr1.update({'customer':customer})
	if location:
		fltr2.update({'location':location})
	if asset:
		fltr2.update({'name':asset})

	for i in frappe.get_all('Project',fltr1,['name']):
		fltr2.update({'project':i.get('name'),'docstatus':1})
		for j in frappe.get_all('Asset',fltr2,['serial_no']):
			if j.serial_no not in lst:
				lst.append(j.serial_no)
	return lst


@frappe.whitelist()
def get_locationlist(doctype, txt, searchfield, start, page_len, filters):
	location_list=[]
	project_list = [p.name for p in frappe.db.get_list("Project", filters={"customer":filters.get("Customer_Name")},fields={"name"})]
	for p in project_list:
		location_list =[[l.location] for l in frappe.db.get_list("Asset",{"project":p},"location") if [l.location] not in location_list ]
	return location_list

@frappe.whitelist()
def set_items_on_machine_reading_from_mr(asset,task):
	material_request_list =[i.name for i in frappe.db.get_list('Material Request',{'task':task, 'asset':asset}, 'name')]
	if material_request_list:
		machine_reading_doc = frappe.get_last_doc('Machine Reading', filters={"task":task, "asset":asset})
		machine_reading_doc.items =[]
		for mr in material_request_list:
			mr_doc = frappe.get_doc('Material Request',mr)
			for i in mr_doc.items:
				machine_child =machine_reading_doc.append('items',{})
				machine_child.item_code = i.item_code
				machine_child.item_name = i.item_name
				machine_child.item_group = i.item_group
				machine_reading_doc.save(ignore_permissions=True)


@frappe.whitelist()
def transfer_data_to_issue(doc):
	doc=json.loads(doc)
	if doc.get('status')=='Completed':
		issue_doc = frappe.get_doc('Issue',doc.get('issue'))
		issue_doc.symptoms=doc.get('symptoms')
		issue_doc.action=doc.get('action')
		issue_doc.cause=doc.get('cause')
		issue_doc.completed_sent=1
		task = frappe.get_doc("Task", doc.get('name'))
		for current_reading in issue_doc.current_reading:
			current_reading.reading = task.current_reading[0].reading
			current_reading.reading_2 = task.current_reading[0].reading_2
		issue_doc.save(ignore_permissions=True)

def get_location_validation(customer):
	lst = []
	for i in frappe.get_all('Project',{"customer":customer},['name']):
		for a in frappe.get_all('Asset',{'project':i.get('name')},['location']):
			if a.location not in lst:
				lst.append(a.location)
	return lst


def get_asset(customer,location):
	fltr1 = {}
	fltr2 = {}
	lst = []
	if customer:
		fltr1.update({'customer':customer})
	if location:
		fltr2.update({'location':location})

	for i  in frappe.get_all('Project',fltr1,['name']):
		fltr2.update({'project':i.get('name'),'docstatus':1})
		for ass in frappe.get_all('Asset',fltr2,['name']):
			if ass.name not in lst:
				lst.append(ass.name)
	return lst


def validate_current_reading(doc):
	if frappe.db.get_value('Type of Call',{'name':doc.type_of_call},'ignore_reading')==0 and len(doc.get("current_reading"))==0:
		frappe.throw("Cann't Complete Task Without Current Reading")


def escalation_section(doc):
    issue= frappe.get_doc('Issue', doc.issue)
    if doc.escalation ==1 and doc.senior_technician_description:
       if issue:
          issue.escalation=1
          issue.escalated_technician_name=doc.escalated_technician_name
          issue.escalation_description=doc.escalation_
          issue.senior_technician_description=doc.senior_technician_description
          issue.save(ignore_permissions=True)
    if doc.status =="Completed" and doc.requested_material_status:
       if issue:
          issue.requested_material_status=doc.requested_material_status
          issue.save(ignore_permissions=True)




@frappe.whitelist()
def repetitive_call(doc):
	mr_count = frappe.db.sql("select sum(total) from `tabMachine Reading` where asset = %s", doc.asset)
	mr=str(mr_count)
	mr=mr.replace("(","")
	mr=mr.replace(")","")
	mr=mr.replace(",","")
	mr=mr.replace(".0","")

	frappe.msgprint(mr)

@frappe.whitelist()
def assingn_to_fltr_bassed_on_technician(doctype, txt, searchfield, start, page_len, filters):
    list_user=[]
    all_user_list=[i.name for i in  frappe.db.sql("""select name from `tabUser`""",as_dict=1)]
    for usr in all_user_list:
        check_roles=frappe.get_roles(usr)
        for j in check_roles:
            if j == "Technicians":
               list_user.append(usr)
    return  [[d] for d in list_user]


def update_technician_productivity_matrix(doc):
	if frappe.db.exists('Task', doc.name):

		task = frappe.get_doc("Task", doc.name)
		if task:
			# when task is escalated
			if not frappe.db.get_value("Task", doc.name, "escalation") and doc.escalation and doc.escalation_:
				paused_datetime = {row.technician: row.paused for row in task.technician_productivity_matrix}
				if task.completed_by in paused_datetime and not paused_datetime[task.completed_by]:
					for i in doc.technician_productivity_matrix:
						if i.technician == task.completed_by and not i.paused:
							i.paused = now_datetime()
				else:
					row = doc.append("technician_productivity_matrix", {})
					row.technician = doc.completed_by
					row.paused = now_datetime()


			elif frappe.db.get_value("Task", doc.name, "status") != "Working" and doc.status == "Working":  # working
				working_datetime = {row.technician: row.working for row in task.technician_productivity_matrix}
				if task.completed_by in working_datetime and not working_datetime[task.completed_by]:
					for i in doc.technician_productivity_matrix:
						if i.technician == task.completed_by and not i.working:
							i.working = now_datetime()
				else:
					row = doc.append("technician_productivity_matrix", {})
					row.technician = doc.completed_by
					row.working = now_datetime()

			elif frappe.db.get_value("Task", doc.name, "status") != "Completed" and doc.status == "Completed":  # working
				closed_datetime = {row.technician: row.closed for row in task.technician_productivity_matrix}
				if task.completed_by in closed_datetime and not closed_datetime[task.completed_by]:
					for i in doc.technician_productivity_matrix:
						if i.technician == task.completed_by and not i.closed:
							i.closed = now_datetime()
				else:
					row = doc.append("technician_productivity_matrix", {})
					row.technician = doc.completed_by
					row.closed = now_datetime()

def set_assigned_on_task(doc):
	if frappe.db.exists('Task', doc.name):
		if frappe.db.get_value("Task", doc.name, "completed_by") != doc.completed_by:
			assigned_datetime = {row.technician: row.assigned for row in doc.technician_productivity_matrix}
			if doc.completed_by in assigned_datetime and not assigned_datetime.get(doc.completed_by):
				for i in doc.technician_productivity_matrix:
					if i.technician == doc.completed_by and not i.assigned:
						i.assigned = now_datetime()
			else:
				row = doc.append("technician_productivity_matrix", {})
				row.technician = doc.completed_by
				row.assigned = now_datetime()
	else:
		row = doc.append("technician_productivity_matrix", {})
		row.technician = doc.completed_by
		row.assigned = now_datetime()

def set_escalate(doc):
	technician = frappe.db.get_value("Task", doc.name, "completed_by")

	if technician != doc.completed_by:
		doc.escalation = 0

# def resolution_time(doc):
# 	if frappe.db.exists('Task', doc.name):
# 		if len(doc.technician_productivity_matrix)>0:
# 			for i in doc.technician_productivity_matrix:
# 				if i.working and i.closed and not i.material_request and not i.material_issued:
# 					i.resolution_time = i.closed - datetime.strptime(i.working, '%Y-%m-%d %H:%M:%S.%f')
# 				elif i.working and i.closed and i.material_request and i.material_issued:
# 					i.resolution_time = (i.material_request - i.working) + (i.closed - i.material_issued)
