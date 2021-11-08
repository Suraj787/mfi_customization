# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import data, today,add_days,fmt_money


def execute(filters=None):
	columns  = get_column(filters)
	months=get_prev_months_consum_columns(columns, filters)
	columns.append({'label': 'Average Monthly Consumption', 'fieldname': "avg_monthly_consumption","fieldtype":"Float" })
	warehouse_list=[i['name']  for i in frappe.db.get_list('Warehouse', {'is_group':1, 'company':filters.get('company')}, 'name')]

	for wh in warehouse_list:
		columns.append({'label':wh+' Qty' , 'fieldname':wh,'fieldtype': "Data" })
		
	get_purchase_receipt_qty(columns, filters)
	shipment_list_by_month=get_in_transit_shipment(columns, filters)
	po_names=get_po_name(columns,filters)

	columns.extend([
		{'label':'Total Transit Qty', 'fieldname':'total_transit_qty', 'fieldtype': 'Int'},
		{'label':'Life-Stock on hand plus Transit', 'fieldname':'life_stock_transit', 'fieldtype': 'Float'},
		{'label':'Qty on Sales Order', 'fieldname':'qty_on_sales_order', 'fieldtype': 'Data'},
		{'label':'Purchase Qty to Order Suggestion', 'fieldname':'purchase_qty to_order_suggestion', 'fieldtype': 'Data'},
	])
	
	data     = get_data(filters, columns,months,warehouse_list,shipment_list_by_month,po_names)
	return columns, data

def get_column(filters = None):
	columns = [
		{
			"label":"Part Number",
			"fieldname":"part_number",
			"fieldtype":"Link",
			"options":"Item"
		},
		{
			"label":"Part Name",
			"fieldname":"part_name",
			"fieldtype":"Data" ,
			"width":160 
		},
		{
			"label":"Brand",
			"fieldname":"brand",
			"fieldtype":"Data" ,
			"width":140 
		},
		{
			"label":"For Use In Models",
			"fieldname":"for_use_in_models",
			"fieldtype":"Data"  
		}
	]
	
	return columns
	

