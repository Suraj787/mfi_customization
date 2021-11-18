
from __future__ import unicode_literals
import frappe
import json
import frappe.utils
from frappe.utils import flt
from frappe import _
from frappe.model.utils import get_fetch_values
from frappe.model.mapper import get_mapped_doc
from frappe.contacts.doctype.address.address import get_company_address
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults

def on_submit(doc,method):
	create_po(doc)

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None, skip_item_mapping=False):
	target_doc=None
	skip_item_mapping=False
	shipment = frappe.flags.args.shipment_type
	sales_doc=frappe.get_doc("Sales Order",source_name)
	def set_missing_values(source, target):
		target.ignore_pricing_rule = 1
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")

		if source.company_address:
			target.update({'company_address': source.company_address})
		else:
			# set company address
			target.update(get_company_address(target.company))

		if target.company_address:
			target.update(get_fetch_values("Delivery Note", 'company_address', target.company_address))

	def update_item(source, target, source_parent):
		target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.base_rate)
		target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
		target.qty = flt(source.qty) - flt(source.delivered_qty)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)

		if item:
			target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center") \
				or item.get("buying_cost_center") \
				or item_group.get("buying_cost_center")
	
	mapper = {
		"Sales Order": {
			"doctype": "Delivery Note",
			"validation": {
				"docstatus": ["=", 1]
			}
		},
		"Sales Taxes and Charges": {
			"doctype": "Sales Taxes and Charges",
			"add_if_empty": True
		},
		"Sales Team": {
			"doctype": "Sales Team",
			"add_if_empty": True
		}
	}

	if not skip_item_mapping:
		mapper["Sales Order Item"] = {
			"doctype": "Delivery Note Item",
			"field_map": {
				"rate": "rate",
				"name": "so_detail",
				"parent": "against_sales_order",
			},
			"postprocess": update_item,
			"condition": lambda doc: abs(doc.delivered_qty) < abs(doc.qty) and doc.delivered_by_supplier!=1
		}

	target_doc = get_mapped_doc("Sales Order", source_name, mapper, target_doc, set_missing_values)

	sorted_items=[]
	for item_sp in sales_doc.get("item_shipment"):
		if item_sp.shipment_type==shipment:
			sorted_items.append(item_sp.item)

	for i,d in enumerate(target_doc.get("items")):
		if d.item_code not in sorted_items:
			del target_doc.get("items")[i]
	return target_doc

def create_po(doc):
	from frappe.contacts.doctype.address.address import get_address_display
	if doc.company=="MFI International FZE":
		duplicate=[]
		items=[]
		for itm in doc.get("items"):
			rows=[]
			for itm2 in doc.get("items"):
				if itm.price_list==itm2.price_list and itm.price_list not in duplicate:
					rows.append(itm2)
			duplicate.append(itm.price_list)
			items.append(rows)
			
		for i in items:
			if i:
				po=frappe.new_doc("Purchase Order")
				po.schedule_date=doc.delivery_date
				po.company=doc.company
				po.mode_of_shipment=doc.mode_of_shipment
				po.order_confirmation_no=doc.name
				po.order_confirmation_date=doc.transaction_date
				for row in i:
					po.ship_to=row.ship_to
					po.address=row.address
					po.address_detail=get_address_display({"address_dict": row.address})
					po.currency=frappe.db.get_value("Price List",row.price_list,"currency")
					po.buying_price_list=row.price_list
					for sup in frappe.get_all("Price List Supplier",{"parent":row.price_list,"company":doc.company},["supplier"]):
						po.supplier=sup.supplier
				for itm in i:
					row={}
					for key in ["item_code","item_name","required_date","description","qty","uom","conversion_factor","stock_uom","stock_qty","price_list_rate","base_price_list_rate","rate","rate_amount","base_rate","base_amount","stock_uom_rate","net_rate","net_amount","base_net_rate","base_net_amount","billed_amt","gross_profit","price_list","ship_to","address"]:
						row[key]=itm.get(key)
					row["warehouse"]=doc.get("set_warehouse")
					row["price_list_rate"]=itm.get("item_purchase_rate")
					po.append("items",row)

				po.save()

@frappe.whitelist()
def get_customer_by_price_list(doctype, txt, searchfield, start, page_len, filters):
	data=[]
	for d in frappe.get_all("Price List Country",{"parent":filters.get("price_list")},["customer"]):
		for cust in frappe.get_all("Customer",{"name":d.customer},["name","customer_name","customer_group","territory", "mobile_no","primary_address"],as_list=1):
			data.append(cust)
	return data