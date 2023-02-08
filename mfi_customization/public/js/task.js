frappe.ui.form.on('Task', {
	type_of_call: function (frm) {
		if (frm.doc.type_of_call == "Installation") {
			frm.set_df_property('failure_date_and_time', 'reqd', 0);
		} else {
			frm.set_df_property('failure_date_and_time', 'reqd', 1);
		}
	},
	status: function (frm) {
		if (frm.doc.status == "Working") {
			frm.save()
			// set_permissions_for_symptoms(frm);
		}
		transfer_data_to_issue(frm)
		//fetch_data_material_request_item(frm)
		if (frm.doc.status == 'Working') {
			let today = new Date()
			frappe.model.set_value("Issue", frm.doc.issue, 'first_responded_on', today);
		}
		if (frm.doc.status == "Completed") {
			// frm.set_df_property('status','read_only',1);
			if (frm.doc.type_of_call && frappe.user.has_role("Call Coordinator") != 1 && frappe.user == "Administrator") {
				frappe.db.get_value('Type of Call', { 'name': frm.doc.type_of_call }, 'ignore_reading', (r) => {
					if (r.ignore_reading == 1) {
						frm.set_df_property('current_reading', 'hidden', 1);
					} else {
						frm.set_df_property('current_reading', 'hidden', 0);
						frm.set_df_property('current_reading', 'read_only', 1);
					}
				});
			}

			frappe.call({
				method: 'mfi_customization.mfi.doctype.task.set_items_on_machine_reading_from_mr',
				args: {
					'asset': frm.doc.asset,
					'task': frm.doc.name
				},
				callback: function(r) {
				 console.log(r)
				}
			});

		}

	},

	before_save: function (frm) {

	},

	after_save: function (frm) {
		//frm.reload();
	},

	asset: function (frm) {
		if (frm.doc.asset) {
			frappe.db.get_value('Asset', { 'name': frm.doc.asset, 'docstatus': 1 }, ['asset_name', 'location', 'serial_no', 'project'])
				.then(({ message }) => {
					frm.set_value('asset_name', message.asset_name);
					frm.set_value('location', message.location);
					frm.set_value('serial_no', message.serial_no);
					// frm.set_value('project',message.project);
				});
		} else {
			frm.set_value('asset_name', "");
			frm.set_value('serial_no', "");
		}
	},
	serial_no: function (frm) {
		if (frm.doc.serial_no && !frm.doc.asset) {
			frappe.db.get_value('Asset', { 'serial_no': frm.doc.serial_no, 'docstatus': 1 }, ['project'])
				.then(({ message }) => {
					frm.set_value('project', message.project);
				});


			frappe.db.get_value('Asset Serial No', { 'name': frm.doc.serial_no }, ['asset', 'location'])
				.then(({ message }) => {

					if (!frm.doc.asset) {
						frm.set_value('asset', message.asset);
					}

					if (!frm.doc.location) {
						frm.set_value('location', message.location);
					}
				});


		}
		if (!frm.doc.serial_no) {
			frm.set_value('asset', "");
		}
	},
	onload: function (frm) {
		if (frm.doc.status == "Working") {
		set_permissions_for_symptoms(frm);
		}
		// fetch_data_material_request_item(frm)
		/*
   frappe.call({
	 method: "mfi_customization.mfi.doctype.issue.get_logged_user",
	 args: {

	},
	 callback: function(r) {
		frm.set_value("customer",r.message);
		   }
	});
	*/

		if (frm.doc.type_of_call && frappe.user.has_role("Call Coordinator") != 1 && frappe.user == "Administrator") {
			frappe.db.get_value('Type of Call', { 'name': frm.doc.type_of_call }, 'ignore_reading', (r) => {
				if (r.ignore_reading == 1) {
					frm.set_df_property('current_reading', 'hidden', 1);
				} else {
					frm.set_df_property('current_reading', 'hidden', 0);
				}
			});
		}
		if (!frm.doc.asset) {
			frm.set_df_property('asset', "read_only", 0);
			frm.set_df_property('customer', "read_only", 0);
			frm.set_df_property('location', "read_only", 0);
			frm.set_df_property('serial_no', "read_only", 0);
			frm.set_df_property('project', "read_only", 0);
			frm.set_df_property('clear', "hidden", 0);
		}
		if (frm.doc.issue) {
			frm.set_df_property('customer', "read_only", 1);
			// frm.set_df_property('location',"read_only",1);
			frm.set_df_property('project', "read_only", 1);
		}

	},
	refresh: function (frm) {
		set_permissions_for_symptoms(frm);
		permision_fr_call_co_and_tech(frm);
		transfer_data_to_issue(frm)
		read_onl_for_call_codinator_status_complete(frm)
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Material Request'), function () {
				frappe.set_route('List', 'Material Request', { task: frm.doc.name });

			}, __("View"));
		}
		frm.trigger('customer');

		frm.add_custom_button('Material Request', () => {
			var check_machine_reading = frappe.db.get_value("Machine Reading", { 'task': frm.doc.name }, 'name', (r) => {
				if (r.name != null) {
					frappe.model.open_mapped_doc({
						method: "mfi_customization.mfi.doctype.task.make_material_req",
						frm: me.frm
					})

				} else {

					frappe.msgprint("can't create Material Request without Creating Machine Reading")
				}
			})
		}, __('Make'))

		frm.set_query("completed_by", function () {
			return {
				// query: 'mfi_customization.mfi.doctype.task.get_tech',
				query: 'mfi_customization.mfi.doctype.task.get_assign_user',
				filters: {
					"user": frappe.session.user
				}
			};

		});
		let issue = frappe.model.get_doc("Issue", frm.doc.issue);

		if (frm.is_new()) {
			frm.clear_table("current_reading");
			let row = frm.add_child("current_reading");
			frappe.model.set_value(row.doctype, row.name, 'date', frappe.datetime.nowdate());
			frm.refresh_field("current_reading");
			let first_row = frm.doc.current_reading[0];
			frappe.db.get_value('Asset', { 'name': frm.doc.asset }, 'type', (r) => {
				frappe.model.set_value(first_row.doctype, first_row.name, 'type', r.type);
			});
			frm.refresh_field("current_reading");
		}
	},
	setup: function (frm) {
		// frm.set_query("location", function() {
		//     if (frm.doc.customer) {
		//         return {
		//             query: 'mfi_customization.mfi.doctype.task.get_location',
		//             filters: {
		//                 "customer":frm.doc.customer
		//             }
		//         };
		//     }
		// });


		frm.set_query("location", function () {
			return {
				query: 'mfi_customization.mfi.doctype.task.get_locationlist',
				filters: {
					"Customer_Name": frm.doc.customer
				}
			}
		});


		frm.set_query("asset", function () {
			if (frm.doc.customer && frm.doc.location) {
				return {
					query: 'mfi_customization.mfi.doctype.task.get_asset_in_task',
					filters: {
						"location": frm.doc.location,
						"customer": frm.doc.customer
					}
				};
			}
			if (frm.doc.customer && !frm.doc.location) {
				return {
					query: 'mfi_customization.mfi.doctype.task.get_asset_on_cust',
					filters: {
						"customer": frm.doc.customer
					}
				};
			}

		});

		frm.set_query("serial_no", function () {
			if (frm.doc.location && frm.doc.asset) {
				return {
					query: 'mfi_customization.mfi.doctype.task.get_serial_no_list',
					filters: {
						"location": frm.doc.location,
						"asset": frm.doc.asset
					}
				};
			}
			if (frm.doc.customer && !frm.doc.location) {
				return {
					query: 'mfi_customization.mfi.doctype.task.get_asset_serial_on_cust',
					filters: {
						"customer": frm.doc.customer
					}
				};
			}
			if (frm.doc.customer && frm.doc.location) {
				return {
					query: 'mfi_customization.mfi.doctype.task.get_serial_on_cust_loc',
					filters: {
						"location": frm.doc.location,
						"customer": frm.doc.customer
					}
				};

			}

		});
		frm.set_query("asset", "current_reading", function () {
			// if(frm.doc.asset){
			return {
				filters: {
					"name": frm.doc.asset || ""
				}
			}
			// }
			// else{
			//     return {
			//         filters: {
			//             "name": ""
			//         }
			//     }
			// }
		});


	},
	customer: function (frm) {
		if (frm.doc.customer) {
			// frm.set_query('location', 'asset_details_table', function() {
			//     if(frm.doc.customer){return {
			//         query: 'mfi_customization.mfi.doctype.task.get_location',
			//         filters: {
			//             "customer":frm.doc.customer
			//         }
			//     };}
			// });
			frm.set_query('asset', 'asset_details_table', function () {
				if (frm.doc.customer) {
					return {
						query: 'mfi_customization.mfi.doctype.task.get_asset_on_cust',
						filters: {
							"customer": frm.doc.customer
						}
					};
				}
			});
			frm.set_query('serial_no', 'asset_details_table', function () {
				if (frm.doc.customer) {
					return {
						query: 'mfi_customization.mfi.doctype.task.get_asset_serial_on_cust',
						filters: {
							"customer": frm.doc.customer
						}
					};
				}
			});
			// frappe.db.get_value('Project',{'customer':frm.doc.customer},['name'],(val) =>
			// {
			//     frm.set_value('project',val.name);
			// });

		}
	},
	completed_by: function (frm) {
		if (frm.doc.completed_by) {
			frappe.db.get_value('User', { 'name': frm.doc.completed_by }, ['full_name'], (val) => {
				frm.set_value('technician_name', val.full_name);
			});
		}
	},
	validate: function (frm) {

		if (frm.doc.status == 'Completed') {
			frm.set_value("completed_on", frappe.datetime.now_date());
			if (!frm.doc.asset) {
				frappe.throw('Asset details missing.');
			}

		}
		frm.set_df_property('failure_date_and_time', 'read_only', 1);
		// Assigning time on start and on complete
		if (frm.doc.completed_by && frm.doc.assign_date == null) {
			frm.set_value("assign_date", frappe.datetime.now_datetime());

		};
		if (frm.doc.status == 'Working' && frm.doc.attended_date_time == null) {
			frm.set_value("attended_date_time", frappe.datetime.now_datetime());
		};

		if (frm.doc.status == 'Completed' && !frm.doc.completion_date_time) {
			frm.set_value("completion_date_time", frm.doc.modified);
		};
		// Validation for working and completion time
		if (!frm.doc.attended_date_time && frm.doc.status == 'Completed') {
			frm.set_value("completion_date_time", "");
			frappe.throw("Status Cannot be complete before working")
		}



	}
})
cur_frm.dashboard.add_transactions([{
	'items': [
		'Material Request'
	],
	'label': 'Others'
},]);
frappe.ui.form.on("Asset Readings", "type", function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];

	var bl_and_wht = frappe.meta.get_docfield("Asset Readings", "reading", d.name);
	var clr = frappe.meta.get_docfield("Asset Readings", "reading_2", d.name);

	if (d.type == 'Black & White') {
		// bl_and_wht.reqd = 1;
		bl_and_wht.read_only = 0;
		clr.reqd = 0;
		clr.read_only = 1;
		d.set_df_property('reading_2', 'read_only', 1);
		// frm.refresh_fields("current_reading");
		// refresh_field("reading", d.name, d.parentfield);
		// refresh_field("reading_2", d.name, d.parentfield);
	}
	if (d.type == "Colour") {
		bl_and_wht.reqd = 0;
		bl_and_wht.read_only = 1;
		// clr.reqd = 1;
		clr.read_only = 0;
		d.set_df_property('reading', 'read_only', 1);
		// frm.refresh_fields("current_reading");
		// refresh_field("reading", d.name, d.parentfield);
		// refresh_field("reading_2", d.name, d.parentfield);
	}

	d.asset = frm.doc.asset
	frm.set_df_property('asset', 'read_only', 1);
	refresh_field("asset", d.name, d.parentfield);
	refresh_field("reading", d.name, d.parentfield);
	refresh_field("reading_2", d.name, d.parentfield);
});