def get_data(filters, columns,months_list,warehouse_list,shipment_list_by_month,po):
	data = []
	fltr={"is_stock_item":1}

	if filters.get('item_list'):
		fltr.update({"name":["IN",filters.get('item_list')]})

	if filters.get('item_group_list'):
		fltr.update({"item_group":["IN",[d for d in (filters.get('item_group_list')).split(',')]]})

	if filters.get('brand_list'):
		fltr.update({"brand":["IN",[d for d in (filters.get('brand_list')).split(',')]]})

	last_90_days="""and PR.posting_date between '{0}' and '{1}'""".format(add_days(today(),-90),today())
	between_91_to_180="""and PR.posting_date between '{0}' and '{1}'""".format(add_days(today(),-180),add_days(today(),-91))
	between_181_to_365="""and PR.posting_date between '{0}' and '{1}'""".format(add_days(today(),-365),add_days(today(),-181))
	greater_than_365="""and PR.posting_date<'{0}'""".format(add_days(today(),-365))
	for itm in frappe.get_all('Item',fltr,['item_code','item_name','brand']):
		total_qty=0
		row = {
				'part_number': itm.item_code,
				'part_name': itm.item_name,
				'brand':itm.brand
			   }
		months={mn:0 for mn in months_list}
		for st in frappe.db.sql("""SELECT SI.qty, DATE_FORMAT(S.posting_date, '%c-%y') posting_date, SI.item_code 
			from `tabStock Entry` as S inner join `tabStock Entry Detail` as SI 
			on S.name= SI.parent where SI.item_code = '{0}' 
			and S.stock_entry_type='Material Issue' 
			and S.company = '{1}' """.format(itm.item_code, filters.get('company')), as_dict=1):
			months[st.posting_date]+=st.qty
			total_qty+=st.qty
		for dl in frappe.db.sql("""SELECT DLI.qty, DATE_FORMAT(DL.posting_date, '%c-%y') posting_date, DLI.item_code 
			from `tabDelivery Note` as DL inner join `tabDelivery Note Item` as DLI 
			on DL.name= DLI.parent where DLI.item_code = '{0}' 
			and DL.company = '{1}' """.format(itm.item_code, filters.get('company')), as_dict=1):
			months[dl.posting_date]+=dl.qty
			total_qty+=dl.qty
		row.update(months)
		row["avg_monthly_consumption"]=round((total_qty/6),3)
		
		# warehouse data
		all_warehouse_total=0
		for warehouse in warehouse_list:
			warehouse_qty=0
			for child_w in frappe.db.get_all("Warehouse", {'parent_warehouse':warehouse}, 'name'):
				warehouse_data = frappe.db.sql("""SELECT sum(actual_qty) as qty from tabBin 
					where item_code='{0}' and warehouse = '{1}' """.format(itm.item_code,child_w.name), as_dict=1)
				warehouse_qty += warehouse_data[0]['qty'] or 0
			row[warehouse]=warehouse_qty
			all_warehouse_total+=warehouse_qty
		row['last_90_days']=get_purchase_receipt(itm.item_code,last_90_days,filters.get('company'))
		row['between_91_to_180']=get_purchase_receipt(itm.item_code,between_91_to_180,filters.get('company'))
		row['between_181_to_365']=get_purchase_receipt(itm.item_code,between_181_to_365,filters.get('company'))
		row['greater_than_365']=get_purchase_receipt(itm.item_code,greater_than_365,filters.get('company'))

		# In Stock Qty
		row["in_stock_qty"]=all_warehouse_total

		# life_stock_on_hand
		row["life_stock_on_hand"]=0
		if row.get("avg_monthly_consumption")>0 and row.get("in_stock_qty")>0:
			row["life_stock_on_hand"]=round((row.get("in_stock_qty")/row.get("avg_monthly_consumption")),3)

		# shipment data
		shipment_data=get_shipment_values(itm.item_code,filters.get('company'))
		row.update(shipment_data)
		months_total=0
		for mn in shipment_list_by_month:
			total=0
			for sh in shipment_data:
				if sh in shipment_list_by_month[mn]:
					total+=shipment_data.get(sh)
			if total>0:
				row[mn]=total
				months_total+=total

		#  PO Data
		get_po_data(itm.item_code,filters.get('company'),row,po)
		row["total_transit_qty"]=(row.get('total_eta_po') or 0) + months_total
		if row.get("avg_monthly_consumption") > 0:
			row["life_stock_transit"]=round((row.get("in_stock_qty")+row.get("total_transit_qty"))/row.get("avg_monthly_consumption"),3)
		
		#  SO Data
		get_so_data(itm.item_code,filters.get('company'),row)

		#  purchase_qty_calculation
		purchase_qty_calculation(itm.item_code,row)
		row["price_list"]=filters.get('price_list')
		row["currency"]=frappe.db.get_value("Price List",filters.get('price_list'),"currency")
		for d in frappe.get_all("Item Price",{"item_code":itm.item_code,"price_list":filters.get('price_list')},["currency","price_list_rate"]):
			d['price_list_rate']=fmt_money(d.price_list_rate, currency=d.currency)
			row.update(d)
		data.append(row)
	return data

def get_purchase_receipt(item_code,date_filter,company):
	qty=0

	for pr in frappe.db.sql("""SELECT PRI.qty,PRI.batch_no
			from `tabPurchase Receipt` as PR inner join `tabPurchase Receipt Item` as PRI
			on PR.name= PRI.parent where PRI.item_code = '{0}' 
			and PR.company = '{1}'  {2}""".format(item_code, company,date_filter), as_dict=1):

		if pr.batch_no:
			qty+=(pr.qty-(frappe.db.get_value("Batch",pr.batch_no,"batch_qty") or 0))
		else:
			qty+=pr.qty
	return qty

def get_prev_months_consum_columns(columns, filters):
	from datetime import datetime
	from dateutil.relativedelta import relativedelta
	colms=[]
	months=[]
	for i in range(0, 6):
		dt = datetime.now() + relativedelta(months=-i)
		colms.append({'label': str(dt.month) +'/'+ dt.strftime('%y') , 'fieldname':str(dt.month) +'-'+ dt.strftime('%y'),'fieldtype': "Float" })
		months.append(str(dt.month) +'-'+ dt.strftime('%y'))
	columns.extend(colms[::-1])
	return months

