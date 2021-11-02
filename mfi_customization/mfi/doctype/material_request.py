import frappe,json
from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate, getdate,today,add_months
from six import string_types, iteritems
from frappe.desk.query_report import run
from frappe import _
from frappe.desk.query_report import get_report_doc,get_prepared_report_result,generate_report_result

def validate(doc,method):
	for emp in frappe.get_all("Employee",{"user_id":frappe.session.user},['material_request_approver']):
		if emp.material_request_approver:
			for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
				if emp2.user_id:
					doc.approver=emp2.user_id
					doc.approver_name=frappe.db.get_value("User",emp2.user_id,"full_name")


def on_submit(doc,method):
	validate_mr(doc)

def validate_mr(doc):
	if doc.report_name and doc.approval_status!="Second Approved":
		frappe.throw("Cann't Submit Before Final Approval")
		
@frappe.whitelist()
def get_approver(user):
	id = ""
	approver_name=""
	for emp in frappe.get_all("Employee",{"user_id":user},['material_request_approver']):
		if emp.material_request_approver:
			for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
				if emp2.user_id:
					id = emp2.user_id
					approver_name=frappe.db.get_value("User",emp2.user_id,"full_name")
					
	return {"approver":id,"approver_name":approver_name}
	
@frappe.whitelist()
def get_approver_name(user):

	return frappe.db.get_value("User",{"email":user},"full_name")


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
	conditions = []

	#Get searchfields from meta and use in Item Link field query
	meta = frappe.get_meta("Item", cached=True)
	searchfields = meta.get_search_fields()

	if "description" in searchfields:
		searchfields.remove("description")

	columns = ''
	extra_searchfields = [field for field in searchfields
		if not field in ["name", "item_group", "description"]]

	if extra_searchfields:
		columns = ", " + ", ".join(extra_searchfields)

	searchfields = searchfields + [field for field in[searchfield or "name", "item_code", "item_group", "item_name"]
		if not field in searchfields]
	searchfields = " or ".join([field + " like %(txt)s" for field in searchfields])
	item_group_list=''
	if filters.get("item_group"):
		item_group_list=",".join(['"'+d.name+'"' for d in frappe.get_all("Item Group",{"parent_item_group":filters.get("item_group")})])
	custom_condition=''
	if item_group_list:
		custom_condition=(" and `tabItem`.item_group IN ("+item_group_list+")")

	description_cond = ''
	if frappe.db.count('Item', cache=True) < 50000:
		# scan description only if items are less than 50000
		description_cond = 'or tabItem.description LIKE %(txt)s'

	return frappe.db.sql("""select tabItem.name,
		if(length(tabItem.item_name) > 40,
			concat(substr(tabItem.item_name, 1, 40), "..."), item_name) as item_name,
		tabItem.item_group,
		if(length(tabItem.description) > 40, \
			concat(substr(tabItem.description, 1, 40), "..."), description) as description
		{columns}
		from tabItem
		where tabItem.docstatus < 2
			and tabItem.has_variants=0
			and tabItem.disabled=0
			and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
			and ({scond} or tabItem.item_code IN (select parent from `tabItem Barcode` where barcode LIKE %(txt)s)
				{description_cond})
			 {mcond} {custom_condition}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
			idx desc,
			name, item_name
		limit %(start)s, %(page_len)s """.format(
			columns=columns,
			scond=searchfields,
			mcond=get_match_cond(doctype).replace('%', '%%'),
			custom_condition=custom_condition,
			description_cond = description_cond),
			{
				"today": nowdate(),
				"txt": "%%%s%%" % txt,
				"_txt": txt.replace("%", ""),
				"start": start,
				"page_len": page_len
			}, as_dict=as_dict)


def set_item_from_material_req(doc,method):
	if doc.get('task_') and doc.status=="Issued":
		task=frappe.get_doc('Task',doc.get('task_'))
		items=[]
		for t in task.get('refilled__items'):
			items.append(t.item)
		for d in doc.get('items'):
			if d.get('item_code') not in items:
				task.append("refilled__items", {
							"item": d.get('item_code'),
							"warehouse": d.get('warehouse'),
							"qty": d.get('qty')
						})
		task.material_request=doc.name
		task.save()   


@frappe.whitelist() 
def get_material_request(current_mr):
	fields = ['name', 'schedule_date', 'status']
	MR_list = frappe.db.get_all("Material Request", filters={'docstatus': 0,"name":("!=",current_mr)}, fields=fields)
	return MR_list

