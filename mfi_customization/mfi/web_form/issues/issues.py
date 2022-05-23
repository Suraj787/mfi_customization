from __future__ import unicode_literals

import frappe

def get_context(context):
	# do your magic here
	pass
	
	
@frappe.whitelist()
def get_logged_user():
    user = frappe.db.get_value('User',{"name":frappe.session.user},"full_name")
    customerId=frappe.db.get_all("Customer", filters={"customer_name":user},fields ={"name"})
    return customerId

    frappe.response["message"] = {
        "success_key":1,
        "message":"Authentication success",
        "sid":frappe.session.sid,
        "api_key":user.api_key,
        "username":user.username,
        "email":user.email
    }
	

@frappe.whitelist()		
def get_location(customerId):
    location_list=[]
    project_list = [p.name for p in frappe.db.get_list("Project", filters={"customer":customerId},fields={"name"})]
    for p in project_list:
        location =frappe.db.get_list("Asset",{"project":p},"location")
        [location_list.append(Location) for Location in location if Location not in location_list]
    return location_list   
        
	
@frappe.whitelist()		
def get_Customer_name(customer):
    A=frappe.db.get_all("Customer", filters={"name":customer},fields ={"customer_name"})
    full_name=A[0]["customer_name"]
    return full_name



@frappe.whitelist()
def get_Asset(customerId,location):
    getcompany=[]
    on_basis_company_customer=[]
    cpny_and_locn1=[]
    project_list = [p.name for p in frappe.db.get_list("Project", filters={"customer":customerId},fields={"name"})]
    for p in project_list:
        company =frappe.db.get_list("Asset",filters={"project":p},fields={"company"})
        [getcompany.append(cmpny) for cmpny in company]
        for I in getcompany:
            company_customer =frappe.db.get_all("Asset",filters={"company":I["company"],"project":p},fields={"name"})
            [on_basis_company_customer.append(value) for value in company_customer if value not in on_basis_company_customer ]
            cpny_and_locn=frappe.db.get_all("Asset",filters={"company":I["company"],"project":p,              "location":location},fields={"name"})
            [cpny_and_locn1.append(value1) for value1 in cpny_and_locn if value1 not in cpny_and_locn1 ]
    return project_list,getcompany,on_basis_company_customer,cpny_and_locn1

   	
@frappe.whitelist()   	
def get_serialNo(customerId,location):
    bycustomer_location =[]
    bycustomer =[]
    project_list = [p.name for p in frappe.db.get_list("Project", filters={"customer":customerId},fields={"name"})]
    for p in project_list:
        locn_cust=frappe.db.get_all("Asset",filters={"project":p,"location":location},fields={"serial_no"})
        [bycustomer_location.append(I) for I in locn_cust if I not in bycustomer_location]
        ByCustomerFilter= frappe.db.get_all("Asset",filters={"project":p},fields={"serial_no"})
        [bycustomer.append(J) for J  in ByCustomerFilter if J not in bycustomer]
    return bycustomer_location,bycustomer
    
     
     
     
@frappe.whitelist()     
def get_location_serialnoby_asset(asset):
    location_serial=frappe.db.get_value("Asset",{"name":asset},["location","serial_no","asset_name"])
    return location_serial      
     
     
@frappe.whitelist()     
def get_location_assetByseriaNo(serialno):
    location_asset=frappe.db.get_value("Asset",{"serial_no":serialno},["location","name"])
    return location_asset
         
     
     
     
     
 
    	
