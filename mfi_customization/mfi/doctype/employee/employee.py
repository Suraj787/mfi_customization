import frappe
from frappe.model.document import Document

def get_company(doc,method):
    usr_perm = frappe.new_doc('User Permission')
    usr_perm.user = doc.user_id
    usr_perm.allow = 'Company'
    usr_perm.for_value = doc.company
    usr_perm.apply_to_all_doctypes = 1
    usr_perm.save()

def get_territory(doc,method):
    # if doc.territory:
    usr_perm = frappe.new_doc('User Permission')
    usr_perm.user = doc.user_id
    usr_perm.allow = 'Territory'
    usr_perm.for_value = doc.territory
    usr_perm.apply_to_all_doctypes = 1
    usr_perm.save()