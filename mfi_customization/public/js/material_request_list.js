frappe.listview_settings['Material Request'] = {
	onload: function(listview) {
    const action = () => {
        const selected_docs = listview.get_checked_items();
        const docnames = listview.get_checked_items(true);
        if (selected_docs.length > 0) {
            for (let doc of selected_docs) {
                if (doc.material_request_type!="Purchase") {
                    frappe.throw(__("Cannot create a Purchase Order,Purpose Must Be Purchase <b>"+`${doc.name}`+"</b>"));
                }
            };
        }

        frappe.call({
            method: "mfi_customization.mfi.doctype.material_request.make_po",
            args:{
                checked_values: selected_docs
            },
            callback: function(r) {
                if (r.message['status']){
                    var msg_content="<h4>Purchase Orders Created</h4>";
                    (r.message['po_names']).forEach(function(element) {
                        msg_content+=("<br> <b>"+'<a href="/app/purchase-order/'+element+'">' + element + '</a></b>')
                    })
                    frappe.msgprint("<p>"+`${msg_content}`+"</p>")
                }
            }
        });

    };
    listview.page.add_actions_menu_item(__('Create Purchase Order'), action, false);
    }
};
