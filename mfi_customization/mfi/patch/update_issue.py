import frappe
# bench execute mfi_customization.mfi.patch.update_issue.execute
def execute():
    set_location()

def set_location():
    for issue in frappe.get_all("Issue",['name','location']):
        if not issue.location:
            for tk in frappe.get_all("Task",{"issue":issue.name},['location']):
                if tk.location:
                    frappe.db.set_value("Issue",{"name":issue.name},"location",tk.location)