# Copyright (c) 2022, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CompatibleItems(Document):
	pass

def add_item(doc, method):
    item = frappe.get_doc('Item',doc.asset_item)
    if doc.type == "Accessories":
            add_on_entry_child = item.append('items',{})
            add_on_entry_child.item_code = doc.item

    elif doc.type == "Toner":
            add_on_entry_child = item.append('compatible_toners',{})
            add_on_entry_child.item_code = doc.item
            
    item.save()

# def add_item_in_asset(doc, method):
# 	asset = frappe.get_doc("Asset", doc.asset)
# 	item = frappe.get_doc("Item", doc.item)

# 	if doc.type == "Accessories":
# 		items = [item.item_code for item in asset.items]
# 		if item.item_code not in items:
# 			row = asset.append('items', {})
# 			row.item_code = item.item_code
# 			row.item_name = item.item_name
# 			row.item_group = item.item_group
# 			row.yeild = item.yeild
# 	elif doc.type == "Toner":
# 		items = [item.item_code for item in asset.compatible_toners]
# 		if item.item_code not in items:
# 			row = asset.append('compatible_toners', {})
# 			row.item_code = item.item_code
# 			row.item_name = item.item_name
# 			row.item_group = item.item_group
# 			row.yeild = item.yeild
# 	asset.save()

def add_item():
    comp_it = frappe.db.get_all('Compatible Items', pluck='name')
    for i in comp_it:
        comp_items = frappe.get_doc('Compatible Items',i)
        item = frappe.get_doc('Item',comp_items.asset_item)
        if comp_items.type == 'Accessories':
            item.append("items",{
                "item_code": comp_items.item,
                "company": 'MFI DOCUMENT SOLUTIONS KENYA'
                })
            print(f'\n\n\nitem{item}\n\n\n\n')
            item.save()

        else:
            item.append("compatible_toners",{
                "item_code": comp_items.item,
                "company": 'MFI DOCUMENT SOLUTIONS KENYA'
                })
            item.save()
        


