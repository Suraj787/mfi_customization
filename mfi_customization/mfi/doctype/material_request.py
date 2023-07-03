import frappe,json
# from frappe.desk.reportview import get_match_cond, get_filters_cond
from frappe.utils import nowdate, getdate,today,add_months, flt, now_datetime
# from six import string_types, iteritems
# from frappe.desk.query_report import run
from frappe import _
# from datetime import datetime
# import time
# import threading
# from frappe.desk.query_report import get_report_doc,get_prepared_report_result,generate_report_result
from frappe.core.doctype.communication.email import make
from frappe.utils.user import get_users_with_role

from mfi_customization.mfi.doctype.project import get_customer_emails


# def validate(doc,method):
#     for emp in frappe.get_all("Employee",{"user_id":frappe.session.user},['material_request_approver']):
#         if emp.material_request_approver:
#             for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
#                 if emp2.user_id:
#                     doc.approver=emp2.user_id
#                     doc.approver_name=frappe.db.get_value("User",emp2.user_id,"full_name")

def before_save(doc,method):
    set_yeild_details(doc)

# def on_submit(doc,method):
#     validate_mr(doc)

# def validate_mr(doc):
#     if doc.report_name and doc.approval_status!="Second Approved":
#         frappe.throw("Cann't Submit Before Final Approval")

# @frappe.whitelist()
# def get_approver(user):
#     id = ""
#     approver_name=""
#     for emp in frappe.get_all("Employee",{"user_id":user},['material_request_approver']):
#         if emp.material_request_approver:
#             for emp2 in frappe.get_all("Employee",{"name":emp.material_request_approver},['user_id']):
#                 if emp2.user_id:
#                     id = emp2.user_id
#                     approver_name=frappe.db.get_value("User",emp2.user_id,"full_name")

#     return {"approver":id,"approver_name":approver_name}

# @frappe.whitelist()
# def get_approver_name(user):

#     return frappe.db.get_value("User",{"email":user},"full_name")


# @frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
# def item_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
#     conditions = []

#     #Get searchfields from meta and use in Item Link field query
#     meta = frappe.get_meta("Item", cached=True)
#     searchfields = meta.get_search_fields()

#     if "description" in searchfields:
#         searchfields.remove("description")

#     columns = ''
#     extra_searchfields = [field for field in searchfields
#         if not field in ["name", "item_group", "description"]]

#     if extra_searchfields:
#         columns = ", " + ", ".join(extra_searchfields)

#     searchfields = searchfields + [field for field in[searchfield or "name", "item_code", "item_group", "item_name"]
#         if not field in searchfields]
#     searchfields = " or ".join([field + " like %(txt)s" for field in searchfields])
#     item_group_list=''
#     if filters.get("item_group"):
#         item_group_list=",".join(['"'+d.name+'"' for d in frappe.get_all("Item Group",{"parent_item_group":filters.get("item_group")})])
#     custom_condition=''
#     if item_group_list:
#         custom_condition=(" and `tabItem`.item_group IN ("+item_group_list+")")

#     description_cond = ''
#     if frappe.db.count('Item', cache=True) < 50000:
#         # scan description only if items are less than 50000
#         description_cond = 'or tabItem.description LIKE %(txt)s'

