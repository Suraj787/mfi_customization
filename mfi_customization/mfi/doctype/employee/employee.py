import frappe
from frappe.model.document import Document

def get_company(doc,method):
    if doc.company not in frappe.db.get_all('User Permission',{'allow':'Company','user':doc.user_id},'for_value',pluck='for_value') or doc.user_id not in frappe.db.get_all('User Permission',{'allow':'Company','for_value':doc.company},'user',pluck='user'):
        if doc.designation != 'Regional Technical Manager':
            print('\n\n\ncompjklkkllk\n\n\n\n')
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
            if doc.designation == 'Call Coordinator':
                user.append("roles", {
                "role": 'Sales Master Manager'
                })
                user.append("roles", {
                "role": 'System Manager'
                })

            if doc.designation == 'Technical Manager':
                user.append("roles", {
                "role": 'Purchase User'
                })
                user.append("roles", {
                "role": 'Stock User'
                })

            if doc.designation == 'Toner Coordinator':
                user.append("roles", {
                "role": 'System Manager'
                })

            # Save the user document
            user.save()

def get_territory(doc,method):
    if doc.territory:
        if (doc.territory not in frappe.db.get_all('User Permission',{'allow':'Territory','user':doc.user_id},'for_value',pluck='for_value') or doc.user_id not in frappe.db.get_all('User Permission',{'allow':'Territory','for_value':doc.territory},'user',pluck='user')) and doc.designation != 'Regional Technical Manager':
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
            if doc.designation == 'Call Coordinator':
                user.append("roles", {
                "role": 'Sales Master Manager'
                    })
                user.append("roles", {
                "role": 'System Manager'
                })

            if doc.designation == 'Technical Manager':
                user.append("roles", {
                "role": 'Purchase User'
                })
                user.append("roles", {
                "role": 'Stock User'
                })

            if doc.designation == 'Toner Coordinator':
                user.append("roles", {
                "role": 'System Manager'
                })

                # Save the user document
            user.save()

def get_type_of_call(doc,method):
    if doc.type_of_call:
        if doc.type_of_call not in frappe.db.get_all('User Permission',{'allow':'Type of Call','user':doc.user_id},'for_value',pluck='for_value') or doc.user_id not in frappe.db.get_all('User Permission',{'allow':'Type of Call','for_value':doc.type_of_call},'user',pluck='user'):
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
            if doc.designation == 'Call Coordinator':
                user.append("roles", {
                "role": 'Sales Master Manager'
                })
                user.append("roles", {
                "role": 'System Manager'
                })

            if doc.designation == 'Technical Manager':
                user.append("roles", {
                "role": 'Purchase User'
                })
                user.append("roles", {
                "role": 'Stock User'
                })

            if doc.designation == 'Toner Coordinator':
                user.append("roles", {
                "role": 'System Manager'
                })

                # Save the user document
            user.save()


def get_roles_checked(doc,method):  
    print('\n\n\nroles checkefd\n\n\n\n')
    if doc.designation == 'Regional Technical Manager':
        print('\n\n\ncompjklkkllk\n\n\n\n')
        user = frappe.get_doc("User", doc.user_id)
        user.append("roles", {
                "role": 'Projects Manager'
        })
        user.append("roles", {
        "role": 'Stock Manager'
        })
        user.save()

