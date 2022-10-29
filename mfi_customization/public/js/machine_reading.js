frappe.ui.form.on('Machine Reading', {
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