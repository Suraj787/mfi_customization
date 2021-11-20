# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

import frappe,json
from frappe.model.document import Document
from frappe.utils import today

class MachineReadingTool(Document):
	pass

@frappe.whitelist()	
def get_machine_reading(project,reading_date,reading_type):
	asset_list=[]
	for ast in frappe.get_all("Asset",filters={'project':project}, fields=['name',"asset_name"],order_by="name"):
		asset_list.append(({"asset":ast.name,"asset_name":ast.asset_name,"reading_date":reading_date,"reading_type":reading_type}))
	return asset_list



@frappe.whitelist()
def create_machine_reading(readings):
	readings=json.loads(readings)
	for r in readings.get("reading_details"):
		if readings.get("reading_details")[r].get('black_and_white_reading') or readings.get("reading_details")[r].get('colour_reading'):
			make_machine_reading(readings.get("reading_details")[r])
	return []

def make_machine_reading(doc):

	mr=frappe.new_doc("Machine Reading")
	for key in doc.keys():
		mr.set(key,doc[key])
	mr.save()