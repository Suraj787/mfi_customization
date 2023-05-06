frappe.ui.form.on('Sales Invoice', {
    onload(frm) {
        if(frappe.user.has_role("Customer")==1 || frappe.user.has_role("Technicians")==1 || frappe.user.has_role("Area Technical Manager")==1 && frappe.user!="Administrator"){
            $(".form-control").hide();
            $(".search-icon").hide();
        }
    },
	get_assets:function(frm){
        if (frm.doc.project){
                frappe.call({
                    method: "mfi_customization.mfi.doctype.sales_invoice.get_assets",
                    args: {
                        "project": frm.doc.project,
                        "company":frm.doc.company
                    },
                    callback: function(r) {
                       if (r.message){
                            frm.clear_table("assets_rates_item");
                            var total_mono=0;
                            var total_colour=0;
                            var per_click_mono=0;
                            var per_click_colour=0;
                            var total_rate=0;
                            var asset_non_zero_values=0;
                            $.each(r.message[0] || [], function(i, d) {
                                var row=frm.add_child("assets_rates_item")
                                row.asset=d.asset
                                row.asset_name=d.asset_name
                                row.serial_no=d.serial_no
                                row.colour_click_rate=d.colour_click_rate
                                row.mono_click_rate=d.mono_click_rate
                                row.total_mono_reading=d.total_mono_reading
                                row.total_colour_reading=d.total_colour_reading
                                row.mono_current_reading=d.mono_current_reading
                                row.mono_last_reading=d.mono_last_reading
                                row.colour_current_reading=d.colour_current_reading
                                row.colour_last_reading=d.colour_last_reading
                                row.total_rate=d.total_rate
                                row.total_mono_billing=d.total_mono_billing
                                row.total_colour_billing=d.total_colour_billing,
                                row.machine_reading_current=d.machine_reading_current
                                row.machine_reading_last=d.machine_reading_last
                                total_mono+=d.total_mono_reading
                                total_colour+=d.total_colour_reading
                                per_click_mono=d.mono_click_rate
                                per_click_colour=d.colour_click_rate
                                total_rate+=d.total_rate
                                if (d.total_mono_reading>0 || d.total_colour_reading>0){
                                    asset_non_zero_values+=1
                                }
                            });
                            $.each(r.message[1] || [], function(i, d) {
                                var row=frm.add_child("items")
                                Object.keys(d).forEach(fieldname => {
                                    row[fieldname]=d[fieldname]
                                });
                            })

                            $.each(r.message[2] || [], function(i, d) {
                                var row=frm.add_child("printing_slabs")
                                row.rage_from=d.range_from
                                row.range_to=d.range_to
                                row.printer_type=d.printer_type
                                row.no_of_copies=parseFloat(d.range_to)-parseFloat(d.range_from)
                                row.rate=d.rate
                                row.total_amount=parseFloat(row.no_of_copies)*d.rate
                            });
                            frm.set_value("total_billable_assets",asset_non_zero_values);
                            frm.set_value("total_contract_assets",(r.message[0]).length);
                            frm.set_value("total_mono_reading",total_mono);
                            frm.set_value("total_color_reading",total_colour);
                            frm.set_value("mono_click_rate",per_click_mono);
                            frm.set_value("colour_click_rate",per_click_colour);
                            frm.set_value("total_rent",r.message[3]);
                            frm.refresh_field("assets_rates_item")
                            frm.refresh_field("printing_slabs")
                            frm.refresh_field("items")
                       }
                    }
            
                });
        }

	}
})

frappe.ui.form.on('Assets Rates Item','mono_click_rate',function(frm,cdt,cdn){
    var d = locals[cdt][cdn];
    d.total_mono_reading=(parseFloat(d.mono_current_reading)- parseFloat(d.mono_last_reading))*parseFloat(d.mono_click_rate)
    d.total_rate=parseFloat(d.total_mono_reading)+parseFloat(d.total_colour_reading)
    refresh_field("total_rate", d.name, d.parentfield);
    refresh_field("total_mono_reading", d.name, d.parentfield);
    var total_mono=0;
    var total_colour=0;
    var per_click_mono=0;
    var per_click_colour=0;
    $.each(frm.doc.assets_rates_item || [], function(i, d) {
        total_mono+=d.total_mono_reading
        total_colour+=d.total_colour_reading
        per_click_mono=d.mono_click_rate
        per_click_colour=d.colour_click_rate
    })
    frm.set_value("total_mono_reading",total_mono);
    frm.set_value("total_color_reading",total_colour);
    frm.set_value("mono_click_rate",per_click_mono);
    frm.set_value("colour_click_rate",per_click_colour);
});
frappe.ui.form.on('Assets Rates Item','colour_click_rate',function(frm,cdt,cdn){
    var d = locals[cdt][cdn];
    d.total_colour_reading=(parseFloat(d.colour_current_reading)- parseFloat(d.colour_last_reading))*parseFloat(d.colour_click_rate)
    d.total_rate=parseFloat(d.total_mono_reading)+parseFloat(d.total_colour_reading)
    refresh_field("total_rate", d.name, d.parentfield);
    refresh_field("total_colour_reading", d.name, d.parentfield);
    var total_mono=0;
    var total_colour=0;
    var per_click_mono=0;
    var per_click_colour=0;
    $.each(frm.doc.assets_rates_item || [], function(i, d) {
        total_mono+=d.total_mono_reading
        total_colour+=d.total_colour_reading
        per_click_mono=d.mono_click_rate
        per_click_colour=d.colour_click_rate
    })
    frm.set_value("total_mono_reading",total_mono);
    frm.set_value("total_color_reading",total_colour);
    frm.set_value("mono_click_rate",per_click_mono);
    frm.set_value("colour_click_rate",per_click_colour);
});