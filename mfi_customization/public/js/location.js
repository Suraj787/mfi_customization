frappe.ui.form.on('Location', {
    // onload(frm) {
    //     if(frappe.user.has_role("Customer")==1 || frappe.user.has_role("Technicians")==1 || frappe.user.has_role("Area Technical Manager")==1 && frappe.user!="Administrator"){
    //         $(".form-control").hide();
    //         $(".search-icon").hide();
    //     }
    // },
    refresh:function(frm){
        frm.set_query("customer", function() {
          
            if(frm.doc.company){
			return {
                query: 'mfi_customization.mfi.doctype.location.get_customer',
                filters: {
                    "company":frm.doc.company
                }
            };
        }
		});             
        frm.set_query("address", function() {
          
            if(frm.doc.customer){
			return {
                query: 'mfi_customization.mfi.doctype.location.get_address',
                filters: {
                    "customer":frm.doc.customer
                }
            };
        }
		});             
    
    
    },
    customer:function(frm){
        frm.set_query('contact', 'customer_contact_list', function() {
			if(frm.doc.customer){
                return {
				query: 'mfi_customization.mfi.doctype.location.get_contact',
				filters: {
					"customer":frm.doc.customer
				}
			};}
		});
    },
    address:function(frm){
        if(frm.doc.address){
            var addr1 = "" ;
            frappe.db.get_value('Address',{'name':frm.doc.address},['address_line1','address_line2','city'],(val) =>
			{
                if(val.address_line2){
                    frm.set_value('address_detail',val.address_line1+"\n"+val.address_line2+"\n"+val.city);    
                }
                else{
                    frm.set_value('address_detail',val.address_line1+", "+val.city);
                }

				
			});
        }
        else{
            frm.set_value('address_detail',"");
        }
    }
});    
frappe.ui.form.on("Contact List","contact", function(frm, cdt, cdn) {

    var d = locals[cdt][cdn];

    if(d.contact){
        frappe.db.get_value('Contact', {name: d.contact}, ['first_name','last_name'], (r) => {
        d.contact_name=r.first_name +" "+ r.last_name        
        
        refresh_field("contact_name", d.name, d.parentfield);
        
       })
    }
});