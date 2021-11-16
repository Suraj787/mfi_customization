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
	}
});
