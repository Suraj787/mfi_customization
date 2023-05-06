frappe.ui.form.on('Asset Movement', {
    onload:function(frm){
        if(frappe.user.has_role("Customer")==1 || frappe.user.has_role("Technicians")==1 || frappe.user.has_role("Area Technical Manager")==1 && frappe.user!="Administrator"){
            $(".form-control").hide();
            $(".search-icon").hide();
        }
        if(frm.doc.task){
        frm.set_query("asset", "assets", function() {
            
		return {
            query: 'mfi_customization.mfi.doctype.asset_movement.get_asset_filter',

            filters: {
                "task": frm.doc.task 
            }
        }
    });

        
    }}


})