def get_purchase_receipt_qty(columns, filters):
	pr_qty_row = [{"label":"Qty < 90 Daysget_shipment_value","fieldname":"last_90_days", "fieldtype":"Int" },
	{"label":"Qty > 91 Days and < 180 Days","fieldname":"between_91_to_180", "fieldtype":"Int"},
	{"label":"Qty > 181 Days and < 365 Days","fieldname":"between_181_to_365", "fieldtype":"Int"},
	{"label":"Qty > 365 Days","fieldname":"greater_than_365", "fieldtype":"Int"},
	{"label":"In Stock Qty","fieldname":"in_stock_qty", "fieldtype":"Int"},
	{"label":"Life-Stock on hand","fieldname":"life_stock_on_hand", "fieldtype":"Float"}]
	columns.extend(pr_qty_row)

def get_po_name(columns, filters):
	po_names=""
	for po in frappe.db.sql("""SELECT name from `tabPurchase Order` where status IN ("To Receive","To Receive and Bill") and transaction_date 
   		BETWEEN SUBDATE(CURDATE(), INTERVAL 6 MONTH) AND NOW() and company='{0}' """.format(filters.get("company")), as_dict=1):
		columns.append({'label':po.name, 'fieldname':po.name, 'fieldtype': 'Data'})
		po_names+=('"'+po.get("name")+'"'+',')
	columns.append({'label': 'Total ETA PO', 'fieldname': 'total_eta_po', 'fieldtype': 'Data'})
	return po_names.rstrip(',')
	
def get_in_transit_shipment(columns, filters):
	month_list=[]
	custom_columns=[]
	awb_number=[]
	data={}
	for d in frappe.db.sql("""SELECT awb_number, DATE_FORMAT(pickup_date, '%M') pickup_date from `tabShipment` where pickup_date 
    BETWEEN SUBDATE(CURDATE(), INTERVAL 4 MONTH) AND NOW() and pickup_company='{0}' """.format(filters.get("company")), as_dict=1):
		if d.awb_number:
			if d.pickup_date not in month_list:
				awb_number=[]
				month_list.append(d.pickup_date)
				custom_columns.append({'label': 'Total '+ d.pickup_date, 'fieldname':d.pickup_date,'fieldtype': "Int" })
			awb_number.append(d.awb_number)
			custom_columns.append({'label': d.awb_number, 'fieldname':d.awb_number,'fieldtype': "Int" })
			data[d.pickup_date]=awb_number

	columns.extend(custom_columns[::-1])
	return data

def get_shipment_values(item_code,company):
	row={}
	for sh in frappe.db.sql("""SELECT S.awb_number,DLI.qty, DATE_FORMAT(S.pickup_date, '%c-%y') pickup_date,S.name 
		from `tabDelivery Note` as DL 
		inner join `tabDelivery Note Item` as DLI on DL.name= DLI.parent 
		inner join `tabShipment Delivery Note` as SI on SI.delivery_note= DL.name
		inner join `tabShipment` as S on S.name=SI.parent 
		where DLI.item_code = '{0}' and  S.pickup_date BETWEEN SUBDATE(CURDATE(), INTERVAL 4 MONTH) AND NOW() and S.pickup_company = '{1}' """.format(item_code,company), as_dict=1):
		if sh.awb_number:
			row[sh.awb_number]=((row.get(sh.awb_number) or 0)+ sh.qty)
	
	return row

def get_po_data(item_code,company,row,po):
	total_qty=0
	for po in frappe.db.sql("""SELECT POI.qty,PO.name
			from `tabPurchase Order` as PO inner join `tabPurchase Order Item` as POI
			on PO.name= POI.parent where POI.item_code = '{0}' 
			and PO.company = '{1}'  and PO.name IN ({2})""".format(item_code, company,po), as_dict=1):
		total_qty+=po.qty
		row[po.name]=po.qty
	row['total_eta_po']=total_qty

def get_so_data(item_code,company,row):
	so_data=frappe.db.sql("""SELECT sum(SOI.qty) as qty
			from `tabSales Order` as SO inner join `tabSales Order Item` as SOI
			on SO.name= SOI.parent where SOI.item_code = '{0}' 
			and SO.company = '{1}' """.format(item_code, company), as_dict=1)
	row["qty_on_sales_order"]=0
	if so_data[0].qty:
		row["qty_on_sales_order"]=so_data[0].qty

def purchase_qty_calculation(item_code,row):
	row['purchase_qty to_order_suggestion']=0
	lead_time=frappe.db.get_value("Item",item_code,"lead_time") or 0
	if (row.get("life_stock_transit") or 0)<lead_time:
		row['purchase_qty to_order_suggestion']=round(((lead_time-(row.get("life_stock_transit") or 0))*(row.get("avg_monthly_consumption")or 0)),3)
