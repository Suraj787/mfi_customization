frappe.ui.form.on('Item', {
    onload(frm) {
        if(frappe.user.has_role("Customer")==1 || frappe.user.has_role("Technicians")==1 || frappe.user.has_role("Area Technical Manager")==1 && frappe.user!="Administrator"){
            $(".form-control").hide();
            $(".search-icon").hide();
        }
    },
    setup:function(frm){
        frm.set_query("toner","compatible_toner_item", function() {
                return {
                    query: 'mfi_customization.mfi.doctype.item.toner_from_mfi_setting',
                };
        });
        frm.set_query("accessory","compatible_accessories_item", function() {
            return {
                query: 'mfi_customization.mfi.doctype.item.accessory_from_mfi_setting',
            };
    });
    },
})