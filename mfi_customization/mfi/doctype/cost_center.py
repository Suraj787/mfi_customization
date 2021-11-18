import frappe,json
from erpnext.controllers.accounts_controller import update_child_qty_rate

@frappe.whitelist()
def update_cost(doc):
	doc=json.loads(doc)
	items=[]
	updated_items=""
	for itm in doc.get('items'):
		for item_price in frappe.get_all("Item Price",{"item_code":itm.get("item_code"),"price_list":doc.get("selling_price_list")},['price_list_rate']):
			if itm.get("rate")!=item_price.price_list_rate:
				itm.update({"rate":item_price.price_list_rate})
				updated_items+=(itm.get("item_code")+',')
		items.append(itm)

	update_child_qty_rate(doc.get("doctype"), json.dumps(items), doc.get("name"))

	if updated_items:
		frappe.msgprint("Items Updated <b>{0}</b>".format(updated_items.rstrip(',')))
	return "ok"

	
