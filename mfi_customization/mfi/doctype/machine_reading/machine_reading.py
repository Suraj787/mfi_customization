# -*- coding: utf-8 -*-
# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import month_diff

class MachineReading(Document):

	def before_insert(self):
		task = frappe.get_doc("Task", self.task)
		asset = frappe.get_doc("Asset", self.asset)
		item_total = frappe.db.get_value("Item", asset.item_code, "total")
		item_months = frappe.db.get_value("Item", asset.item_code, "no_of_month")
		if task.type_of_call == "CM" and asset.docstatus:
			filters = {"asset": self.asset, "project": self.project}
			previous_readings = frappe.db.get_all("Machine Reading", filters=filters, fields=['name', 'total', 'task'], order_by="creation desc")
			machine_readings = []
			for reading in previous_readings:
				task_type = frappe.db.get_value("Task", reading.task, 'type_of_call')
				if task_type == "CM":
					machine_readings.append(reading)
			if not machine_readings:
				machine_readings = frappe.db.get_all("Machine Reading", filters=filters, fields=['name', 'total', 'task'])
				if machine_readings:
					machine_readings = machine_readings[0]

			if machine_readings:
				total_diff = int(self.total)-int(machine_readings[0].total)
				last_mr_posting_date = frappe.db.get_value("Machine Reading", machine_readings[0].name, "posting_date")
				months_diff = month_diff(self.posting_date, last_mr_posting_date)
				if total_diff<item_total or months_diff<item_months:
					frappe.db.sql("UPDATE `tabTask` SET repetitive_call = 1 WHERE name=%s",task.name)




# def validate(doc,method):
# 	machine_reading_asset=[i.total for i in frappe.db.sql(f"""select max(reading_date),total from `tabMachine Reading` where asset ='{doc.asset}' """,as_dict=1)if i.total is not None]
# 	mr_name = frappe.db.get_value("Material Request",{"task":doc.task},"name")
# 	if mr_name and machine_reading_asset:
# 		mr_doc  = frappe.get_doc('Material Request', mr_name)
# 		if len(mr_doc.items_with_yeild) == 0:
# 			mr_doc.items_with_yeild=[]
# 			for i in mr_doc.items:
# 				machine_reding_with_itm =[i.total for i in  frappe.db.sql(f"""select max(m.reading_date),m.total from `tabMachine Reading` as m inner join `tabAsset Item Child Table` as a on a.parent=m.name where m.asset ='{doc.asset}' and a.item_code ='{i.item_code}' and m.task='{doc.task}' """,as_dict=1)if i.total is not None ]
# 				item_yeild =[itm.yeild for itm in frappe.db.sql(f""" SELECT yeild from `tabItem` where item_code ='{i.item_code}' """,as_dict=1)]
# 				if machine_reding_with_itm:
# 					mr_child = mr_doc.append("items_with_yeild",{})
# 					mr_child.item_code= i.item_code
# 					mr_child.item_name= i.item_name
# 					mr_child.item_group= i.item_group
# 					mr_child.yeild=int(machine_reding_with_itm[0]) - int(machine_reading_asset[0])
# 					mr_child.total_yeild =float(item_yeild[0])
# 					mr_doc.save()




