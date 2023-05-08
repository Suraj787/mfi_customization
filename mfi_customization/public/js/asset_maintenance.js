frappe.ui.form.on('Asset Maintenance', {
	// onload(frm) {
    //     if(frappe.user.has_role("Customer")==1 || frappe.user.has_role("Technicians")==1 || frappe.user.has_role("Area Technical Manager")==1 && frappe.user!="Administrator"){
    //         $(".form-control").hide();
    //         $(".search-icon").hide();
    //     }
    // },
	setup:function(frm){
		frm.set_query("asset_name", function() {
			if (frm.doc.project) {
				return {
					query: 'mfi_customization.mfi.doctype.issue.get_asset_list',
					filters: {
						"project": frm.doc.project
					}
				};
			}
		});
	},
})

