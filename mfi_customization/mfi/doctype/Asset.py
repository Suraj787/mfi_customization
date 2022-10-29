import frappe
def after_insert(doc,method):
    if len(frappe.get_all('Asset Serial No',{"serial_no":doc.serial_no},['name','asset']))>0:
        for d in frappe.get_all('Asset Serial No',{"serial_no":doc.serial_no},['name','asset']):
            if d.asset:
                frappe.throw("serial number already exist")
            else:
                asn=frappe.get_doc('Asset Serial No',d.name)
                asn.asset = doc.name
                asn.location = doc.location
                asn.save()

    else: 
        asn = frappe.new_doc('Asset Serial No')
        asn.subject = doc.serial_no
        asn.serial_no = doc.serial_no
        asn.asset = doc.name
        asn.location = doc.location
        asn.save()

def on_cancel(doc,method):
    #removing serial number on serial number
	frappe.db.delete('Asset Serial No', {'name':doc.serial_no})
    
    
def on_update(doc, method):
    #updating location in Serial No doctype with Asset location change.
 	frappe.db.set_value('Asset Serial No',doc.serial_no,'location',doc.location)
 	
	
def make_task_on_PM_call_interval(doc, method):
    project = frappe.get_value('Project', {'name': doc.project}, 'status')
    if project == "Open":
        if doc.status == "Submitted":
            task_doc = frappe.new_doc('Task')
            task_doc.subject = "PM Call Interval"
            task_doc.customer = frappe.get_value(
                'Project', {'name': doc.project}, 'customer')
            task_doc.asset = doc.name
            task_doc.location = doc.location
            task_doc.type_of_call = "PM"
            task_doc.issue_type = "Preventive"
            task_doc.failure_date_and_time = datetime.today()
            task_doc.raise_by_contact = frappe.get_value(
                'Customer', {'name': task_doc.customer}, 'customer_name')
            task_doc.project = doc.project
            task_doc.status = "Open"
            task_doc.serial_no = doc.serial_no
            task_doc.area = doc.area
            task_doc.sub_location_area = doc.sub_location_area
            task_doc.machine_location = doc.machine_location
            task_doc.completed_by = doc.technician
            task_doc.save()
            print("Task created for project", doc.project)
            print("Asset", doc.name)	
	
    	
