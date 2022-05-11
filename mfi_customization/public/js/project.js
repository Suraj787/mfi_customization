cur_frm.dashboard.add_transactions([
	{
		'items': [
			'Asset',
			'Asset Maintenance',
			'Asset Maintenance Log',
			'Asset Repair',
		],
		'label': 'Others'
	},
	{
		'items': [
			'Asset Delivery Note',
			'Asset Installation Note',
			"Machine Reading"
		],
		'label': 'Asset Delivery'
	},
]);

frappe.ui.form.on('Project', {
	refresh:function(frm){
		// frm.add_custom_button(__('Asset Delivery Note'), function() {
		// 	frappe.model.open_mapped_doc({
		// 		method: "mfi_customization.mfi.doctype.project.make_asset_delivery_note",
		// 		frm: frm
		// 	});
		// },__("Create"));
		frm.add_custom_button(__('Installation'), function() {
			frappe.call({
				method: "mfi_customization.mfi.doctype.project.make_asset_task",
				args: {
					doc: frm.doc
				},
				freeze: true,
				callback: function(r) {
					if(r.message) {
					    frm.remove_custom_button('Installation');
						frappe.msgprint({
							message: __('Task Created: {0}', [r.message.map(function(d) {
								return repl('<a href="/app/task/%(name)s">%(name)s</a>', {name:d})
							}).join(', ')]),
							indicator: 'green'
						})
					}
				}
			});
		},__("Create"));
	},
	setup:function(frm){
		frm.set_query("asset", "machine_readings", function() {
			var asset_list=[]
			cur_frm.doc.asset_list.map((value) => {
				asset_list.push(value.asset)
			})
			return {
				filters: {
					"name": ['in',asset_list]
				}
			}
		});
	},
	maintenance_team(frm){
		if (frm.doc.maintenance_team){
		frm.set_value('maintainance_manager','')
		frm.set_value('manager_name','')
		frm.set_value('maintenance_team_member',[])
		frappe.call({
			method:"mfi_customization.mfi.doctype.project.fetch_asset_maintenance_team",
			args: {
				maintenance_team:frm.doc.maintenance_team
			},
				callback: function (data) {
					frm.set_value('maintainance_manager',data.message.manager)
					frm.set_value('manager_name',data.message.name)
					$.each(data.message.team_members_list || [], function (i, list) {
						var d = frm.add_child("maintenance_team_member");
						d['team_member']=list['member']
						d['maintenance_role']=list['role']
						d['full_name']=list['name']
					})
					cur_frm.refresh_field("maintenance_team_member")
				}
			})
		}
	}
})

// frappe.ui.form.on("Asset Readings", "asset", function(frm, cdt, cdn) {
// 	var d = locals[cdt][cdn];
// 	frappe.db.get_value("Asset", {"name":d.asset},["asset_name"], function(r){
// 		d.asset_name=r.asset_name
// 		refresh_field("machine_readings");
// 	})
// });