@frappe.whitelist() 
def make_po(checked_values):
	checked_values = json.loads(checked_values)
	item_shipment=[]
	mr_list=[]
	for mr in checked_values:
		mr_list.append(mr.get('name'))
		mr_doc=frappe.get_doc('Material Request',{"name":mr.get('name')})
		for itm in mr_doc.get("item_shipment"):
			item_shipment.append(itm)

	duplicate_items=[]
	status=False
	po_names=[]
	for itm in item_shipment:
		po=frappe.new_doc("Purchase Order")
		po.supplier=itm.supplier
		brand=frappe.db.get_value("Item",itm.item,"brand")
		po.buying_price_list=itm.price_list
		po.currency=frappe.db.get_value("Price List",itm.price_list,"currency")
		po.mode_of_shipment=itm.shipment_type
		if frappe.db.get_value("Item",itm.item,"supplier_category") in ["Toner","Finished Goods"]:
			for i in frappe.get_all("Item Shipment",{"parent":["IN",mr_list],"shipment_type":itm.shipment_type,"supplier":itm.supplier},["name","item","qty","parent"]):
				if frappe.db.get_value("Item",i.item,"brand")==brand and frappe.db.get_value("Item",i.item,"supplier_category") in ["Toner","Finished Goods"]:
					mr_doc=frappe.get_doc('Material Request',{"name":i.get('parent')})
					po.schedule_date=mr_doc.schedule_date
					warehouse=""
					for mr_item in mr_doc.get("items"):
						if mr_item.item_code==i.item:
							warehouse=mr_item.warehouse
					if i.name not in duplicate_items:
						duplicate_items.append(i.name)
						if not frappe.db.get_value("Item Price",{"item_code":itm.item,"price_list":itm.price_list},"price_list_rate"):
							frappe.throw("Item Price Not Exists for Item <b>{0}</b>".format(itm.item))
						po.append("items",{
							"item_code":i.item,
							"qty":i.qty,
							"rate":frappe.db.get_value("Item Price",{"item_code":id,"price_list":itm.price_list},"price_list_rate"),
							"warehouse":warehouse,
							"price_list":itm.price_list
						})
			if po.get("items"):
				status=True
				po.save()
				po_names.append(po.name)
		elif frappe.db.get_value("Item",itm.item,"supplier_category")=="Spares":
			for i in frappe.get_all("Item Shipment",{"parent":["IN",mr_list],"shipment_type":itm.shipment_type,"supplier":itm.supplier},["name","item","qty","parent"]):
				if frappe.db.get_value("Item",i.item,"brand")==brand and frappe.db.get_value("Item",i.item,"supplier_category") =="Spares":
					mr_doc=frappe.get_doc('Material Request',{"name":i.get('parent')})
					po.schedule_date=mr_doc.schedule_date
					warehouse=""
					for mr_item in mr_doc.get("items"):
						if mr_item.item_code==i.item:
							warehouse=mr_item.warehouse
					if i.name not in duplicate_items:
						duplicate_items.append(i.name)
						if not frappe.db.get_value("Item Price",{"item_code":id,"price_list":itm.price_list},"price_list_rate"):
							frappe.throw("Item Price Not Exists for Item <b>{0}</b>".format(itm.item))
						po.append("items",{
							"item_code":i.item,
							"qty":i.qty,
							"rate":frappe.db.get_value("Item Price",{"item_code":id,"price_list":itm.price_list},"price_list_rate"),
							"warehouse":warehouse,
							"price_list":itm.price_list
						})
			if po.get("items"):
				status=True
				po.save()
				po_names.append(po.name)
		else:
			frappe.throw("Supplier Category Not Exists for Item <b>{0}</b>".format(itm.item))
	return {"status":status,"po_names":po_names}


@frappe.whitelist()
def make_material_req(source_name):
	filters=json.loads(source_name)
	report_data=run(filters.get("report_name"),filters.get("filters"))
	doclist=frappe.new_doc("Material Request")
	last_six_months=get_prev_months_consum_columns()
	last_3_months_shipment=get_shipment_months()
	doclist.report_name=filters.get("report_name")
	doclist.filters=filters.get("filters")
	doclist.prepared_report=filters.get("report_id")
	# if report_data.get("result"):
	# 	for resp in report_data.get("result"):
	# 		doclist.append("items",{
	# 			"item_code":resp.get("part_number")
	# 		})

	# 		doclist.append("requisition_analysis_table",{
	# 			"item_code":resp.get("part_number"),
	# 			"item_name":resp.get("part_name"),
	# 			"1st_month":resp.get(last_six_months[0]),
	# 			"2nd_month":resp.get(last_six_months[1]),
	# 			"3rd_month":resp.get(last_six_months[2]),
	# 			"4th_month":resp.get(last_six_months[3]),
	# 			"5th_month":resp.get(last_six_months[4]),
	# 			"6th_month":resp.get(last_six_months[5]),
	# 			"avg_monthly_consumption":resp.get("avg_monthly_consumption"),
	# 			"90_days":resp.get("last_90_days"),
	# 			"180_days":resp.get("between_91_to_180"),
	# 			"365_days":resp.get("between_181_to_365"),
	# 			"365_above_days":resp.get("greater_than_365"),
	# 			"in_stock_qty":resp.get("in_stock_qty"),
	# 			"life_stock_on_hand":resp.get("life_stock_on_hand"),
	# 			"ship_1st_month":last_3_months_shipment[0],
	# 			"ship_2nd_month":last_3_months_shipment[1],
	# 			"ship_3rd_month":last_3_months_shipment[2],
	# 			"total_eta_unknow":resp.get("total_eta_po"),
	# 			"total_transit_qty":resp.get("total_transit_qty"),
	# 			"life_stock_on_hand_plus_transit":resp.get("life_stock_transit"),
	# 			"qty_on_sales_order":resp.get("qty_on_sales_order"),
	# 			"purchase_qty_to_order_suggestion":resp.get("purchase_qty to_order_suggestion")
	# 		})
	return doclist


