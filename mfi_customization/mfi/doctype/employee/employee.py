import frappe
from frappe.model.document import Document

def get_company(doc,method):
    usr_perm = frappe.new_doc('User Permission')
    usr_perm.user = doc.user_id
    usr_perm.allow = 'Company'
    usr_perm.for_value = doc.company
    usr_perm.apply_to_all_doctypes = 1
    usr_perm.save()
    # user_roles= frappe.get_roles(frappe.session.user)
    # if "Technician" in user_roles:
    user = frappe.get_doc("User", doc.user_id)

    # Add the role to the user's roles property
    user.append("roles", {
        "role": doc.designation
    })

    # Save the user document
    user.save()

def get_territory(doc,method):
    if doc.territory:
        usr_perm = frappe.new_doc('User Permission')
        usr_perm.user = doc.user_id
        usr_perm.allow = 'Territory'
        usr_perm.for_value = doc.territory
        usr_perm.apply_to_all_doctypes = 1
        usr_perm.save()
        # user_roles= frappe.get_roles(frappe.session.user)
        # if "Technician" in user_roles:
        user = frappe.get_doc("User", doc.user_id)

        # Add the role to the user's roles property
        user.append("roles", {
            "role": doc.designation
        })

            # Save the user document
        user.save()

def get_type_of_call(doc,method):
    if doc.type_of_call:
        usr_perm = frappe.new_doc('User Permission')
        usr_perm.user = doc.user_id
        usr_perm.allow = 'Type of Call'
        usr_perm.for_value = doc.type_of_call
        usr_perm.apply_to_all_doctypes = 1
        usr_perm.save()

        user = frappe.get_doc("User", doc.user_id)

        # Add the role to the user's roles property
        user.append("roles", {
            "role": doc.designation
        })

            # Save the user document
        user.save()
      
