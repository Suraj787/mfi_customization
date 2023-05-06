frappe.ui.form.on('Machine Reading', {
    onload(frm) {
        if(frappe.user.has_role("Customer")==1 || frappe.user.has_role("Technicians")==1 || frappe.user.has_role("Area Technical Manager")==1 && frappe.user!="Administrator"){
            $(".form-control").hide();
            $(".search-icon").hide();
        }
    },
    after_save: function(frm) {
        frappe.call({
            method: "mfi_customization.utils.machine_reading.repetitive_call",
            args: {
                asset: frm.doc.asset,
                project: frm.doc.project,
                task: frm.doc.task,
            }
        });
    }
});