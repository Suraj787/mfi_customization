from frappe.utils import validate_email_address




def validate_support_email(doc, method):
    validate_email_address(doc.support_email, True)
    validate_email_address(doc.toner_support_email, True)