#     return frappe.db.sql("""select tabItem.name,
#         if(length(tabItem.item_name) > 40,
#             concat(substr(tabItem.item_name, 1, 40), "..."), item_name) as item_name,
#         tabItem.item_group,
#         if(length(tabItem.description) > 40, \
#             concat(substr(tabItem.description, 1, 40), "..."), description) as description
#         {columns}
#         from tabItem
#         where tabItem.docstatus < 2
#             and tabItem.has_variants=0
#             and tabItem.disabled=0
#             and (tabItem.end_of_life > %(today)s or ifnull(tabItem.end_of_life, '0000-00-00')='0000-00-00')
#             and ({scond} or tabItem.item_code IN (select parent from `tabItem Barcode` where barcode LIKE %(txt)s)
#                 {description_cond})
#              {mcond} {custom_condition}
#         order by
#             if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
#             if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
#             idx desc,
#             name, item_name
#         limit %(start)s, %(page_len)s """.format(
#             columns=columns,
#             scond=searchfields,
#             mcond=get_match_cond(doctype).replace('%', '%%'),
#             custom_condition=custom_condition,
#             description_cond = description_cond),
#             {
#                 "today": nowdate(),
#                 "txt": "%%%s%%" % txt,
#                 "_txt": txt.replace("%", ""),
#                 "start": start,
#                 "page_len": page_len
#             }, as_dict=as_dict)


# def set_item_from_material_req(doc,method):
#     if doc.get('task_') and doc.status=="Issued":
#         task=frappe.get_doc('Task',doc.get('task_'))
#         items=[]
#         for t in task.get('refilled__items'):
#             items.append(t.item)
#         for d in doc.get('items'):
#             if d.get('item_code') not in items:
#                 task.append("refilled__items", {
#                             "item": d.get('item_code'),
#                             "warehouse": d.get('warehouse'),
#                             "qty": d.get('qty')
#                         })
#         task.material_request=doc.name
#         task.save()


# @frappe.whitelist()
# def get_material_request(current_mr):
#     fields = ['name', 'schedule_date', 'status']
#     MR_list = frappe.db.get_all("Material Request", filters={'docstatus': 0,"name":("!=",current_mr)}, fields=fields)
#     return MR_list

# @frappe.whitelist()
# def make_po(checked_values):
#     checked_values = json.loads(checked_values)
#     item_shipment=[]
#     mr_list=[]
#     for mr in checked_values:
#         mr_list.append(mr.get('name'))
#         mr_doc=frappe.get_doc('Material Request',{"name":mr.get('name')})
#         for itm in mr_doc.get("item_shipment"):
#             item_shipment.append(itm)

#     duplicate_items=[]
#     status=False
#     po_names=[]
#     for itm in item_shipment:
#         po=frappe.new_doc("Purchase Order")
#         po.supplier=itm.supplier
#         brand=frappe.db.get_value("Item",itm.item,"brand")
#         po.buying_price_list=itm.price_list
#         po.currency=frappe.db.get_value("Price List",itm.price_list,"currency")
#         po.mode_of_shipment=itm.shipment_type
#         if frappe.db.get_value("Item",itm.item,"supplier_category") in ["Toner","Finished Goods"]:
#             for i in frappe.get_all("Item Shipment",{"parent":["IN",mr_list],"shipment_type":itm.shipment_type,"supplier":itm.supplier},["name","item","qty","parent"]):
#                 if frappe.db.get_value("Item",i.item,"brand")==brand and frappe.db.get_value("Item",i.item,"supplier_category") in ["Toner","Finished Goods"]:
#                     mr_doc=frappe.get_doc('Material Request',{"name":i.get('parent')})
#                     po.schedule_date=mr_doc.schedule_date
#                     warehouse=""
#                     for mr_item in mr_doc.get("items"):
#                         if mr_item.item_code==i.item:
#                             warehouse=mr_item.warehouse
#                     if i.name not in duplicate_items:
#                         duplicate_items.append(i.name)
#                         if not frappe.db.get_value("Item Price",{"item_code":itm.item,"price_list":itm.price_list},"price_list_rate"):
#                             frappe.throw("Item Price Not Exists for Item <b>{0}</b>".format(itm.item))
#                         po.append("items",{
#                             "item_code":i.item,
#                             "qty":i.qty,
#                             "rate":frappe.db.get_value("Item Price",{"item_code":id,"price_list":itm.price_list},"price_list_rate"),
#                             "warehouse":warehouse,
#                             "price_list":itm.price_list
#                         })
#             if po.get("items"):
#                 status=True
#                 po.save()
#                 po_names.append(po.name)
#         elif frappe.db.get_value("Item",itm.item,"supplier_category")=="Spares":
#             for i in frappe.get_all("Item Shipment",{"parent":["IN",mr_list],"shipment_type":itm.shipment_type,"supplier":itm.supplier},["name","item","qty","parent"]):
#                 if frappe.db.get_value("Item",i.item,"brand")==brand and frappe.db.get_value("Item",i.item,"supplier_category") =="Spares":
#                     mr_doc=frappe.get_doc('Material Request',{"name":i.get('parent')})
#                     po.schedule_date=mr_doc.schedule_date
#                     warehouse=""
#                     for mr_item in mr_doc.get("items"):
#                         if mr_item.item_code==i.item:
#                             warehouse=mr_item.warehouse
#                     if i.name not in duplicate_items:
#                         duplicate_items.append(i.name)
#                         if not frappe.db.get_value("Item Price",{"item_code":id,"price_list":itm.price_list},"price_list_rate"):
#                             frappe.throw("Item Price Not Exists for Item <b>{0}</b>".format(itm.item))
#                         po.append("items",{
#                             "item_code":i.item,
#                             "qty":i.qty,
#                             "rate":frappe.db.get_value("Item Price",{"item_code":id,"price_list":itm.price_list},"price_list_rate"),
#                             "warehouse":warehouse,
#                             "price_list":itm.price_list
#                         })
#             if po.get("items"):
#                 status=True
#                 po.save()
#                 po_names.append(po.name)
#         else:
#             frappe.throw("Supplier Category Not Exists for Item <b>{0}</b>".format(itm.item))
#     return {"status":status,"po_names":po_names}


