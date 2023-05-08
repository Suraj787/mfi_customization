frappe.ui.form.on('Asset Movement', {
    onload:function(frm){
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