def get_prev_months_consum_columns():
	from datetime import datetime
	from dateutil.relativedelta import relativedelta
	colms=[]
	for i in range(0, 6):
		dt = datetime.now() + relativedelta(months=-i)
		colms.append(str(dt.month) +'-'+ dt.strftime('%y'))
	return colms[::-1]

def get_shipment_months():
	months=[]
	for d in range(0,3):
		date=add_months(today(),-d)
		months.append(getdate(date).strftime("%B"))
	return months[::-1]


@frappe.whitelist()
@frappe.read_only()
def run(report_name, filters=None, user=None, ignore_prepared_report=False, custom_columns=None):
	report = get_report_doc(report_name)
	if not user:
		user = frappe.session.user
	if not frappe.has_permission(report.ref_doctype, "report"):
		frappe.msgprint(
			_("Must have report permission to access this report."),
			raise_exception=True,
		)

	result = None

	if (
		report.prepared_report
		and not report.disable_prepared_report
		and not ignore_prepared_report
		and not custom_columns
	):
		if filters:
			if isinstance(filters, string_types):
				filters = json.loads(filters)

			dn = filters.get("prepared_report_name")
			filters.pop("prepared_report_name", None)
		else:
			dn = ""
		result = get_prepared_report_result(report, filters, dn, user)
	else:
		result = generate_report_result(report, filters, user, custom_columns)

	result["add_total_row"] = report.add_total_row and not result.get(
		"skip_total_row", False
	)
	result["price_list"]=[d.name for d in frappe.get_all("Price List")]
	item_details={}
	for d in result.get("result"):
		for i in frappe.get_all("Item",{"name":d.get("part_number")},["purchase_uom","carton_qty","description","stock_uom","must_buy_in_purchase_uom"]):
			item_details[d.get("part_number")]=i.update({"uom":i.get("purchase_uom") if i.get("purchase_uom") else i.get("stock_uom"),'conversion_factor':0})
			for uom in frappe.get_all("UOM Conversion Detail",{"parent":d.get("part_number"),"uom":i.get("uom")},['conversion_factor']):
				(item_details[d.get("part_number")]).update(uom)
	
	result["item_details"]=item_details
	return result

@frappe.whitelist()
def create_requisition_reference(doc,requisition_items,table_format):
	doc=json.loads(doc)
	if frappe.db.exists("Requisition Analysis Reference",doc.get("name")):
		requisition_doc=frappe.get_doc("Requisition Analysis Reference",doc.get("name"))
		requisition_doc.set("items",[])
		
	else:
		requisition_doc=frappe.new_doc("Requisition Analysis Reference")
		requisition_doc.material_request=doc.get("name")
	
	print(requisition_items)
	requisition_doc.html_format=table_format
	requisition_doc.items__data=requisition_items
	requisition_doc.save()

@frappe.whitelist()
def get_requisition_analysis_data(doc):
	doc=json.loads(doc)
	if frappe.db.exists("Requisition Analysis Reference",doc.get("name")):
		requisition_doc=frappe.get_doc("Requisition Analysis Reference",doc.get("name"))
		data=json.loads(requisition_doc.get("items__data"))
		sorted_list=sorted(data.items(), key = lambda x: x[1]['total_qty'],reverse=True)
		html_format=json.loads(requisition_doc.get("html_format"))

		html_format_data={}
		for d in html_format.get("result"):
			html_format_data[d.get("part_number")]=d

		data={}
		html_format_result=[]
		for d in sorted_list:
			data[d[0]]=d[1]
			html_format_result.append(html_format_data[d[0]])
			
		html_format["result"]=html_format_result
		return {"html_format":html_format,"data":data}
	return ""
	