# @frappe.whitelist()
# def make_material_req(source_name):
#     filters=json.loads(source_name)
#     report_data=run(filters.get("report_name"),filters.get("filters"))
#     doclist=frappe.new_doc("Material Request")
#     last_six_months=get_prev_months_consum_columns()
#     last_3_months_shipment=get_shipment_months()
#     doclist.report_name=filters.get("report_name")
#     doclist.filters=filters.get("filters")
#     doclist.prepared_report=filters.get("report_id")




	# if report_data.get("result"):
	#   for resp in report_data.get("result"):
	#       doclist.append("items",{
	#           "item_code":resp.get("part_number")
	#       })

	#       doclist.append("requisition_analysis_table",{
	#           "item_code":resp.get("part_number"),
	#           "item_name":resp.get("part_name"),
	#           "1st_month":resp.get(last_six_months[0]),
	#           "2nd_month":resp.get(last_six_months[1]),
	#           "3rd_month":resp.get(last_six_months[2]),
	#           "4th_month":resp.get(last_six_months[3]),
	#           "5th_month":resp.get(last_six_months[4]),
	#           "6th_month":resp.get(last_six_months[5]),
	#           "avg_monthly_consumption":resp.get("avg_monthly_consumption"),
	#           "90_days":resp.get("last_90_days"),
	#           "180_days":resp.get("between_91_to_180"),
	#           "365_days":resp.get("between_181_to_365"),
	#           "365_above_days":resp.get("greater_than_365"),
	#           "in_stock_qty":resp.get("in_stock_qty"),
	#           "life_stock_on_hand":resp.get("life_stock_on_hand"),
	#           "ship_1st_month":last_3_months_shipment[0],
	#           "ship_2nd_month":last_3_months_shipment[1],
	#           "ship_3rd_month":last_3_months_shipment[2],
	#           "total_eta_unknow":resp.get("total_eta_po"),
	#           "total_transit_qty":resp.get("total_transit_qty"),
	#           "life_stock_on_hand_plus_transit":resp.get("life_stock_transit"),
	#           "qty_on_sales_order":resp.get("qty_on_sales_order"),
	#           "purchase_qty_to_order_suggestion":resp.get("purchase_qty to_order_suggestion")
	#       })
	# return doclist