frappe.ui.form.on("Asset Readings", "date", function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.idx > 1) {
		frappe.throw("More than one row not allowed")
	}
	d.asset = frm.doc.asset
	frm.set_df_property('asset', 'read_only', 1);
	refresh_field("asset", d.name, d.parentfield);
});

frappe.ui.form.on("Asset Details", "location", function (frm, cdt, cdn) {

	var d = locals[cdt][cdn];
	if (d.location) {
		frappe.db.get_value('Asset', { location: d.location, "docstatus": 1 }, ['asset_name', 'name', 'serial_no'], (r) => {
			d.asset = r.name
			d.serial_no = r.serial_no
			d.asset_name = r.asset_name
			refresh_field("asset", d.name, d.parentfield);
			refresh_field("serial_no", d.name, d.parentfield);
			refresh_field("asset_name", d.name, d.parentfield);
		})
	}

});
frappe.ui.form.on("Asset Details", "asset", function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.asset) {
		frappe.db.get_value('Asset', { name: d.asset, "docstatus": 1 }, ['location', 'serial_no'], (r) => {
			d.location = r.location
			d.serial_no = r.serial_no

			refresh_field("location", d.name, d.parentfield);
			refresh_field("serial_no", d.name, d.parentfield);
		})
	}
});
frappe.ui.form.on("Asset Details", "serial_no", function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];

	if (d.serial_no) {
		frappe.db.get_value('Asset', { serial_no: d.serial_no, "docstatus": 1 }, ['location', 'name', 'asset_name'], (r) => {
			d.asset_name = r.asset_name
			d.location = r.location
			d.asset = r.name
			refresh_field("location", d.name, d.parentfield);
			refresh_field("asset", d.name, d.parentfield);
			refresh_field("asset_name", d.name, d.parentfield);
		})
	}
	d.asset = frm.doc.asset
	frm.set_df_property('asset', 'read_only', 1);
	refresh_field("asset", d.name, d.parentfield);
});




