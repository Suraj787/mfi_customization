from __future__ import unicode_literals

import frappe

def get_context(context):
	# do your magic here
	pass
	
	
@frappe.whitelist()
def get_logged_user():
    user = frappe.db.get_value('User',{"name":frappe.session.user},"full_name")
    A=frappe.db.get_all("Customer", filters={"customer_name":user},fields ={"name"})
    return A

    frappe.response["message"] = {
        "success_key":1,
        "message":"Authentication success",
        "sid":frappe.session.sid,
        "api_key":user.api_key,
        "username":user.username,
        "email":user.email
    }
	

@frappe.whitelist()		
def get_location(CustomerID):
    location_list=[]
    project_list = [p.name for p in frappe.db.get_list("Project", filters={"customer":CustomerID},fields={"name"})]
    print("project_list",project_list)
    for p in project_list:
        location =frappe.db.get_list("Asset",{"project":p},"location")
        [location_list.append(Location) for Location in location if Location not in location_list]
    return location_list   
        
	
@frappe.whitelist()		
def get_Customer_name(customer):
    A=frappe.db.get_all("Customer", filters={"name":customer},fields ={"customer_name"})
    Full_Name=A[0]["customer_name"]
    return Full_Name



@frappe.whitelist()
def get_Asset(CustomerID,Location):
    GetCompany=[]
    OnBasisCompanyNcustomer=[]
    Final_OnBasisCompanyNcustomer = []
    cpny_and_locn1=[]
    project_list = [p.name for p in frappe.db.get_list("Project", filters={"customer":CustomerID},fields={"name"})]
    for p in project_list:
        company =frappe.db.get_list("Asset",filters={"project":p},fields={"company"})
        [GetCompany.append(cmpny) for cmpny in company]
        for I in GetCompany:
            company_customer =frappe.db.get_all("Asset",filters={"company":I["company"],"project":p},fields={"name"})
            [OnBasisCompanyNcustomer.append(value) for value in company_customer if value not in OnBasisCompanyNcustomer ]
            cpny_and_locn=frappe.db.get_all("Asset",filters={"company":I["company"],"project":p,              "location":Location},fields={"name"})
            print(cpny_and_locn)
            [cpny_and_locn1.append(value1) for value1 in cpny_and_locn if value1 not in cpny_and_locn1 ]
    return project_list,GetCompany,OnBasisCompanyNcustomer,cpny_and_locn1

   	
@frappe.whitelist()   	
def get_serialNo(CustomerID,Location):
    ByCustomer_Location =[]
    ByCustomer =[]
    project_list = [p.name for p in frappe.db.get_list("Project", filters={"customer":CustomerID},fields={"name"})]
    for p in project_list:
        locn_cust=frappe.db.get_all("Asset",filters={"project":p,"location":Location},fields={"serial_no"})
        [ByCustomer_Location.append(I) for I in locn_cust if I not in ByCustomer_Location]
        ByCustomerFilter= frappe.db.get_all("Asset",filters={"project":p},fields={"serial_no"})
        [ByCustomer.append(J) for J  in ByCustomerFilter if J not in ByCustomer]
    return ByCustomer_Location,ByCustomer
    
     
     
     
@frappe.whitelist()     
def Get_Location_SerialNoBy_Asset(Asset):
    Location_Serial=frappe.db.get_value("Asset",{"name":Asset},["location","serial_no","asset_name"])
    return Location_Serial      
     
     
@frappe.whitelist()     
def Get_Location_AssetBySeriaNo(SerialNo):
    Location_Asset=frappe.db.get_value("Asset",{"serial_no":SerialNo},["location","name"])
    return Location_Asset
         
     
     
     
     
 
    	
