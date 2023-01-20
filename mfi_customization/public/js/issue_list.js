frappe.listview_settings['Issue'] = {
    onload: function (listview) {
      if(frappe.user.has_role("Customer")==1){
		$(".list-sidebar").hide();
		$(".overlay-sidebar").hide();
	
    }
}
};

frappe.listview_settings['Issue'] = {
  add_fields: ["mr_status"],
  get_indicator: function(doc) {
      if (doc.mr_status == 'Material Rejected') {
          return [__("Material Rejected"), "red", "status,=,Material Rejected"];
      }
  }
};