function transfer_data_to_issue(frm) {

	if (frm.doc.status == "Completed") {

		frappe.call({
			method: 'mfi_customization.mfi.doctype.task.transfer_data_to_issue',
			args: {
				'doc': frm.doc
			}

		});

	}

}






// function fetch_data_material_request_item(frm){

//     if(frm.doc.status=="Completed"){

//        frappe.call({
//        method: 'mfi_customization.mfi.doctype.task.fetch_data_from_material_request',
//        args: {
//         'task':frm.doc.name,
//         'status':frm.doc.status
//             }

//         });

//      }

//   }


// function insert_items_with_yeild(frm){

//     if(frm.doc.status=="Completed"){

//        frappe.call({
//        method: 'mfi_customization.mfi.doctype.task.items_with_yeild',
//        args: {
//         'task':frm.doc.name,
//         'asset':frm.doc.asset
//             }

//         });

//      }

//   }

// frappe.ui.form.on('Task', {
//     after_save: function(frm) {
//         frappe.call({
//             method: "mfi_customization.utils.machine_reading.repetitive_call",
//             args: {
//                 asset: frm.doc.asset,
//                 project: frm.doc.project,
//                 task: frm.doc.name,
//                 cm: frm.doc.type_of_call
//             }
//         });
//     }
// });

