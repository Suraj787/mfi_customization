# Copyright (c) 2021, bizmap technologies and contributors
# For license information, please see license.txt

import frappe,json
from frappe.model.delete_doc import delete_doc
from frappe.model.document import Document
from frappe.utils import today,comma_and
from mfi_customization.mfi.doctype.issue import validate

class AssetDeliveryNote(Document):
	# pass
	def validate(self):
		validation(self)
		set_values(self)
	# 	create_stock_entry(self)
	# 	create_assets(self)
	def on_submit(self):
		self.validate_if_asset_not_exist()
		create_stock_entry(self)
	def on_cancel(self):
		delete_or_cancel_asset_and_asset_installation_note(self)
		delete_stock_entry_and_journal_entry(self)

	def validate_if_asset_not_exist(self):
		if len(frappe.get_all("Asset",{"asset_delivery_note":self.name}))==0:
			frappe.throw("Please Create Asset Before Submit")
			
def validation(doc):
	for am in doc.get('asset_models'):
		count=0
		for msn in doc.get("model_serial_nos"):
			if msn.asset_model==am.asset_model:
				count+=1
		if am.qty!=count:
			frappe.throw("Model Serial No row should be Equal to Asset Model Qty")

def set_values(doc):
	for d in frappe.get_all("Default Asset Accounts",{"parent":"MFI Settings","company":doc.company},["asset_account"]):
		doc.fixed_asset_account=d.asset_account

def delete_or_cancel_asset_and_asset_installation_note(doc):
	for asset in frappe.get_all("Asset",{"asset_delivery_note":doc.name},['docstatus','name']):
		asset_doc=frappe.get_doc("Asset",asset.name)
		for asset_inst in frappe.get_all("Asset Installation Note",{"asset":asset.name},['docstatus','name']):
			asset_inst_doc=frappe.get_doc("Asset Installation Note",asset_inst.name)
			if asset_inst.docstatus==1:
				asset_inst_doc.cancel()
			frappe.delete_doc("Asset Installation Note",asset_inst.name)
		delete_asset_movement(asset.name)
		delete_asset_serial_no(asset.name)
		if asset.docstatus==1:
			asset_doc.cancel()
		frappe.delete_doc("Asset",asset_doc.name)
		
def delete_asset_movement(asset):
	parent=[]
	for d in frappe.get_all("Asset Movement Item",{"asset":asset},["parent"]):
		if d.parent not in parent:
			frappe.delete_doc("Asset Movement",d.parent)
		parent.append(d.parent)

def delete_asset_serial_no(asset):
	for d in frappe.get_all("Asset Serial No",{"asset":asset}):
		frappe.delete_doc("Asset Serial No",d.name)

def delete_stock_entry_and_journal_entry(doc):
	for d in frappe.get_all("Stock Entry",{"asset_delivery_note":doc.name}):
		frappe.delete_doc("Stock Entry",d.name)
	for d in frappe.get_all("Journal Entry",{"asset_delivery_note":doc.name}):
		frappe.delete_doc("Journal Entry",d.name)

def create_stock_entry(doc):
	warehouse={}
	for d in  doc.get("model_serial_nos"):
		warehouse.update({d.warehouse:(warehouse.get(d.warehouse) or "") +d.serial_no+","})
	se=frappe.new_doc("Stock Entry")
	se.company=frappe.db.get_value("Sales Order",{"name":doc.get('sales_order')},"company")
	se.stock_entry_type="Material Transfer"
	se.project=doc.project
	se.asset_delivery_note=doc.name
	for itm in doc.get("model_serial_nos"):
		se.append("items",{
			"s_warehouse":itm.warehouse,
			"t_warehouse":frappe.db.get_value("Customer Warehouse Item",{"parent":"MFI Settings","company":se.company},"warehouse"),
			"item_code":itm.asset_model,
			"qty":1,
			"batch_no":itm.batch,
			"serial_no":itm.serial_no,
			"basic_rate":frappe.db.get_value("Item",itm.asset_model,"valuation_rate") or 0,
			"valuation_rate":frappe.db.get_value("Item",itm.asset_model,"valuation_rate") or 0
		})


	se.save()
	se.submit()

@frappe.whitelist()
def create_assets(doc):
	doc=json.loads(doc)
	# if len(frappe.get_all("Asset",{"asset_delivery_note":doc.name}))==0:
	records=[]
	for i,d in enumerate(doc.get("model_serial_nos")):
		# frappe.publish_realtime('update_progress',{"progress": [i, len(doc.get("model_serial_nos"))]}, user=frappe.session.user)
		# frappe.publish_progress(i / len(doc.get("model_serial_nos"))* 100, title=("Updating Assets..."))
		asset=frappe.new_doc("Asset")
		asset.company=frappe.db.get_value("Sales Order",{"name":doc.get('sales_order')},"company")
		asset.item_code=frappe.db.get_value("Item",{"stock_item":d.get("asset_model")},'name')
		asset.item_name=frappe.db.get_value("Item",{"name":asset.item_code},'item_name')
		asset.asset_owner="Company"
		asset.asset_owner_company=asset.company
		asset.asset_name=asset.item_name
		asset.location=d.get("client_location")
		asset.is_existing_asset=1
		asset.gross_purchase_amount=100
		asset.purchase_date=today()
		asset.available_for_use_date=today()
		asset.asset_delivery_note=doc.get("name")
		asset.serial_no=d.get("serial_no")
		asset.project=doc.get("project")
		asset.save()
		asset_installation_note=frappe.new_doc("Asset Installation Note")
		asset_installation_note.company=asset.company
		asset_installation_note.customer=doc.get('customer')
		asset_installation_note.asset=asset.name
		asset_installation_note.asset_name=asset.asset_name
		asset_installation_note.project=doc.get("project")
		asset_installation_note.location=asset.location
		asset_installation_note.asset_serial_no=asset.serial_no
		asset_installation_note.asset_delivery_note=doc.get("name")
		asset_installation_note.save()
		records.append(asset_installation_note.name)
	if records:
		frappe.msgprint("Asset Records Created <b>{0}</b>".format(comma_and(records)))



@frappe.whitelist()
def get_serial_nos(filters):
	filters=json.loads(filters)
	fltr={"status":"Active","company":filters.get("company")}
	if filters.get("item_code"):
		fltr.update({"item_code":filters.get("item_code")})
	qty=0
	for d in filters.get("asset_models"):
		if filters.get("item_code")==d.get("asset_model"):
			qty=d.get("qty")
	data=[]
	for serial_no in frappe.get_all("Serial No",filters=fltr,fields=['item_code','name','warehouse','batch_no','item_name'],order_by="creation"):
		if len(frappe.get_all('Asset Serial No', {'name':serial_no.get('name')}))==0 and len(frappe.get_all('Serial Nos Model wise', {'serial_no':serial_no.get('name'), 'docstatus':1}))==0:
			data.append(serial_no)
	return data[:qty]


@frappe.whitelist()
def get_company_users(doctype, txt, searchfield, start, page_len, filters):
	cond=""
	if filters.get("company"):
		cond=""" where emp.company='{0}'""".format(filters.get("company"))
	if txt :
		cond+=""" and (usr.name like '%{0}%' or usr.full_name like '%{0}%')""".format(txt)
		if not cond:
			cond="""where (usr.name like '%{0}%' or usr.full_name like '%{0}%')""".format(txt)
		
	return frappe.db.sql("""Select usr.name,usr.full_name from `tabUser` usr left join `tabEmployee` emp on emp.user_id=usr.name {0}""".format(cond))