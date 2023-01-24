frappe.listview_settings['Issue'] = {
	onload: function (listview) {
		if (frappe.user.has_role("Customer") == 1) {
			$(".list-sidebar").hide();
			$(".overlay-sidebar").hide();
		}
	}
};
