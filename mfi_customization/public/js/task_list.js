frappe.listview_settings['Task'] = {
    add_fields: ["mr_status"],
    get_indicator: function(doc) {
        if (doc.mr_status == 'Material Rejected') {
            return [__("Material Rejected"), "red", "status,=,Material Rejected"];
        }
    }
};