# def get_prev_months_consum_columns():
#     from datetime import datetime
#     from dateutil.relativedelta import relativedelta
#     colms=[]
#     for i in range(0, 6):
#         dt = datetime.now() + relativedelta(months=-i)
#         colms.append(str(dt.month) +'-'+ dt.strftime('%y'))
#     return colms[::-1]

# def get_shipment_months():
#     months=[]
#     for d in range(0,3):
#         date=add_months(today(),-d)
#         months.append(getdate(date).strftime("%B"))
#     return months[::-1]


# @frappe.whitelist()
# @frappe.read_only()
# def run(report_name, filters=None, user=None, ignore_prepared_report=False, custom_columns=None):
#     report = get_report_doc(report_name)
#     if not user:
#         user = frappe.session.user
#     if not frappe.has_permission(report.ref_doctype, "report"):
#         frappe.msgprint(
#             _("Must have report permission to access this report."),
#             raise_exception=True,
#         )

#     result = None

#     if (
#         report.prepared_report
#         and not report.disable_prepared_report
#         and not ignore_prepared_report
#         and not custom_columns
#     ):
#         if filters:
#             if isinstance(filters, string_types):
#                 filters = json.loads(filters)

#             dn = filters.get("prepared_report_name")
#             filters.pop("prepared_report_name", None)
#         else:
#             dn = ""
#         # result = get_prepared_report_result(report, filters, dn, user)
#         result = generate_report_result(report, filters, user, custom_columns)
#     else:
#         result = generate_report_result(report, filters, user, custom_columns)

#     result["add_total_row"] = report.add_total_row and not result.get(
#         "skip_total_row", False
#     )
#     result["price_list"]=[d.name for d in frappe.get_all("Price List")]
#     item_details={}
#     for d in result.get("result"):
#         for i in frappe.get_all("Item",{"name":d.get("part_number")},["purchase_uom","carton_qty","description","stock_uom","must_buy_in_purchase_uom"]):
#             item_details[d.get("part_number")]=i.update({"uom":i.get("purchase_uom") if i.get("purchase_uom") else i.get("stock_uom"),'conversion_factor':0})
#             for uom in frappe.get_all("UOM Conversion Detail",{"parent":d.get("part_number"),"uom":i.get("uom")},['conversion_factor']):
#                 (item_details[d.get("part_number")]).update(uom)

#     result["item_details"]=item_details
#     return result

# @frappe.whitelist()
# def create_requisition_reference(doc,requisition_items,table_format):
#     doc=json.loads(doc)
#     if frappe.db.exists("Requisition Analysis Reference",doc.get("name")):
#         requisition_doc=frappe.get_doc("Requisition Analysis Reference",doc.get("name"))
#         requisition_doc.set("items",[])

#     else:
#         requisition_doc=frappe.new_doc("Requisition Analysis Reference")
#         requisition_doc.material_request=doc.get("name")

#     print(requisition_items)
#     requisition_doc.html_format=table_format
#     requisition_doc.items__data=requisition_items
#     requisition_doc.save()

# @frappe.whitelist()
# def get_requisition_analysis_data(doc):
#     doc=json.loads(doc)
#     if frappe.db.exists("Requisition Analysis Reference",doc.get("name")):
#         requisition_doc=frappe.get_doc("Requisition Analysis Reference",doc.get("name"))
#         data=json.loads(requisition_doc.get("items__data"))
#         sorted_list=sorted(data.items(), key = lambda x: x[1]['total_qty'],reverse=True)
#         html_format=json.loads(requisition_doc.get("html_format"))

#         html_format_data={}
#         for d in html_format.get("result"):
#             html_format_data[d.get("part_number")]=d

#         data={}
#         html_format_result=[]
#         for d in sorted_list:
#             data[d[0]]=d[1]
#             html_format_result.append(html_format_data[d[0]])

#         html_format["result"]=html_format_result
#         return {"html_format":html_format,"data":data}
#     return ""


@frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
def item_child_table_filters(asset,company,task):
	l = []
	frappe.log_error(f'task,{task}')
	asset_item = frappe.db.get_value('Asset',{'name':asset},'item_code')
	task = frappe.db.get_value('Task',{'name':task},'type_of_call')
	it = frappe.get_doc('Item',asset_item)
	for i in it.compatible_spares:
		l.append(i.item_code)

	return l
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_code_filteration(doctype, txt, searchfield, start, page_len, filters):

	if frappe.db.get_value('Task',{'name':filters.get("task")},'type_of_call')=="Toner":
		query="""
        SELECT item_code,item_name
        FROM `tabAsset Item Child Table`
        WHERE
		parentfield="compatible_toners"
		and
       company='{0}'
       and parent='{1}'
        """.format(filters.get("company"),frappe.db.get_value('Asset',filters.get("asset"),'item_code'))
		if txt:
			query+=' AND (name like "%{0}%" OR item_name like "%{0}%")'.format(txt)
		return frappe.db.sql(query,as_list=True)

		# return frappe.db.get_all('Asset Item Child Table',{'company':filters.get("company"),'parent': frappe.db.get_value('Asset',filters.get("asset"),'item_code'),'parentfield':"compatible_toners"},['item_code'],as_list=1)
	else:
		query="""
        SELECT item_code,item_name
        FROM `tabCompatible Spares Item`
        WHERE
		parentfield="compatible_spares"
		and
       company='{0}'
       and parent='{1}'
        """.format(filters.get("company"),frappe.db.get_value('Asset',filters.get("asset"),'item_code'))
		if txt:
			query+=' AND (name like "%{0}%" OR item_name like "%{0}%")'.format(txt)
		return frappe.db.sql(query,as_list=True)
		# return frappe.db.get_all('Compatible Spares Item',{'company':filters.get("company"),'parent':frappe.db.get_value('Asset',filters.get("asset"),'item_code'),'parentfield':"compatible_spares"},['item_code'],as_list=1)




@frappe.whitelist()
# @frappe.validate_and_sanitize_search_inputs
def get_atm_users(doctype, txt, searchfield, start, page_len, filters):
	user_list = []
	user_list.extend(get_users_with_role("Area Technical Manager"))
	user_list.extend(get_users_with_role("Technical Manager"))
	users = []
	for user in user_list:
		employee = frappe.get_all("Employee", {'user_id': user, 'company': filters.get('company')})
		user_enabled = frappe.db.get_value("User", user, 'enabled')
		if employee and user_enabled:
			users.append(user)
	search_cond = ''
	if txt:
		search_cond = f" and u.{searchfield} like '%{txt}%' "
	sql_users = str(tuple([key for key in users])).replace(',)', ')')
	query = f""" select u.name, u.full_name from `tabUser` u where u.name in {sql_users} {search_cond}"""
	return frappe.db.sql(query)


def onload(doc,method):
	project_name= frappe.db.get_value('Asset',{'name':doc.asset},'project')
	doc.set('comprehensive_contract',[])
	doc.set('labour_contract',[])
	labour_itm =frappe.db.sql(f"""
	 SELECT labour_contract_item from `tabContract Terms` where parent= "{project_name}" """, as_dict=1)
	for lbr_itm in labour_itm:
		 doc.append("labour_contract",{
		 "labour_contract_item":lbr_itm.labour_contract_item
		 })


