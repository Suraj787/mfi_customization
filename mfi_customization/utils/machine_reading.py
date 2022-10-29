import frappe


@frappe.whitelist()
def repetitive_call(asset,task):
  mr_count = frappe.db.sql("select sum(total) from `tabMachine Reading` where asset = %s", asset)
  mr=str(mr_count)
  mr=mr.replace("(","")
  mr=mr.replace(")","")
  mr=mr.replace(",","")
  mr=mr.replace(".0","")
#   items = []  
  items = frappe.db.sql("select item_code from `tabAsset Item Child Table` where parent = %s", asset)
#   for item in scrapitems:
#        items.append(item[0])
  
  bandw = frappe.db.sql("select total from `tabItem` where name = %s", items)
  b=str(bandw)
  b=b.replace("(","")
  b=b.replace(")","")
  b=b.replace(",","")
  

 
#   frappe.msgprint(ass)
  if mr >= b:
    frappe.db.sql("UPDATE `tabTask` SET `repetitive_call` = 1 WHERE name=%s",task)
    # frappe.msgprint("Grater than or equal")
  else:
    frappe.msgprint("less than or equal")
		



				   