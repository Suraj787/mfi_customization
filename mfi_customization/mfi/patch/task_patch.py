import frappe

# bench execute mfi_customization.mfi.patch.task_patch.set_company_in_task_if_not_set
def set_company_in_task_if_not_set():
    for d in frappe.get_all("Task",{"company":""}):
        print(d.name)
        frappe.db.set_value("Task",d.name,'company',"MFI MAROC SARL")