def set_yeild_details(doc):
	machine_reading_list= frappe.db.sql(f"""select name, total from `tabMachine Reading` where asset ='{doc.asset}' ORDER BY name DESC """,as_dict=1)
	asset_reading=0
	for reading in machine_reading_list:
		machn_doc = frappe.get_doc("Machine Reading", reading)
		# if len(machn_doc.items) == 0:
		asset_reading = machn_doc.total
			# print(f"asset_reading {asset_reading}")
		if asset_reading:
			break
	doc.items_with_yeild = []
	for i in doc.get('items'):
		machine_reding_with_itm =[i.total for i in  frappe.db.sql(f"""select m.total, m.reading_date from `tabMachine Reading` as m inner join `tabAsset Item Child Table` as a on a.parent=m.name where m.asset ='{doc.asset}' and a.item_code ='{i.item_code}' ORDER BY m.name DESC LIMIT 3 """,as_dict=1)if i.total is not None ]
		item_yeild =[itm.yeild for itm in frappe.db.sql(f""" SELECT yeild from `tabItem` where item_code ='{i.item_code}' """,as_dict=1)]
		coverage = [cvrg.coverage for cvrg in frappe.db.sql(f""" SELECT coverage from `tabItem` where item_code='{i.item_code}'""",as_dict=1) ]
		print(f"asset_reading {asset_reading}")

		if asset_reading:
			if  machine_reding_with_itm:
				percent = (int(item_yeild[0])/int(machine_reding_with_itm[0]))*100
				last_coverage = (float(coverage[0])/100) * (percent/100)
				doc.append("items_with_yeild",{
					"item_code": i.item_code,
					"item_name": i.item_name,
					"item_group": i.item_group,
					"yeild":int(asset_reading) - int(machine_reding_with_itm[0]) ,
					"total_yeild" :float(item_yeild[0]),
					"last_coverage":"%.6f"% last_coverage,
					"1st_reading":int(asset_reading) - int(machine_reding_with_itm[0]) if 0 < len(machine_reding_with_itm) else 0,
					"2nd_reading": int(asset_reading) - int(machine_reding_with_itm[1]) if 1 < len(machine_reding_with_itm) else 0,
					"3rd_reading": int(asset_reading) - int(machine_reding_with_itm[2]) if 2 < len(machine_reding_with_itm) else 0
					})
			else:
				mchn_reading_installation = frappe.db.sql("""select name, total from `tabMachine Reading`
				where asset ='{0}' and reading_type = 'Installation' ORDER BY name DESC LIMIT 3""".format(doc.asset),as_dict=1)
				if mchn_reading_installation and mchn_reading_installation[0]['total']:
					frappe.msgprint(" asset_reading {0} and mchn_reading_installation {1} for item '{2}'".format(asset_reading, mchn_reading_installation[0]['total'],i.item_code) )
					doc.append("items_with_yeild",{
						"item_code": i.item_code,
						"item_name": i.item_name,
						"item_group": i.item_group,
						"yeild":int(asset_reading) - int(mchn_reading_installation[0]['total']) ,
						"total_yeild" :float(item_yeild[0]),
						"last_coverage":"%.6f"% last_coverage,
						"1st_reading":int(asset_reading) - int(mchn_reading_installation[0]['total']),
						"2nd_reading":int(asset_reading) - int(mchn_reading_installation[1]['total']),
						"3rd_reading":int(asset_reading) - int(mchn_reading_installation[2]['total'])

						})
				# else:
				# 	frappe.msgprint("Machine reading not found for any item or for type installation.")



#def before_submit(doc,method):
#    for i in doc.get('items_with_yeild'):
#        coverage = [cvrg.coverage for cvrg in frappe.db.sql(f""" SELECT coverage from `tabItem` where item_code='{i.item_code}'""",as_dict=1) ]
#        if i.last_coverage > coverage[0]:
#           frappe.throw("coverage is low ")



def on_submit(doc,method):
	itm_child_data_into_issue(doc)
	if doc.task:
		frappe.db.set_value("Task", doc.task, 'status', 'Material Issued')
		issue = frappe.db.get_value("Task",{'name': doc.task}, 'issue')
		if issue:
			frappe.db.set_value("Issue", issue, 'status', 'Material Issued')
	set_yeild_details_on_machine_reading(doc)


