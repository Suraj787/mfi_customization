// Copyright (c) 2021, bizmap technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Machine Reading', {
	setup: function(frm) {
		frm.set_query("asset", function() {
			return {
				filters: {
					"project":frm.doc.project
				}
			};
		});
	},
	
	
		
	
});



frappe.ui.form.on("Machine Reading", 'onload_post_render', function(frm,cdt,cdn) {
       cur_frm.fields_dict['items'].grid.get_field('item_code').get_query =
        function() {
        return {

        query: "mfi_customization.mfi.doctype.material_request.item_child_table_filter",
        filters:{
            
            "asset":frm.doc.asset
       
               }
           }
       }

   });


