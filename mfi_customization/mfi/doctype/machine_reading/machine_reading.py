# -*- coding: utf-8 -*-
# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MachineReading(Document):
    
	def after_insert(self):
		toc = frappe.db.sql("select type_of_call from `tabTask` where name =%s", self.task)
		toc=str(toc)
		toc=toc.replace("(","")
		toc=toc.replace(")","")
		toc=toc.replace(",","")
		toc=toc.replace("'","")	
		mr_count = frappe.db.sql("select sum(total) from `tabMachine Reading` where asset = %s", self.asset)
		mr=str(mr_count)
		mr=mr.replace("(","")
		mr=mr.replace(")","")
		mr=mr.replace(",","")
		mr=mr.replace(".0","")
		
		items = frappe.db.sql("select item_code from `tabAsset` where name = %s", self.asset)
		
		bandw = frappe.db.sql("select total from `tabItem` where name = %s", items)
		b=str(bandw)
		b=b.replace("(","")
		b=b.replace(")","")
		b=b.replace(",","")
		
		if mr >= b:
			if toc == "CM":
				frappe.db.sql("UPDATE `tabTask` SET repetitive_call = 1 WHERE name=%s",self.task)
			


  
       
       
               
		



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
		



				   