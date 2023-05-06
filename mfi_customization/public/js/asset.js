frappe.ui.form.on('Asset', {
    onload(frm) {
        if(frappe.user.has_role("Customer")==1 || frappe.user.has_role("Technicians")==1 || frappe.user.has_role("Area Technical Manager")==1 && frappe.user!="Administrator"){
            $(".form-control").hide();
            $(".search-icon").hide();
        }
    },

    item_code(frm) {
        frappe.model.with_doc("Item", frm.doc.item_code, function() {
            var itemschild_data = frappe.model.get_doc("Item", frm.doc.item_code)
            if (itemschild_data.items) {
                frm.clear_table('items');
                $.each(itemschild_data.items,
                    function(index, row) {
                        var d = frm.add_child('items');
                        d.item_code = row.item_code
                        d.item_name = row.item_name
                        d.item_group = row.item_group;
                        frm.refresh_field("items")
                    })

            }

        })

    },

    pm_cycle: function(frm) {
            frappe.call({
                method: 'mfi_customization.mfi.doctype.Asset.date_pm_cycle',
                args: {
                    "project": frm.doc.project,
                    "pm_cycle": frm.doc.pm_cycle

                },
                callback: function(r) {
                    console.log(r)
                    if (frm.doc.pm_cycle == "Monthly") {
                        cur_frm.clear_table("pm_schedule");
                        cur_frm.refresh_fields("pm_schedule")
                        for (let i = 0; i < r.message[0].length; i++) {

                            var childTable = cur_frm.add_child("pm_schedule")
                            childTable.date = r.message[0][i]

                            cur_frm.refresh_fields("pm_schedule")


                        }

                    }

                    if (frm.doc.pm_cycle == "By Monthly") {
                        cur_frm.clear_table("pm_schedule");
                        cur_frm.refresh_fields("pm_schedule")
                        for (let i = 0; i < r.message[4].length; i++) {

                            var childTable = cur_frm.add_child("pm_schedule")
                            childTable.date = r.message[4][i]

                            cur_frm.refresh_fields("pm_schedule")


                        }

                    }


                    if (frm.doc.pm_cycle == "Yearly") {
                        cur_frm.clear_table("pm_schedule");
                        cur_frm.refresh_fields("pm_schedule")
                        for (let i = 0; i < r.message[1].length; i++) {

                            var childTable = cur_frm.add_child("pm_schedule")
                            childTable.date = r.message[1][i]

                            cur_frm.refresh_fields("pm_schedule")


                        }

                    }

                    if (frm.doc.pm_cycle == "Quarterly") {
                        cur_frm.clear_table("pm_schedule");
                        cur_frm.refresh_fields("pm_schedule")
                        for (let i = 0; i < r.message[2].length; i++) {

                            var childTable = cur_frm.add_child("pm_schedule")
                            childTable.date = r.message[2][i]

                            cur_frm.refresh_fields("pm_schedule")


                        }

                    }

                    if (frm.doc.pm_cycle == "Half Yearly") {
                        cur_frm.clear_table("pm_schedule");
                        cur_frm.refresh_fields("pm_schedule")
                        for (let i = 0; i < r.message[3].length; i++) {

                            var childTable = cur_frm.add_child("pm_schedule")
                            childTable.date = r.message[3][i]

                            cur_frm.refresh_fields("pm_schedule")


                        }

                    }

                }
            })
        
    }

})