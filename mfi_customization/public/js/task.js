frappe.ui.form.on('Task', {
    status:function(frm){
        if(frm.doc.status == 'Working'){
            let today = new Date()
            frappe.model.set_value("Issue", frm.doc.issue, 'first_responded_on',today);
        }
        if (frm.doc.status == "Completed"){
            frm.set_df_property('status','read_only',1);
            frm.set_df_property('current_reading','read_only',1);
        }
        
    },
asset:function(frm){
    if(frm.doc.asset){
    frappe.db.get_value('Asset',{'name':frm.doc.asset,'docstatus':1},['asset_name','location','serial_no','project'])
    .then(({ message }) => {
        frm.set_value('asset_name',message.asset_name);
        frm.set_value('location',message.location);
        frm.set_value('serial_no',message.serial_no);
        frm.set_value('project',message.project);
    });
 
}
},serial_no:function(frm){
    if(frm.doc.serial_no && !frm.doc.asset){
    frm.set_value('asset','');
    frm.set_value('asset_name','');
    frm.set_value('location','');
    frm.set_value('customer','');
    
    frappe.call({
        method: "mfi_customization.mfi.doctype.task.get_customer",
        args: {
            "serial_no":frm.doc.serial_no,
            "asset":frm.doc.asset
        },
        callback: function(r) {
        
                frm.set_value('customer',r.message);				
            }

        
});
        frappe.db.get_value('Asset',{'serial_no':frm.doc.serial_no,'docstatus':1},['project'])
        .then(({ message }) => {
            frm.set_value('project',message.project);
        });
    

    frappe.db.get_value('Asset Serial No',{'name':frm.doc.serial_no},['asset','location'])
    .then(({ message }) => {
        
        if (!frm.doc.asset){
                frm.set_value('asset',message.asset);
            }

        if (!frm.doc.location){
                frm.set_value('location',message.location);
            }
    });                                                                                  
}},
onload:function(frm){
    if(!frm.doc.asset){
        frm.set_df_property('asset',"read_only",0);
        frm.set_df_property('customer',"read_only",0);
        frm.set_df_property('location',"read_only",0);
        frm.set_df_property('serial_no',"read_only",0);
        frm.set_df_property('project',"read_only",0);
        frm.set_df_property('clear',"hidden",0);

        // frm.set_value('project','');
    }

},
clear:function(frm){
    frm.set_value('asset','');
    frm.set_value('location','');
    frm.set_value('serial_no','');
    frm.set_value('customer','');
    
}
,

refresh:function(frm){
    if (!frm.doc.__islocal ){
		frm.add_custom_button(__('Material Request'), function() {
			frappe.set_route('List', 'Material Request', {task: frm.doc.name});
		},__("View"));
    }
    frm.trigger('customer');

    frm.add_custom_button('Material Request', () => {
        frappe.model.open_mapped_doc({
            method: "mfi_customization.mfi.doctype.task.make_material_req",
            frm: me.frm
        })

        }, __('Make'))
    frm.set_query("completed_by", function() {
            return {
                query: 'mfi_customization.mfi.doctype.task.get_tech',
                filters: {
                    "user":frappe.session.user
                }
            };
        
    });
    if (frm.doc.status == "Completed"){
        frm.set_df_property('status','read_only',1);
        frm.set_df_property('current_reading','read_only',1);
    }
       
},

setup:function(frm){
    frm.set_query("location", function() {
        if (frm.doc.customer) {
            return {
                query: 'mfi_customization.mfi.doctype.task.get_location',
                filters: {
                    "customer":frm.doc.customer
                }
            };
        }
    });
    frm.set_query("asset", function() {
        if (frm.doc.customer && frm.doc.location) {
            return {
                query: 'mfi_customization.mfi.doctype.task.get_asset_in_task',
                filters: {
                    "location":frm.doc.location,
                    "customer":frm.doc.customer
                }
            };
        }
        if (frm.doc.customer && !frm.doc.location) {
            return {
                query: 'mfi_customization.mfi.doctype.task.get_asset_on_cust',
                filters: {
                    // "location":frm.doc.location,
                    "customer":frm.doc.customer
                }
            };
        }

    });

		frm.set_query("serial_no", function() {
			if(frm.doc.location && frm.doc.asset){	
			return {
					query: 'mfi_customization.mfi.doctype.task.get_serial_no_list',
					filters: {
						"location":frm.doc.location
						,"asset":frm.doc.asset
					}
				};}
				if (frm.doc.customer && !frm.doc.location) {
					return {
						query: 'mfi_customization.mfi.doctype.task.get_asset_serial_on_cust',
						filters: {
							// "location":frm.doc.location,
							"customer":frm.doc.customer
						}
					};
				}
				if(frm.doc.customer &&  frm.doc.location){
					return {
						query: 'mfi_customization.mfi.doctype.task.get_serial_on_cust_loc',
						filters: {
							"location":frm.doc.location,
							"customer":frm.doc.customer
						}
					};

				}
		});
    frm.set_query("asset", "current_reading", function() {
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
customer:function(frm){
    if(frm.doc.customer){
        frm.set_query('location', 'asset_details_table', function() {
            if(frm.doc.customer){return {
                query: 'mfi_customization.mfi.doctype.task.get_location',
                filters: {
                    "customer":frm.doc.customer
                }
            };}
        });	
        frm.set_query('asset', 'asset_details_table', function() {
            if(frm.doc.customer){return {
                query: 'mfi_customization.mfi.doctype.task.get_asset_on_cust',
                filters: {
                    "customer":frm.doc.customer
                }
            };}
        });
        frm.set_query('serial_no', 'asset_details_table', function() {
            if(frm.doc.customer){return {
                query: 'mfi_customization.mfi.doctype.task.get_asset_serial_on_cust',
                filters: {
                    "customer":frm.doc.customer
                }
            };}
        });
        frappe.db.get_value('Project',{'customer':frm.doc.customer},['name'],(val) =>
        {
            frm.set_value('project',val.name);
        });
        
    }
}
,
completed_by:function(frm){
    if(frm.doc.completed_by){
        frappe.db.get_value('User',{'name':frm.doc.completed_by},['full_name'],(val) =>
			{
				frm.set_value('technician_name',val.full_name);
			});
    }
},
validate:function(frm){
  
    if(frm.doc.status == 'Completed'  ){
        if(!frm.doc.asset){
        frappe.throw('Asset details missing.');
    }
    if(!frm.doc.current_reading.length){
        frappe.throw('Current readings missing.');
    }

}
    frm.set_df_property('failure_date_and_time','read_only',1);
    // Assigning time on start and on complete
    if (frm.doc.completed_by && frm.doc.assign_date == null){
        frm.set_value("assign_date",frappe.datetime.now_datetime());
       
    };
    if (frm.doc.status == 'Working' && frm.doc.attended_date_time == null){
        frm.set_value("attended_date_time", frappe.datetime.now_datetime());
    };
    
    if (frm.doc.status == 'Completed' && !frm.doc.completion_date_time){
        frm.set_value("completion_date_time", frm.doc.modified);
    };
    // Validation for working and completion time
    if(!frm.doc.attended_date_time && frm.doc.status == 'Completed'){
        frm.set_value("completion_date_time","");
        frappe.throw("Status Cannot be complete before working")
    }
    


}
})
cur_frm.dashboard.add_transactions([
	{
		'items': [
			'Material Request'
		],
		'label': 'Others'
	},
]);
frappe.ui.form.on("Asset Readings", "type", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.type=='Black & White'){
	$("div[data-idx='"+d.idx+"']").find("input[data-fieldname='reading_2']").css('pointer-events','none')
    $("div[data-idx='"+d.idx+"']").find("input[data-fieldname='reading']").css('pointer-events','all')
	}
	if (d.type=="Colour"){
        $("div[data-idx='"+d.idx+"']").find("input[data-fieldname='reading_2']").css('pointer-events','all')
		$("div[data-idx='"+d.idx+"']").find("input[data-fieldname='reading']").css('pointer-events','all')
	}
	refresh_field("asset", d.name, d.parentfield);
});
    
frappe.ui.form.on("Asset Readings", "date", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.idx>1){
        frappe.throw("More than one row not allowed")
    }
});

