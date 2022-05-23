# -*- coding: utf-8 -*-
# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MachineReading(Document):
	pass
	
	
@frappe.whitelist()	
def item_child_table_filter(doctype, txt, searchfield, start, page_len, filters):
    asset_name = filters.get("asset")
    data = frappe.db.sql(f"""
    SELECT item_code,item_name,item_group from `tabAsset Item Child Table` where parent= '{asset_name}'
""", as_dict=0)
    return data
    
	
