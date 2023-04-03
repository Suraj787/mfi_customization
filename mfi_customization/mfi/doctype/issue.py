# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import today,getdate
from frappe.core.doctype.communication.email import make
from mfi_customization.mfi.doctype.project import get_customer_emails

def validate(doc,method):
	email_validation(doc)
	set_company(doc)
	set_territory(doc)
	# validate_link_fileds(doc)
	# validate_issue(doc)
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

	send_call_resolved_email(doc)
	send_issue_closed_email(doc)


def on_change(doc,method):
	# validate_reading(doc)
	set_task_status_cancelled(doc)

def email_validation(doc):
	if doc.email_conact and "@" not in 	doc.email_conact:
		frappe.throw("Email Not Valid")

def set_company(doc):
	if doc.asset:
		company = frappe.db.get_value("Asset", {'name': doc.asset}, 'company')
	if company:
		doc.company = company

def set_territory(doc):
	if doc.customer:
		territory = frappe.db.get_value("Customer", {'name': doc.customer}, 'territory')
	if territory:
	 	doc.territory = territory

@frappe.whitelist()
def make_task(source_name, target_doc=None):
	# issue = frappe.get_doc("Issue", source_name)
	# if issue.type_of_call == "Service Request" and issue.issue_type=="Error message":
	# 	return get_mapped_doc("Issue", source_name, {
	# 		"Issue": {
	# 			"doctype": "Task",
	# 			"field_map": {"last_readings": "current_reading"},
	# 		}
	# 	}, target_doc)

	return get_mapped_doc("Issue", source_name, {
	"Issue": {
		"doctype": "Task",
		"field_map": {"last_readings": "current_reading"},
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
def add_item_filter(asset):
	if asset is not None and asset:
		item_code = frappe.db.get_value('Asset',{'name':asset},'item_code')
		item = frappe.get_doc('Item',{'item_code':item_code})
		toner = []
		for tone in item.compatible_toners:
			toner.append(tone.item_code)

		return toner


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
    user_roles= frappe.get_roles(frappe.session.user)
    curr = []
    last = []
    curr_date = []
    last_date = []
    if "Call Coordinator" not in user_roles or "Administrator" in user_roles:
        for cur in doc.get('current_reading'):
            # print(f'\n\n\n\n\ntask{cur.get("reading")},{cur.get("reading_2")}\n\n\n\n\n')
            cur.total=( int(cur.get('reading') or 0)  + int(cur.get('reading_2') or 0))
            curr.append(cur.total)
            curr_date.append(cur.date)
            for lst in doc.get('last_readings'):
                lst.total=( int(lst.get('reading') or 0)  + int(lst.get('reading_2') or 0))
                last.append(lst.total)
                last_date.append(lst.date)

    if len(curr)>0 and len(last)>0:
        # print(f'\n\n\n\n\n122{curr},{last}\n\n\n\n\n')
        if int(last[0])>=int(curr[0]):
            frappe.throw("Current Reading Must be Greater than Last Reading")

    if len(curr_date)>0 and len(last_date)>0:
        if getdate(lst.date)>=getdate(cur.date):
            frappe.throw("Current Reading <b>Date</b> Must be Greater than Last Reading")
#def validate_reading(doc):
#	for cur in doc.get('current_reading'):
#		cur.total=( int(cur.get('reading') or 0)  + int(cur.get('reading_2') or 0))
#		if doc.get('last_readings'):
#			for lst in doc.get('last_readings'):
#				lst.total=( int(lst.get('reading') or 0)  + int(lst.get('reading_2') or 0))
#				if int(lst.total)>int(cur.total):
#					frappe.throw("Current Reading Must be Greater than Last Reading")
#				if getdate(lst.date)>getdate(cur.date):
#					frappe.throw("Current Reading <b>Date</b> Must be Greater than Last Reading")


@frappe.whitelist()
def get_issue_types(doctype, txt, searchfield, start, page_len, filters):
	fltr={"name":("IN",[d.parent for d in frappe.get_all("Call Type List",{"call_type":filters.get("type_of_call")},['parent'])])}
	if txt:
		fltr.update({"name": ("like", "{0}%".format(txt))})
	return frappe.get_all("Issue Type",filters=fltr,fields = ["name"], as_list=1)

def validate_issue(doc):
	for issue in frappe.get_all("Issue",{"asset":doc.asset,"name":("!=",doc.name),"status":["NOT IN",["Closed","Cancelled"]]}):
		frappe.throw("Issue already exists with <b>{0}</b>".format(issue.name))

def set_task_status_cancelled(doc):
	if doc.status=="Cancelled":
		for tk in frappe.get_all("Task",{"issue":doc.name}):
			task=frappe.get_doc("Task",tk.name)
			if task.status!="Cancelled":
				task.status="Cancelled"
				task.save()

def validate_link_fileds(doc):
	validate_location(doc)
	validate_asset(doc)
	validate_serial_no(doc)


def validate_asset(doc):
	if doc.asset and doc.asset not in get_asset(doc.customer,doc.location):
		frappe.throw("Please Enter Valid Asset")


def validate_serial_no(doc):
	if doc.serial_no and doc.serial_no not in get_serial_no(doc.customer,doc.location,doc.asset):
		frappe.throw("Please Enter Valid Serial No")

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

def validate_location(doc):
	if doc.status=="Closed" and not doc.location:
		frappe.throw("Can't Closed Issue Without <b>Location</b>")


@frappe.whitelist()
def get_logged_user():
	user = frappe.db.get_value('User',{"name":frappe.session.user},"full_name")
	customerId_of_user=frappe.db.get_value("Customer",{"customer_name":user},"name")
	return customerId_of_user


@frappe.whitelist()
def get_locationlist(doctype, txt, searchfield, start, page_len, filters):
	location_list=[]
	project_list = [p.name for p in frappe.db.get_list("Project", filters={"customer":filters.get("Customer_Name")},fields={"name"})]
	for p in project_list:
		location_list =[[l.location] for l in frappe.db.get_list("Asset",{"project":p},"location") if [l.location] not in location_list ]
	return location_list

@frappe.whitelist()
def check_type_of_call(project, type_of_call):
	call_type_list = [c.call_type for c in frappe.db.get_list("Hold Call Types",{'parent':project}, "call_type")]
	if len(call_type_list) > 0 and type_of_call in call_type_list:
		return True
	else:
		return False


def after_insert(doc,method):
	"""
	Send email notifications when Issue is created
	"""
	if doc.type_of_call == "Service Request" or doc.type_of_call == "Toner":
		client_emails = get_customer_emails(doc.project)
		support_email = frappe.db.get_value("Company", doc.company, "support_email")
		subject = f"""Ticket created for Issue"""
		customer_name = frappe.db.get_value("Customer", doc.customer, "customer_name")
		helpdesk_body = f"""Issue ticket number {doc.name} has been
							created by {doc.customer} - {customer_name}"""
		if doc.type_of_call == "Service Request":
			client_body = f"""Your issue has been successfully created with ticket number {doc.name}
					Kindly wait as we assign our Engineer."""

		elif doc.type_of_call == "Toner":
			client_body = f"""Your issue regarding Toner has been successfully created with ticket number
							{doc.name}. Kindly wait as we resolve it."""
			support_email = frappe.db.get_value("Company", doc.company, "toner_support_email")


		make(subject = subject,content=client_body,
			recipients=client_emails,
			send_email=True, sender="erp@groupmfi.com")
		make(subject = subject,content=helpdesk_body,
			recipients=support_email,
			send_email=True, sender="erp@groupmfi.com")
		frappe.msgprint("Issue ticket creation email has been sent")

def send_call_resolved_email(issue):
	if not frappe.db.get_value("Issue", issue.name, "over_call_resolution"):
		if issue.over_call_resolution and issue.resolution_reason and issue.type_of_call == "Service Request":
			subject = f"Issue {issue.name} resolved on call"
			helpdesk_email = frappe.db.get_value("Company", issue.company, "support_email")
			client_emails = get_customer_emails(issue.project)
			email_body = f"Issue ticket number {issue.name} has been resolved on call"
			if issue.type_of_call == "Toner":
				helpdesk_email = frappe.db.get_value("Company", issue.company, "toner_support_email")

			make(subject = subject,content=email_body,
				recipients=client_emails,
				send_email=True, sender="erp@groupmfi.com")

			make(subject = subject,content=email_body,
				recipients=helpdesk_email,
				send_email=True, sender="erp@groupmfi.com")

def send_issue_closed_email(issue):
	status = frappe.db.get_value("Issue", issue.name, "status")
	if status != "Closed" and issue.status == "Closed":
		subject = f"Issue {issue.name} closed"
		helpdesk_email = frappe.db.get_value("Company", issue.company, "support_email")
		if issue.type_of_call == "Toner":
			helpdesk_email = frappe.db.get_value("Company", issue.company, "toner_support_email")
		client_emails = get_customer_emails(issue.project)
		email_body = f"Issue ticket number {issue.name} has been closed"

		make(subject = subject,content=email_body,
			recipients=client_emails,
			send_email=True, sender="erp@groupmfi.com")

		make(subject = subject,content=email_body,
			recipients=helpdesk_email,
			send_email=True, sender="erp@groupmfi.com")

@frappe.whitelist()
def asset_name_item(item_code):
	items = []
	scrapitems = frappe.db.sql("select aic.item_code from `tabItem` i LEFT JOIN `tabAsset Item Child Table` aic on aic.parent = i.name where i.name = %s and aic.item_group='Toner' group by aic.item_code",item_code)
	for item in scrapitems:
		items.append(item[0])
	return items

# @frappe.whitelist()
# def user_customer(user):
#     user = frappe.db.sql(f"""select for_value from `tabUser Permission` where user='{user}' and allow='Customer'""")
#     return user