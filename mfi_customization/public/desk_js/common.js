function hide_search_bar(){
    if (frappe.user != "Administrator"){
        if(frappe.user.has_role("Customer")==1 || frappe.user.has_role("Technicians")==1 || frappe.user.has_role("Area Technical Manager")==1){
            $("#navbar-search.form-control").hide();
            $(".search-icon").hide();
        }
    }
    
}

window.onload = function(){
    hide_search_bar()
}