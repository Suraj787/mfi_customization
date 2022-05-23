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
 	
    	
