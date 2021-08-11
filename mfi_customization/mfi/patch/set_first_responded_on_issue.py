import frappe
from datetime import datetime

# bench execute mfi_customization.mfi.patch.set_first_responded_on_issue.execute
def execute():
	for d in frappe.get_all("Issue"):
		for tk in frappe.get_all("Task",{"issue": d.name}, ['attended_date_time', 'status']):
			if tk.attended_date_time:
				frappe.db.set_value("Issue", {"name": d.name},"first_responded_on",tk.attended_date_time)
			