def set_yeild_details_on_machine_reading(doc):
	if doc.asset and doc.task:
		machine_reading_list = frappe.db.get_list("Machine Reading",{'asset':doc.asset}, 'name')
		for machine_reading in machine_reading_list:
			machine_reading_doc = frappe.get_doc('Machine Reading', machine_reading['name'])
			machine_reading_doc.items=[]
			for i in doc.items_with_yeild:
				reading_child = machine_reading_doc.append("items", {})
				reading_child.item_code= i.item_code
				reading_child.item_name= i.item_name
				reading_child.item_group= i.item_group
				reading_child.yeild= frappe.db.get_value("Item", {'name':i.item_code}, 'yeild')
				current_reading =[m.total for m in frappe.db.sql(f"""select m.reading_date, m.total as total from `tabMachine Reading` as m
				 inner join `tabAsset Item Child Table` as a on a.parent=m.name
				 where m.asset ='{doc.asset}' ORDER BY reading_date DESC LIMIT 1""",as_dict=1)]

				first_reading =[m.total for m in frappe.db.sql(f"""select m.reading_date, m.total as total
					from `tabMachine Reading` as m inner join `tabAsset Item Child Table` as a
					on a.parent=m.name where m.asset ='{doc.asset}' and a.item_code ='{i.item_code}' ORDER BY reading_date ASC LIMIT 1""",as_dict=1)]
				if current_reading and first_reading:
					reading_child.total_reading = flt(current_reading[0]) - flt(first_reading[0])
					if reading_child.total_reading > 0:
						reading_child.percentage_yeild = round((reading_child.yeild * 100)/(reading_child.total_reading),2)
				machine_reading_doc.save(ignore_permissions=True)


def set_item_details(doc,method):
	machine_reading_asset=[i.total for i in frappe.db.sql(f"""select max(reading_date),total from `tabMachine Reading` where asset ='{doc.asset}' """,as_dict=1)if i.total is not None]
	if doc.task and machine_reading_asset:
		if len(doc.items_with_yeild) == 0:
			doc.items_with_yeild=[]
			for i in doc.items:
				machine_reding_with_itm =[i.total for i in  frappe.db.sql(f"""select max(m.reading_date),m.total from `tabMachine Reading` as m inner join `tabAsset Item Child Table` as a on a.parent=m.name where m.asset ='{doc.asset}' and a.item_code ='{i.item_code}' and m.task='{doc.task}' """,as_dict=1)if i.total is not None ]
				item_yeild =[itm.yeild for itm in frappe.db.sql(f""" SELECT yeild from `tabItem` where item_code ='{i.item_code}' """,as_dict=1)]
				if machine_reding_with_itm:
					mr_child = doc.append("items_with_yeild",{})
					mr_child.item_code= i.item_code
					mr_child.item_name= i.item_name
					mr_child.item_group= i.item_group
					mr_child.yeild=int(machine_reding_with_itm[0]) - int(machine_reading_asset[0])
					mr_child.total_yeild =float(item_yeild[0])
					doc.save()

def notify_client_about_material_requested(doc, method):
	"""
	Email clients about material request for their task ticket
	"""
	if doc.task:
		issue = frappe.db.get_value("Task", doc.task, 'issue')
		if issue:
			subject = f"""Material request created for issue {issue}"""

			# notify client
			# email_body = f"""Kindly Note that Your Task Ticket Number {issue} is awaiting material to be resolved."""
			# recipients = get_customer_emails(doc.project)
			# make(subject = subject, content=email_body, recipients=recipients,
			#         send_email=True, sender="erp@groupmfi.com")

			# notify helpdesk
			email_body = f"""Kindly note that Material Request for ticket number {issue} is awaiting your approval"""
			recipients = frappe.db.get_value("Company", doc.company, "support_email")
			type_of_call = frappe.db.get_value("Task", doc.task, 'type_of_call')

			if type_of_call == "Toner":
				recipients = frappe.db.get_value("Company", doc.company, "toner_support_email")
			make(subject = subject, content=email_body, recipients=recipients,
					send_email=True, sender="erp@groupmfi.com")


