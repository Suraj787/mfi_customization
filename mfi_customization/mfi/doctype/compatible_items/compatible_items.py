# Copyright (c) 2022, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CompatibleItems(Document):
	pass


def add_item_in_asset(doc, method):
	asset = frappe.get_doc("Asset", doc.asset)
	item = frappe.get_doc("Item", doc.item)

	if doc.type == "Accessories":
		items = [item.item_code for item in asset.items]
		if item.item_code not in items:
			row = asset.append('items', {})
			row.item_code = item.item_code
			row.item_name = item.item_name
			row.item_group = item.item_group
			row.yeild = item.yeild
	elif doc.type == "Toner":
		items = [item.item_code for item in asset.compatible_toners]
		if item.item_code not in items:
			row = asset.append('compatible_toners', {})
			row.item_code = item.item_code
			row.item_name = item.item_name
			row.item_group = item.item_group
			row.yeild = item.yeild
	asset.save()

