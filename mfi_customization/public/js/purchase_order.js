
frappe.ui.form.on('Purchase Order', {
    refresh:function(frm){
        if(frm.doc.docstatus==1 && ["To Receive and Bill","To Receive"].includes(frm.doc.status)) {
			frm.add_custom_button(__('Update Cost'), function() {
				frappe.call({
					method: "mfi_customization.mfi.doctype.cost_center.update_cost",
					args: {
						"doc": frm.doc,
					},
					callback: function(r) {
						frm.reload_doc()
					}
				})
			});
		}
    },
    address:function(frm){
        frm.set_value('address_detail', "");
		if (frm.doc.address!=undefined){
            frappe.call({
                method: "frappe.contacts.doctype.address.address.get_address_display",
                args: {"address_dict": frm.doc.address},
                callback: function(r) {
                    if(r.message) {
                        frm.set_value('address_detail', r.message);
                    }
                }
            });
        }
    }
})