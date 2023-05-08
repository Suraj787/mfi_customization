frappe.ui.form.on('Item', {
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