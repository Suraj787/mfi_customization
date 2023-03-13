# Copyright (c) 2022, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CompatibleItems(Document):
	pass


def add_item():
	compatible_items = frappe.get_all("Compatible Items")
	for c_item in compatible_items:
		c_item = frappe.get_doc("Compatible Items", c_item)
		if frappe.db.exists('Item',c_item.asset_item):
			item = frappe.get_doc('Item',c_item.asset_item)
			print('checking item to add compatible item')
			company = "MFI DOCUMENT SOLUTIONS KENYA"
			added_items = [row.item_code for row in item.compatible_spares]
			added_compatible_toners = [row.item_code for row in item.compatible_toners]
			item_modified = 0
			if c_item.item not in added_items and c_item.type == "Accessories":
				print('*************adding Accessories***************')
				add_on_entry_child = item.append('compatible_spares',{})
				add_on_entry_child.item_code = c_item.item
				add_on_entry_child.company = company
				add_on_entry_child.item_name = item.item_name
				add_on_entry_child.item_group = item.item_group
				add_on_entry_child.yeild = item.yeild
				item_modified = 1


			elif c_item.item not in added_compatible_toners and c_item.type == "Toner":
				print('*************adding Toner***************')
				add_on_entry_child = item.append('compatible_toners',{})
				add_on_entry_child.item_code = c_item.item
				add_on_entry_child.company = company
				add_on_entry_child.item_name = item.item_name
				add_on_entry_child.item_group = item.item_group
				add_on_entry_child.yeild = item.yeild
				item_modified = 1
			if item_modified:
				print('*************saving item***************')
				item.save()
	frappe.db.commit()

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

def add_item_details():
    comp_it = frappe.db.get_all('Compatible Items', pluck='name')
    for i in comp_it:
        comp_items = frappe.get_doc('Compatible Items',i)
        item = frappe.get_doc('Item',comp_items.asset_item)
        added_items = [row.item_code for row in item.compatible_spares]
        if comp_items.item not in added_items and comp_items.type == 'Accessories':
            item.append("compatible_spares",{
                "item_code": comp_items.item,
                "company": 'MFI DOCUMENT SOLUTIONS KENYA'
                })
            print(f'\n\n\nitem{item}\n\n\n\n')
            item.save()

        if comp_items.item not in added_items and comp_items.type == 'Toner':
            item.append("compatible_toners",{
                "item_code": comp_items.item,
                "company": 'MFI DOCUMENT SOLUTIONS KENYA'
                })
            print(f'\n\n\nitem{item}\n\n\n\n')
            item.save()
        


@frappe.whitelist()
def update_toner_acc_items():
	# mfi_customization.mfi.doctype.compatible_items.compatible_items.update_toner_acc_items
	
	# MFI DOCUMENT SOLUTIONS KENYA
	try:
		compatible_items=frappe.get_all('Compatible Items',["type","asset_item","item"])
		if len(compatible_items)>0:
			for compatible_item in compatible_items:
				if compatible_item.get("type")=="Accessories":
					# if not frappe.db.get_value('Compatible Spares Item',{'parent': compatible_item.get("asset_item"),"item_code": compatible_item.get("item")}):
					if compatible_item.get("asset_item")=="1102RL3NL0":
						
						item_doc=frappe.get_doc("Item",compatible_item.get("asset_item"))
						print("not found acc",compatible_item.get("asset_item"),item_doc.name)
						for i in item_doc.get("compatible_spares"):					# if not frappe.db.get_value('Compatible Spares Item',{'parent': compatible_item.get("asset_item"),"item_code": compatible_item.get("item")}):

							if compatible_item.get("item") not in i.item_code:
								print("not found acc",compatible_item.get("asset_item"),item_doc.name)
								item =  {'item_code':compatible_item.get("item"),"company":"MFI DOCUMENT SOLUTIONS KENYA"}
								item_doc.append("compatible_spares", item)
						item_doc.save(ignore_permissions=True)

				# if compatible_item.get("type")=="Toner":
				# 	if not frappe.db.get_value('Asset Item Child Table',{'parent': compatible_item.get("asset_item"),"item_code": compatible_item.get("item")}):
				# 		print("not found toner",compatible_item.get("asset_item"))
				# 		item_doc=frappe.get_doc("Item",compatible_item.get("asset_item"))
				# 		item =  {'item_code':compatible_item.get("item"),"company":"MFI DOCUMENT SOLUTIONS KENYA"}
				# 		item_doc.append("compatible_toners", item)
				# 		item_doc.save(ignore_permissions=True)
					
	except Exception as e:
		print(e)
		frappe.log_error(f"traceback: {frappe.get_traceback()}", f"Failed to  update_toner_acc_items")

				
	