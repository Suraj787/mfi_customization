import frappe,json
from erpnext.controllers.accounts_controller import update_child_qty_rate

@frappe.whitelist()
def update_cost(doc):
	doc=json.loads(doc)
	items=[]
	for itm in doc.get('items'):
		for item_price in frappe.get_all("Item Price",{"item_code":itm.get("item_code"),"price_list":doc.get("selling_price_list")},['price_list_rate']):
			itm.update({"rate":item_price.price_list_rate})
		items.append(itm)

	update_child_qty_rate('Sales Order', json.dumps(items), doc.get("name"))
	return "ok"

	
