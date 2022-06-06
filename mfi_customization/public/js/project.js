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
	 frm.set_df_property("expected_end_date", "read_only", 1);
		// frm.add_custom_button(__('Asset Delivery Note'), function() {
		// 	frappe.model.open_mapped_doc({
		// 		method: "mfi_customization.mfi.doctype.project.make_asset_delivery_note",
		// 		frm: frm
		// 	});
		// },__("Create"));
		// frm.add_custom_button(__('Installation'), function() {
		// 	frappe.call({
		// 		method: "mfi_customization.mfi.doctype.project.make_asset_task",
		// 		args: {
		// 			doc: frm.doc
		// 		},
		// 		freeze: true,
		// 		callback: function(r) {
		// 			if(r.message) {
		// 			    frm.remove_custom_button('Installation');
		// 				frappe.msgprint({
		// 					message: __('Task Created: {0}', [r.message.map(function(d) {
		// 						return repl('<a href="/app/task/%(name)s">%(name)s</a>', {name:d})
		// 					}).join(', ')]),
		// 					indicator: 'green'
		// 				})
		// 			}
		// 		}
		// 	});
		// },__("Create"));
	},
	
	invoice_cycle:function(frm){
	     
	    if (frm.doc.expected_end_date && frm.doc.invoicing_starts_from){
		    frappe.call({
		    method: 'mfi_customization.mfi.doctype.project.date_invoice_cycle',
		    args: {
		    "expected_end_date":frm.doc.expected_end_date,
		    "invoicing_starts_from":frm.doc.invoicing_starts_from,
		    "invoice_cycle_option":frm.doc.invoice_cycle

		    },
		 callback: function(r) {
		          
		           if(frm.doc.invoice_cycle == "Monthly"){
		           cur_frm.clear_table("invoice_schedule");
		           cur_frm.refresh_fields("invoice_schedule")
		            for (let i =0; i<r.message[0].length;i++) {
             
		           var childTable = cur_frm.add_child("invoice_schedule")
		           childTable.date = r.message[0][i]
		           
		           cur_frm.refresh_fields("invoice_schedule")
		            
                           
                       }
		                 
		    }
		    
		    
		        if(frm.doc.invoice_cycle == "Yearly"){
		           cur_frm.clear_table("invoice_schedule");
		           cur_frm.refresh_fields("invoice_schedule")
		            for (let i =0; i<r.message[1].length;i++) {
             
		           var childTable = cur_frm.add_child("invoice_schedule")
		           childTable.date = r.message[1][i]
		           
		           cur_frm.refresh_fields("invoice_schedule")
		            
                           
                       }
		                 
		    }
		    
		       if(frm.doc.invoice_cycle == "Quarterly"){
		           cur_frm.clear_table("invoice_schedule");
		           cur_frm.refresh_fields("invoice_schedule")
		            for (let i =0; i<r.message[2].length;i++) {
            
		           var childTable = cur_frm.add_child("invoice_schedule")
		           childTable.date = r.message[2][i]
		           
		           cur_frm.refresh_fields("invoice_schedule")
		            
                           
                       }
		                 
		    } 
		    
		      if(frm.doc.invoice_cycle == "Half Yearly"){
		           cur_frm.clear_table("invoice_schedule");
		           cur_frm.refresh_fields("invoice_schedule")
		            for (let i =0; i<r.message[3].length;i++) {
            
		           var childTable = cur_frm.add_child("invoice_schedule")
		           childTable.date = r.message[3][i]
		           
		           cur_frm.refresh_fields("invoice_schedule")
		            
                           
                             }
		                 
		           } 
		    
		       }   
                     })            
                  }
            if(frm.doc.invoicing_starts_from==null){
                 frappe.throw("select Invoicing Starts from")
               }
            if(frm.doc.expected_end_date==null){
                frappe.throw("enter contract period")
                 }   
   },
      
     invoicing_starts_from:function(frm){
       frm.set_value("invoice_cycle","")
       
     },
    
      
     
      contract_period:function(frm){
             frm.set_value("invoice_cycle","")
             if(frm.doc.expected_start_date && frm.doc.contract_period){
             frappe.call({
		    method: 'mfi_customization.mfi.doctype.project.contract_period',
		    args: {
                      "expected_start_date":frm.doc.expected_start_date,
                      "contract_period": frm.doc.contract_period
		    },
		 callback: function(r) {
		           
		           frm.set_value("expected_end_date",r.message)
		           
		          }
		     })
	       }
	       if(frm.doc.contract_period==null){
	        
	       }
	       if(frm.doc.expected_start_date==null){
	         frappe.throw("select Expected Start Date")
	         
	       }
           },
       expected_start_date:function(frm){
         if(frm.doc.expected_start_date && frm.doc.contract_period){
             frappe.call({
		    method: 'mfi_customization.mfi.doctype.project.contract_period',
		    args: {
                      "expected_start_date":frm.doc.expected_start_date,
                      "contract_period": frm.doc.contract_period
		    },
		 callback: function(r) {
		           
		           frm.set_value("expected_end_date",r.message)
		           
		          }
		     })
	       }
	       if(frm.doc.contract_period==null){
	         
	       }
	       if(frm.doc.expected_start_date==null){
	        
	         
	       }
       },    
           
	
	// setup:function(frm){
	// 	frm.set_query("asset", "machine_readings", function() {
	// 		var asset_list=[]
	// 		cur_frm.doc.asset_list.map((value) => {
	// 			asset_list.push(value.asset)
	// 		})
	// 		return {
	// 			filters: {
	// 				"name": ['in',asset_list]
	// 			}
	// 		}
	// 	});
	// }
})	


// 	maintenance_team(frm){
// 		if (frm.doc.maintenance_team){
// 		frm.set_value('maintainance_manager','')
// 		frm.set_value('manager_name','')
// 		frm.set_value('maintenance_team_member',[])
// 		frappe.call({
// 			method:"mfi_customization.mfi.doctype.project.fetch_asset_maintenance_team",
// 			args: {
// 				maintenance_team:frm.doc.maintenance_team
// 			},
// 				callback: function (data) {
// 					frm.set_value('maintainance_manager',data.message.manager)
// 					frm.set_value('manager_name',data.message.name)
// 					$.each(data.message.team_members_list || [], function (i, list) {
// 						var d = frm.add_child("maintenance_team_member");
// 						d['team_member']=list['member']
// 						d['maintenance_role']=list['role']
// 						d['full_name']=list['name']
// 					})
// 					cur_frm.refresh_field("maintenance_team_member")
// 				}
// 			})
// 		}
// 	}


// frappe.ui.form.on("Asset Readings", "asset", function(frm, cdt, cdn) {
// 	var d = locals[cdt][cdn];
// 	frappe.db.get_value("Asset", {"name":d.asset},["asset_name"], function(r){
// 		d.asset_name=r.asset_name
// 		refresh_field("machine_readings");
// 	})
// });
