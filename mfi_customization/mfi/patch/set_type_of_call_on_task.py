import frappe
# bench execute mfi_customization.mfi.patch.set_type_of_call_on_task.execute
def execute():
	for d in frappe.get_all("Task"):
		task=frappe.get_doc("Task",d.name)
		if task.issue:
			status = frappe.db.get_value("Issue",{'name':task.issue},"status")
			if status != 'Cancelled':
				type_of_call = frappe.db.get_value("Issue",{'name':task.issue, 'docstatus':['in',[0,1]]},"type_of_call")
				if type_of_call:
					task.type_of_call = type_of_call 
					task.save()