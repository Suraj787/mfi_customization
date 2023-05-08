frappe.ui.form.on('Quotation', {
    refresh:function(frm){
        if(frm.doc.asset_quotation_selection){
			let parent = '';
  			(frm.doc.asset_quotation_selection).forEach(i =>{
       		parent = parent+"\n"+i.asset     
   		 })
    		frm.set_df_property('select_item','options', parent); 

		}
        frm.fields_dict['compatible_accessories_list'].grid.add_custom_button('Add Mutiple Accessories', () => {
            frm.trigger("set_accessories_dialog");
        })
        frm.fields_dict['compatible_toner_list'].grid.add_custom_button('Add Mutiple Toner', () => {
            frm.trigger("set_toner_dialog");
        })
    },
    set_accessories_dialog:function(frm){
        frappe.call({
            method: "mfi_customization.mfi.doctype.quotation.get_accessories_items",
            args:{
                "item":frm.doc.select_item,
            },
            callback: function(r) {
                if(r.message) {
                    let table_values = [];
                    $.each(r.message || [], function(i, row) {
                        table_values.push(row)
                    });
                    var d = new frappe.ui.Dialog({
                        'fields': [
                            {fieldname:'accessories_item',label:'Default Accessories Item',fieldtype:'Table',
                                fields: [
                                    {
                                        fieldtype:'Link',
                                        fieldname:'accessory',
                                        label: __('Accessory'),
                                        options:'Item',
                                        in_list_view:1,
                                        onchange: () => {
                                            d.fields_dict.accessories_item.df.data.some(row => { 
                                                frappe.db.get_value('Item',row.accessory, ["item_name"], function(value) {
                                                    row.accessory_name=value['item_name']
                                                    d.fields_dict.accessories_item.refresh();
                                                })
                                               
                                            })
                                            d.fields_dict.accessories_item.refresh();
                                        }
                                    },
                                    {
                                        fieldtype:'Data',
                                        fieldname:'accessory_name',
                                        label: __('Accessory Name'),
                                        in_list_view:1,
                                    }
                                ],
                                data: table_values,
                                in_place_edit: true,
                                get_data: function() {
                                    return table_values;
                                }
                            },
                        ],
                        primary_action: function(){
                            d.hide();
                            (d.get_values()['accessories_item']).forEach(element => {
                                var c = frm.add_child("compatible_accessories_list")
                                c.accessory=element.accessory
                                c.accessory_name=element.accessory_name
                                c.qty=1
                                c.yeild=element.yeild
                                c.compatible_with=frm.doc.select_item
                            })
                            frm.refresh_field("compatible_accessories_list")
                        },
                        primary_action_label: __('Insert')
                    
                    });
                    d.show();
                }
            }
    })
    },
    set_toner_dialog:function(frm){
        frappe.call({
            method: "mfi_customization.mfi.doctype.quotation.get_toner_items",
            args:{
                "item":frm.doc.select_item,
            },
            callback: function(r) {
                if(r.message) {
                    let table_values = [];
                    $.each(r.message || [], function(i, row) {
                        table_values.push(row)
                    });
                    var d = new frappe.ui.Dialog({
                        'fields': [
                            {fieldname:'toner_item',label:'Compatible Toner Item',fieldtype:'Table',
                                fields: [
                                    {
                                        fieldtype:'Link',
                                        fieldname:'toner',
                                        label: __('Toner'),
                                        options:'Item',
                                        in_list_view:1,
                                        onchange: () => {
                                            d.fields_dict.toner_item.df.data.some(row => { 
                                                frappe.db.get_value('Item',row.toner, ["item_name"], function(value) {
                                                    row.toner_name=value['item_name']
                                                    d.fields_dict.toner_item.refresh();
                                                })
                                               
                                            })
                                            d.fields_dict.toner_item.refresh();
                                        }
                                    },
                                    {
                                        fieldtype:'Data',
                                        fieldname:'toner_name',
                                        label: __('Toner Name'),
                                        in_list_view:1,
                                    }
                                ],
                                data: table_values,
                                in_place_edit: true,
                                get_data: function() {
                                    return table_values;
                                }
                            },
                        ],
                        primary_action: function(){
                            d.hide();
                            (d.get_values()['toner_item']).forEach(element => {
                                var c = frm.add_child("compatible_toner_list")
                                c.toner=element.toner
                                c.toner_name=element.toner_name
                                c.qty=1
                                c.yeild=element.yeild
                                c.compatible_with=frm.doc.select_item
                            })
                            frm.refresh_field("compatible_toner_list")
                        },
                        primary_action_label: __('Insert')
                    
                    });
                    d.show();
                }
            }
    })
    },
    generate_contract_calculation:function(frm){
        frm.clear_table("printing_slabs");
        if (frm.doc.mono_volume>0){
            var row1 = frm.add_child("printing_slabs")
            row1.rage_from=0
            row1.range_to=frm.doc.mono_volume
            row1.printer_type="Mono"
            row1.rate=frm.doc.mono_per_click_rate
        }
        if (frm.doc.colour_volume>0){
            var row2 = frm.add_child("printing_slabs")
            row2.rage_from=0
            row2.range_to=frm.doc.colour_volume
            row2.printer_type="Colour"
            row2.rate=frm.doc.colour_per_click_rate
        }
        frm.refresh_field("printing_slabs")  
    }
})

frappe.ui.form.on('Quotation Asset Item','asset',function(frm){
			
        let parent = '';
        (frm.doc.asset_quotation_selection).forEach(i =>{
       		parent = parent+"\n"+i.asset      
   		 })
    	frm.set_df_property('select_item','options', parent); 

		
});