# Copyright (c) 2022, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CompatibleItems(Document):
	pass


def add_item_in_asset(doc, method):
	if doc.type == "Accessories":
		asset = frappe.get_doc("Asset", doc.asset)
		items = [item.item_code for item in asset.items]
		item = frappe.get_doc("Item", doc.item)
		if item.item_code not in items:
			row = asset.append('items', {})
			row.item_code = item.item_code
			row.item_name = item.item_name
			row.item_group = item.item_group
			row.yeild = item.yeild

