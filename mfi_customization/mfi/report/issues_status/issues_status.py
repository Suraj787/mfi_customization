# Copyright (c) 2023, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta


def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_columns():
	frappe.log_error('get_cols')
	return[
		"Issue" + "Link/Issue:150",
		"Creation" + ":Date:150",
	]	

def get_data(filters=None):
	frappe.log_error('get_data')
	data=[]
	issue_list=frappe.get_all("Issue")
	for i in issue_list:
		iss_doc = frappe.get_doc("Issue",i.name)
		frappe.log_error(f'type,{type(iss_doc.creation)}')
		# datetime_object = datetime.strptime(iss_doc.creation, '%y-%m-%d %H:%M:%S')
		upd_time = iss_doc.creation + timedelta(hours=48)
		if upd_time >= datetime.now():
			if iss_doc.status == 'Open':
				issue = iss_doc.name if iss_doc.name else ""
				# pe = frappe.get_doc("Payment Entry",{'party':purchase_invoice_doc.supplier})
				creation = iss_doc.creation if iss_doc.creation else ""
				row = [
						issue,
						creation
				]
				data.append(row)
	return data
		