// Copyright (c) 2021, bizmap technologies and contributors
// For license information, please see license.txt
frappe.ui.form.on('Machine Reading Tool', {
	refresh:function(frm){
		frm.set_value("project",'')
		frm.disable_save();
		frm.page.clear_indicator();
		frm.set_value("reading_date",frappe.datetime.get_today())
		frm.set_value("reading_type",'Black & White')
	},
	project: function(frm) {
		frm.doc.show_submit = false;
		if(frm.doc.project) {
			frappe.call({
				method: "mfi_customization.mfi.doctype.machine_reading_tool.machine_reading_tool.get_machine_reading",
				args: {
					"project": frm.doc.project,
					"reading_date":frm.doc.reading_date,
					"machine_type":frm.doc.machine_type,
					"reading_type":frm.doc.reading_type,
					
				},
				callback: function(r) {
					if (r.message) {
						frm.events.render_table(frm, r.message);
						for (let value of r.message) {
							if (!value.docstatus) {
								frm.doc.show_submit = true;
								break;
							}
						}
						frm.events.submit_result(frm);
					}
				}
			});
		}
	},
	machine_type:function(frm){
		$(".result-asset").each(function () { 
			document.getElementById("machine_type+"+this.id).value=frm.doc.machine_type;
		})
	},
	reading_type:function(frm){
		$(".result-asset").each(function () { 
			document.getElementById("reading_type+"+this.id).value=frm.doc.reading_type;
		})
	},
	reading_date:function(frm){
		$(".result-asset").each(function () { 
			document.getElementById("reading_date+"+this.id).value=frm.doc.reading_date;
		})
	},
	render_table: function(frm,asset_list) {
		$(frm.fields_dict.reading_items.wrapper).empty();
		frm.events.get_marks(frm,asset_list);
	},

	get_marks: function(frm,asset_list) {
		var result_table = $(frappe.render_template('machine_reading_tool', {
			frm: frm,
			assets: asset_list,
			reading_date:frm.doc.reading_date,
			reading_type:frm.doc.reading_type,
			machine_type:frm.doc.machine_type,
		}));
		result_table.appendTo(frm.fields_dict.reading_items.wrapper);
	},

	submit_result: function(frm) {
		if (frm.doc.show_submit) {
			frm.page.set_primary_action(__("Submit"), function() {
				let result_table=cur_frm.fields_dict.reading_items.wrapper;
				let asset_readings = {};
	
				asset_readings["reading_details"] = {}
				$(".result-asset").each(function () { 
					var row={};

					row["asset"]=this.id;

					$(result_table).find(`[data-asset=${this.id}].result-bw_reading`).each(function(el, input){
						row["black_and_white_reading"] = $(input).val();
					});
					$(result_table).find(`[data-asset=${this.id}].result-colour_reading`).each(function(el, input){
						row["colour_reading"] = $(input).val();
					});
					$(result_table).find(`[data-asset=${this.id}].result-reading_date`).each(function(el, input){
						row["reading_date"] = $(input).val();
					});
					$(result_table).find(`[data-asset=${this.id}].result-machine_type`).each(function(el, input){
						row["machine_type"] = $(input).val();
					});
					$(result_table).find(`[data-asset=${this.id}].result-reading_type`).each(function(el, input){
						row["reading_type"] = $(input).val();
					});
					$(result_table).find(`[data-asset=${this.id}].result-total_reading`).each(function(el, input){
						row["total"] = $(input).val();
					});
					asset_readings["reading_details"][this.id] =row;
				})
				frappe.call({
					method: "mfi_customization.mfi.doctype.machine_reading_tool.machine_reading_tool.create_machine_reading",
					args: {
						"readings": asset_readings,
					},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__("{0} Readings submittted", [r.message]));
						} else {
							frappe.msgprint(__("No Readings to submit"));
						}
						frm.events.project(frm);
					}
				});
			});
		}
		else {
			frm.page.clear_primary_action();
		}
	}
});