frappe.ui.form.on("Asset Details", "location", function(frm, cdt, cdn) {
    
    var d = locals[cdt][cdn];
    if(d.location){
    frappe.db.get_value('Asset', {location: d.location,"docstatus":1}, ['asset_name','name','serial_no'], (r) => {
        d.asset=r.name
        d.serial_no=r.serial_no
        d.asset_name = r.asset_name
        refresh_field("asset", d.name, d.parentfield);
        refresh_field("serial_no", d.name, d.parentfield);
        refresh_field("asset_name",d.name, d.parentfield);
       })
    }

});
frappe.ui.form.on("Asset Details", "asset", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    if(d.asset){
        frappe.db.get_value('Asset', {name: d.asset,"docstatus":1}, ['location','serial_no'], (r) => {
        d.location=r.location
        d.serial_no=r.serial_no
        
        refresh_field("location", d.name, d.parentfield);
        refresh_field("serial_no", d.name, d.parentfield);
       })
    }
});
frappe.ui.form.on("Asset Details", "serial_no", function(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    
    if(d.serial_no){
    frappe.db.get_value('Asset', {serial_no: d.serial_no,"docstatus":1}, ['location','name','asset_name'], (r) => {  
        d.asset_name=r.asset_name
        d.location=r.location
        d.asset=r.name
        refresh_field("location", d.name, d.parentfield);
        refresh_field("asset", d.name, d.parentfield);
        refresh_field("asset_name", d.name, d.parentfield);
       })
      }
});
