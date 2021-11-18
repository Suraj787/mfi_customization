from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, nowdate, getdate
from frappe import _
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults


def on_submit(doc,method):
	create_sales_order(doc)

def create_sales_order(doc):
	if doc.company=="Mfi managed document solutions ltd":
		sales_doc = get_mapped_doc("Purchase Order", doc.name, {
			"Purchase Order": {
				"doctype": "Sales Order",
				"field_map": {
					"schedule_date":"delivery_date"
				},
			},
			"Purchase Order Item": {
				"doctype": "Sales Order Item"
				}
			}, ignore_permissions=True)
		customer=frappe.db.get_value("Customer", {'represents_company': doc.company},'name')
		sales_doc.customer =customer if customer else ''
		company=frappe.db.get_value("Supplier", {'name': doc.supplier, 'is_internal_supplier':1},'represents_company')
		sales_doc.company =company if company else ''
		sales_doc.po_no=doc.name
		sales_doc.po_date=doc.creation
		sales_doc.selling_price_list=doc.buying_price_list
		for d in sales_doc.get("items"):
			d.warehouse="Stores - MFIINTL"
		sales_doc.save()
		frappe.db.set_value("Sales Order",{"name":sales_doc.name},"delivery_date",doc.schedule_date)

def set_missing_values(source, target):
	target.ignore_pricing_rule = 1
	target.run_method("set_missing_values")
	target.run_method("calculate_taxes_and_totals")

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	return get_mapped_purchase_invoice(source_name, target_doc)

def get_mapped_purchase_invoice(source_name, target_doc=None, ignore_permissions=False):
	def postprocess(source, target):
		currency=frappe.db.get_value("Supplier",source.supplier,"default_currency")
		if not currency or currency!=source.currency:
			frappe.db.set_value("Supplier",source.supplier,"default_currency",source.currency)
		target.flags.ignore_permissions = ignore_permissions
		set_missing_values(source, target)
		#Get the advance paid Journal Entries in Purchase Invoice Advance

		if target.get("allocate_advances_automatically"):
			target.set_advances()

	def update_item(obj, target, source_parent):
		target.amount = flt(obj.amount) - flt(obj.billed_amt)
		target.base_amount = target.amount * flt(source_parent.conversion_rate)
		target.qty = target.amount / flt(obj.rate) if (flt(obj.rate) and flt(obj.billed_amt)) else flt(obj.qty)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)
		target.cost_center = (obj.cost_center
			or frappe.db.get_value("Project", obj.project, "cost_center")
			or item.get("buying_cost_center")
			or item_group.get("buying_cost_center"))

	fields = {
		"Purchase Order": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"party_account_currency": "party_account_currency",
				"supplier_warehouse":"supplier_warehouse"
			},
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"Purchase Order Item": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"name": "po_detail",
				"parent": "purchase_order",
			},
			"postprocess": update_item,
			"condition": lambda doc: (doc.base_amount==0 or abs(doc.billed_amt) < abs(doc.amount))
		},
		"Purchase Taxes and Charges": {
			"doctype": "Purchase Taxes and Charges",
			"add_if_empty": True
		},
	}

	if frappe.get_single("Accounts Settings").automatically_fetch_payment_terms == 1:
		fields["Payment Schedule"] = {
			"doctype": "Payment Schedule",
			"add_if_empty": True
		}

	doc = get_mapped_doc("Purchase Order", source_name,	fields,
		target_doc, postprocess, ignore_permissions=ignore_permissions)

	return doc