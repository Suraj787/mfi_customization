frappe.ui.form.on('Asset', {
	item_code(frm) {
		
		frappe.call({
		    method: "mfi_customization.mfi.doctype.Asset.fetching_child_table",
    args:{
        'name':frm.doc.item_code,
    },
    callback: function(r) {
        
		            for (let i =0; i<r.message.length;i++) {   
		           var childTable = cur_frm.add_child("items")
		           childTable.item_code = r.message[0][i]
		           childTable.item_name = r.message[1][i]
		           childTable.item_group = r.message[2][i]
		           
		           cur_frm.refresh_fields("items")
		            
                           
                       }
        
        
        
    }
		    
		    
		})
		
		
	}
})
