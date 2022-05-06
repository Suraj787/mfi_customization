// Copyright (c) 2016, bizmap technologies and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Issue Status"] = {
	"filters": [
	    {
			"label":"Company",
			"fieldname":"company",
			"fieldtype":"Link",
			"options":"Company"	
		},
		
		{
		
		
			"label":"Customer",
			"fieldname":"customer",
			"fieldtype":"Link",
		    	"options":"Customer",
		    	"default":CustomerDefault()
		    	
		    
		
		}
		
	]
	
	
	
	
};



function CustomerDefault(){

    var value =[]

 A = frappe.db.get_value("Customer",{"customer_name":frappe.user_info().fullname},["name"])
 .then(({ message }) => {
         value.push(message.name)
        
})
    
    return value
}

