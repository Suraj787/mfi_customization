import frappe
from datetime import datetime

# bench execute mfi_customization.mfi.patch.set_closing_date_in_issue.execute
def execute():
	for d in frappe.get_all("Issue"):
		for tk in frappe.get_all("Task",{"issue": d.name}, ['completion_date_time']):
			if tk.completion_date_time:
				frappe.db.set_value("Issue", {"name": d.name},"closing_date_time",tk.completion_date_time)
			
