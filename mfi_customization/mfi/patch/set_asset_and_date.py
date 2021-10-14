import frappe
# bench execute mfi_customization.mfi.patch.set_asset_and_date.execute
def execute():
    for i in frappe.get_all("Issue"):
        print(i.name)
        issue=frappe.get_doc("Issue",i.name)
        for d in issue.get("current_reading"):
            if not d.asset:
                frappe.db.set_value("Asset Readings",d.name,"asset",issue.asset)
            if not d.type:
                if d.reading and d.reading_2:
                    frappe.db.set_value("Asset Readings",d.name,"type","Colour")
                elif d.reading:
                    frappe.db.set_value("Asset Readings",d.name,"type","Back & White")
        for d in issue.get("last_readings"):
            if not d.asset:
                frappe.db.set_value("Past Reading",d.name,"asset",issue.asset)
            if not d.type:
                if d.reading and d.reading_2:
                    frappe.db.set_value("Past Reading",d.name,"type","Colour")
                elif d.reading:
                    frappe.db.set_value("Past Reading",d.name,"type","Back & White")

        for tk in frappe.get_all("Task",{"issue":i.name}):
            task=frappe.get_doc("Task",tk.name)
            for d in task.get("current_reading"):
                if not d.asset:
                    frappe.db.set_value("Asset Readings",d.name,"asset",task.asset)
                if not d.type:
                    if d.reading and d.reading_2:
                        frappe.db.set_value("Asset Readings",d.name,"type","Colour")
                    elif d.reading:
                        frappe.db.set_value("Asset Readings",d.name,"type","Back & White")
                if not d.date:
                    frappe.db.set_value("Asset Readings",d.name,"date",task.attended_date_time)

            for d in task.get("last_readings"):
                if not d.asset:
                    frappe.db.set_value("Past Reading",d.name,"asset",task.asset)

            for mr in frappe.get_all("Machine Reading",{"task":tk.name},["name","asset","reading_date","machine_type"]):
                if not mr.asset:
                    frappe.db.set_value("Machine Reading",mr.name,"asset",task.asset)
                if not mr.reading_date:
                    for d in task.get("current_reading"):
                        if d.date:
                            frappe.db.set_value("Machine Reading",mr.name,"reading_date",d.date)
                        else:
                            frappe.db.set_value("Machine Reading",mr.name,"reading_date",task.attended_date_time)
                
                if not mr.machine_type:
                    for d in task.get("current_reading"):
                        if d.reading and d.reading_2:
                            frappe.db.set_value("Machine Reading",mr.name,"machine_type","Colour")
                        elif d.reading:
                            frappe.db.set_value("Machine Reading",mr.name,"machine_type","Back & White")