def notify_helpdesk_about_material_approval(doc, method):
	""" Notify Helpdesk when Material Request is approved for a ticket"""
	if doc.docstatus == 1 and doc.task:
		issue = frappe.db.get_value("Task", doc.task, 'issue')
		if issue:
			# notify helpdesk
			subject = f"""Material request approved for ticket {issue}"""
			email_body = f"""Kindly note that material request for ticket number {issue} has been approved."""
			recipients = frappe.db.get_value("Company", doc.company, "support_email")
			type_of_call = frappe.db.get_value("Task", doc.task, 'type_of_call')
			if type_of_call == "Toner":
				recipients = frappe.db.get_value("Company", doc.company, "toner_support_email")
			make(subject = subject, content=email_body, recipients=recipients,
					send_email=True, sender="erp@groupmfi.com")

			# notify client
			# email_body = f"""Task Ticket number {issue} has been dispatched, kindly expect it any time soon."""
			# recipients = get_customer_emails(doc.project)
			# make(subject = subject, content=email_body, recipients=recipients,
			#         send_email=True, sender="erp@groupmfi.com")


@frappe.whitelist()
def material_reject(doc):
	doc = json.loads(doc)
	doc_mr = frappe.get_doc("Material Request", doc.get("name"))
	doc_mr.mr_status = "Material Rejected"
	doc_mr.cancel()
	task_reject(doc_mr.task)
	issue_reject(doc_mr.task)


def task_reject(task):
	task = frappe.get_doc("Task", task)
	task.mr_status = "Material Rejected"
	task.save()


def issue_reject(task):
	issue = frappe.db.get_value("Task", task, 'issue')
	issue = frappe.get_doc("Issue", issue)
	issue.mr_status = "Material Rejected"
	issue.save()


def itm_child_data_into_issue(doc):
    Task=frappe.get_doc("Task", doc.task)
    if Task:
       get_issue=frappe.get_doc("Issue",Task.issue)
       if doc.items:
          for i in doc.items:
              issue_itm=get_issue.append("items",{})
              issue_itm.item_code=i.item_code
              issue_itm.item_name=i.item_name
              issue_itm.schedule_date = i.schedule_date
              issue_itm.warehouse=i.warehouse
              issue_itm.description=i.description
              issue_itm.qty=i.qty
              issue_itm.stock_uom=i.stock_uom
              issue_itm.uom=i.uom
              issue_itm.conversion_factor=i.conversion_factor
              get_issue.save()

def pause_task(doc, event):
	if doc.task and doc.material_request_type == "Material Issue":
		task = frappe.get_doc("Task", doc.task)
		paused_datetime = {row.technician: row.paused for row in task.technician_productivity_matrix}
		if task.completed_by in paused_datetime and not paused_datetime[task.completed_by]:
			for i in task.technician_productivity_matrix:
				if i.technician == task.completed_by and not i.material_request:
					i.paused = now_datetime()
					i.material_request = now_datetime()

		else:
			row = task.append("technician_productivity_matrix", {})
			row.technician = task.completed_by
			row.paused = now_datetime()
			row.material_request = now_datetime()

		task.save()

def set_material_issued_on_task(doc, event):
	if frappe.db.get_value("Material Request", doc.name, "workflow_state")!= "Approved" and doc.workflow_state=="Approved":
		task = frappe.get_doc("Task", doc.task)
		paused_datetime = {row.technician: row.material_issued for row in task.technician_productivity_matrix}
		if task.completed_by in paused_datetime and not paused_datetime[task.completed_by]:
			for i in task.technician_productivity_matrix:
				if i.technician == task.completed_by and not i.material_issued:
					i.paused = now_datetime()
					i.material_issued = now_datetime()

		else:
			row = task.append("technician_productivity_matrix", {})
			row.technician = task.completed_by
			row.paused = now_datetime()
			row.material_issued = now_datetime()

		task.save()