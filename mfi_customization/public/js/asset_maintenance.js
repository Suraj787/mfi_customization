frappe.ui.form.on('Asset Maintenance', {
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