frappe.ui.form.on('Task', {
	refresh(frm) {
		

		frm.add_custom_button(__('Machine Asset History Report'), function () {
			var asset = frm.doc.current_reading.map((i)=>{
				frappe.route_options = {
					"task": frm.doc.name, 
					"project": frm.doc.project, 
					"asset": i.asset
				};
			})
			// frappe.route_options = {
			// 	"task": frm.doc.name, 
			// };
			frappe.set_route(["query-report", "Machine Asset History"]);
		});
		frm.refresh_fields("current_reading");
		refresh_field("current_reading");

		//frm.add_custom_button(__('Machine Asset History Report'), function () {
		//	frappe.set_route(["query-report", "Machine Asset History"]);
		//});

	}
});

frappe.ui.form.on('Task', {
	onload: function (frm) {
		if (frappe.user.name == cur_frm.doc.completed_by && cur_frm.doc.escalation) {
			{
				frm.set_df_property('senior_technician_description', "hidden", 0);
			}
		}
	}
});


function set_permissions_for_symptoms(frm) {
	if (frm.doc.type_of_call == "Toner") {
		if (frappe.user.has_role("Technicians") == 1 && frappe.user != "Administrator") {
			frm.set_df_property('symptoms', "reqd", 0);
			frm.set_df_property('action', "reqd", 0);
			frm.set_df_property('cause', "reqd", 0);
			frm.set_df_property('signature', "reqd", 1);
			frm.set_df_property('symptoms', "read_only", 1);
			frm.set_df_property('action', "read_only", 1);
			frm.set_df_property('cause', "read_only", 1);
		}
	} else {
		if (frappe.user.has_role("Technicians") == 1 && frappe.user != "Administrator" && frm.doc.status == "Working") {
			frm.set_df_property('symptoms', "reqd", 1);
			frm.set_df_property('action', "reqd", 1);
			frm.set_df_property('cause', "reqd", 1);
			frm.set_df_property('signature', "reqd", 1);
			frm.set_df_property('priority', "read_only", 1);
		}
		if (frappe.user.has_role("Technicians") == 1 && frappe.user != "Administrator" && frm.doc.status == "Open") {
			frm.set_df_property('symptoms', "reqd", 0);
			frm.set_df_property('action', "reqd", 0);
			frm.set_df_property('cause', "reqd", 0);
			frm.set_df_property('signature', "reqd", 1);
			frm.set_df_property('priority', "read_only", 1);
		}
		if (frappe.user.has_role("Call Coordinator") == 1 && frappe.user != "Administrator") {
			frm.set_df_property('symptoms', "hidden", 1);
			frm.set_df_property('action', "hidden", 1);
			frm.set_df_property('cause', "hidden", 1);
			frm.set_df_property('signature', "read_only", 1);
			frm.set_df_property('current_reading', 'hidden', 1);
			frm.set_df_property('priority', "read_only", 1);
			frm.set_df_property('repair_items', 'hidden', 1);

		}
	       
	}
}

function read_onl_for_call_codinator_status_complete(frm){
         if (frappe.user.has_role("Call Coordinator")==1 && frm.doc.status == "Completed"){
	            frm.set_df_property('status',"read_only",1);
	          }
}


function permision_fr_call_co_and_tech(frm){
if (frm.doc.type_of_call == "Toner") {
		if (frappe.user.has_role("Technicians")== 1 || frappe.user.has_role("Call Coordinator")==1) {
			frm.set_df_property('symptoms', "hidden", 1);
			frm.set_df_property('action', "hidden", 1);
			frm.set_df_property('cause', "hidden", 1);
			frm.set_df_property('escalation', "hidden", 1);
			frm.set_df_property('repetitive_call',"hidden",1);
		}
	}

}
