import frappe

def execute():
    # for issue in frappe.get_all("Issue",['name','customer','serial_no','asset','location']):
    for tk in frappe.get_all("Task",{"status":("!=","Cancelled")},["name","issue"]):
        print(tk.name)
        issue=frappe.get_doc("Issue",tk.issue)
        # print(tk.name)
        task=frappe.get_doc("Task",tk.name)
        task.customer=issue.customer
        task.serial_no=issue.serial_no
        task.asset=issue.asset
        task.location=frappe.db.get_value("Asset",issue.asset,"location") if issue.asset else issue.location
        if task.location != issue.location or not task.customer:
            task.customer=issue.customer
            if issue.asset:
                for ass in frappe.get_all("Asset",{"name":issue.asset},["project","location","serial_no"]):
                    frappe.db.set_value("Issue",issue.name,'location',ass.location)
                    frappe.db.set_value("Task",task.name,'location',ass.location)
                    frappe.db.set_value("Issue",issue.name,'serial_no',ass.serial_no)
                    frappe.db.set_value("Task",task.name,'serial_no',ass.serial_no)
                    if ass.project:
                        frappe.db.set_value("Issue",issue.name,'customer',frappe.db.get_value("Project",ass.project,"customer"))
                        frappe.db.set_value("Task",task.name,'customer',frappe.db.get_value("Project",ass.project,"customer"))

    
               