
{% include 'erpnext/public/js/controllers/buying.js' %};

frappe.ui.form.on('Material Request', {
    setup:function(frm){
        if(frm.doc.company){
            frm.set_query("assigned_to", function() {
                return {
                    query: "mfi_customization.mfi.doctype.material_request.get_atm_users",
                    filters:{
                        "company":frm.doc.company
                    }
                }
            });
        }
    }
});

// frappe.ui.form.on('Material Request', {
//     schedule_date:function(frm){
//         frm.set_query("item_code", "items", function() {
// 			return {
// 				query: "mfi_customization.mfi.doctype.material_request.item_query",
// 				filters:{
// 					"item_group":["IN",["Consumable","Spares"]]
// 				}
// 			}
// 		});
//     },
    // refresh:function(frm){
       // fetch_data_from_material_request(frm)

    //     if (frm.doc.report_name){
    //         if (frm.doc.__islocal) {
    //             frappe.call({
    //                 method: 'mfi_customization.mfi.doctype.material_request.run',
    //                 type: 'GET',
    //                 args: {
    //                     report_name: frm.doc.report_name,
    //                     filters: frm.doc.filters,
    //                 },
    //                 callback: function(r) {
    //                     frm.events.render_table(frm, r.message);
    //                 } 
    //             });}
    //         else{
    //             frappe.call({
    //                 method: 'mfi_customization.mfi.doctype.material_request.get_requisition_analysis_data',
    //                 args: {
    //                     doc:frm.doc
    //                 },
    //                 callback: function(r) {
    //                     if (r.message){
    //                         frm.events.render_table(frm, r.message['html_format'],r.message['data']);
    //                     }
    //                 } 
    //             });
    //         }
    //     }
    // },
	// onload: function ( frm ) {
 //        frappe.db.get_doc("MFI Settings","MFI Settings").then(( setting ) => {
 //            (setting.company_purchase_warehouse).forEach((  row ) => {
 //                if (row.company==cur_frm.doc.company){
 //                   frm.set_value("set_warehouse",row.warehouse)
 //                 }
 //            })
 //        });
        
               
        
        
        
        // if (frm.doc.docstatus==1) {
            //  frm.add_custom_button(__('Purchase Order'), function () {
            //     get_items_from_MR(frm);
            // }, __("Create"));
        // }

  //       frm.set_query("item_code", "items", function(doc, cdt, cdn) {
		// 	return {
		// 		query: "erpnext.controllers.queries.item_query"
		// 	}
		// });
  //       if (frm.doc.__islocal) {
  //           frm.set_value("material_request_type","Purchase")
  //           frappe.call({
  //               method: "mfi_customization.mfi.doctype.material_request.get_approver",
  //               args: {
  //                   "user": frappe.session.user
  //               },
  //               callback: function(r) {
  //                   frm.set_value('approver',r.message["approver"]);	
  //                   frm.set_value('approver_name',r.message["approver_name"]);				
  //               }
        
  //       });
  //       }
  //       var get_items_from_MR = function(frm) {
  //           var me = this;
  //           let selected_project = '';
  //           const dialog = new frappe.ui.Dialog({
  //               title: __('Get items from MR'),
  //               fields: [
  //                   { fieldtype: 'Section Break'    },
  //                   { fieldtype: 'HTML', fieldname: 'results_area' }
  //               ]
  //           });
  //           var $wrapper;
  //           var $results;
  //           var $placeholder;
  //           dialog.$wrapper.find('.modal-content').css("width", "800px");
  //           $wrapper = dialog.fields_dict.results_area.$wrapper.append(`<div class="results"
  //               style="border: 1px solid #d1d8dd; border-radius: 3px; height: 300px; overflow: auto;"></div>`);
  //           $results = $wrapper.find('.results');
  //           $placeholder = $(`<div class="multiselect-empty-state">
  //                       <span class="text-center" style="margin-top: -40px;">
  //                           <i class="fa fa-2x fa-heartbeat text-extra-muted"></i>
  //                           <p class="text-extra-muted">No items found</p>
  //                       </span>
  //                   </div>`);
  //                   var method = "mfi_customization.mfi.doctype.material_request.get_material_request";
  //                   var columns = (['name', 'schedule_date', 'status']);
  //                   get_material_request_items(frm, true, $results, $placeholder, method, columns);
            
  //           $results.on('click', '.list-item--head :checkbox', (e) => {
  //               $results.find('.list-item-container .list-row-check')
  //                   .prop("checked", ($(e.target).is(':checked')));
  //           });
  //           set_primary_action(frm, dialog, $results, true);
  //           dialog.show();
  //       };

// var set_primary_action= function(frm, dialog, $results) {
//     var me = this;
//     dialog.set_primary_action(__('Create PO'), function() {
//         let checked_values = get_checked_values($results);
//         checked_values.push({name: frm.doc.name, scheduled_date: false, status: frm.doc.status})
//         make_po(checked_values);
//         dialog.hide();
//     });
// };        
    
// var get_material_request_items = function(frm, project_tasks, $results, $placeholder, method, columns) {
//     var me = this;
//     $results.empty();

//     frappe.call({
//         method: method,
//         args:{
//             "current_mr":frm.doc.name
//         },
//         callback: function(data) {
//             if(data.message){
//                 $results.append(make_list_row(columns, project_tasks));
//                 for(let i=0; i<data.message.length; i++){
//                     $results.append(make_list_row(columns, project_tasks, data.message[i]));
//                 }
//             }else {
//                 $results.append($placeholder);
//             }
//         }
//     });
// };

// var make_list_row= function(columns, project_tasks, result={}) {
//             var me = this;
//             // Make a head row by default (if result not passed)
//             let head = Object.keys(result).length === 0;
//             let contents = ``;
//             columns.forEach(function(column) {
//                 contents += `<div class="list-item__content ellipsis">
//                     ${
//                         head ? `<span class="ellipsis">${__(frappe.model.unscrub(column))}</span>`

//                         :(column !== "name" ? `<span class="ellipsis">${__(result[column])}</span>`
//                             : `<a class="list-id ellipsis">
//                                 ${__(result[column])}</a>`)
//                     }
//                 </div>`;
//             })

//             let $row = $(`<div class="list-item">
//                 <div class="list-item__content" style="flex: 0 0 10px;">
//                     <input type="checkbox" class="list-row-check" ${result.checked ? 'checked' : ''}>
//                 </div>
//                 ${contents}
//             </div>`);

//             $row = list_row_data_items(head, $row, result, project_tasks);
//             return $row;
//         };

    // var list_row_data_items = function(head, $row, result, project_tasks) {
    //     if(project_tasks){
    //         head ? $row.addClass('list-item--head')
    //             : $row = $(`<div class="list-item-container"
    //                 data-name = "${result.name}"
    //                 data-scheduled_date = "${result.scheduled_date}"
    //                 data-status = "${result.status}"
    //                 </div>`).append($row);
    //     }
    //     return $row
    // };
    // var get_checked_values= function($results) {
    //     return $results.find('.list-item-container').map(function() {
    //         let checked_values = {};
    //         if ($(this).find('.list-row-check:checkbox:checked').length > 0 ) {
    //             checked_values['name'] = $(this).attr('data-name');
                
    //             if($(this).attr('data-scheduled_date') != 'undefined'){
    //                 checked_values['scheduled_date'] = $(this).attr('data-scheduled_date');
    //             }
    //             else{
    //                 checked_values['scheduled_date'] = false;
    //             }
    //             if($(this).attr('data-status') != 'undefined'){
    //                 checked_values['status'] = $(this).attr('data-status');
    //             }
    //             else{
    //                 checked_values['status'] = false;
    //             }
                
    //             return checked_values;
    //         }
    //     }).get();
    // };

    // var make_po = function(checked_values){
    //     frappe.call({
    //         method: "mfi_customization.mfi.doctype.material_request.make_po",
    //         args:{
    //             checked_values: checked_values
    //         },
    //         callback: function(r) {
    //             if (r.message['status']){
    //                 var msg_content="<h4>Purchase Orders Created</h4>";
    //                 (r.message['po_names']).forEach(function(element) {
    //                     msg_content+=("<br> <b>"+'<a href="/app/purchase-order/'+element+'">' + element + '</a></b>')
    //                 })
    //                 frappe.msgprint("<p>"+`${msg_content}`+"</p>")
    //             }
    //         }
    //     });
    // };

    // },
 //    get_items:function(frm){
 //        Object.keys(cur_frm.doc.items).forEach(d => {
 //            var row=frm.add_child("item_shipment");
 //            row.item=cur_frm.doc.items[d].item_code
 //            row.qty=cur_frm.doc.items[d].qty
 //        });
 //        frm.refresh_field("item_shipment")
 //    },
 //    render_table: function(frm,response,data={}) {
	// 	$(frm.fields_dict.requisition_analysis_html.wrapper).empty();
	// 	frm.events.get_table(frm,response,data);
	// },
 //    get_table: function(frm,response,data) {
	// 	var result_table = $(frappe.render_template('material_request_table', {
	// 		frm: frm,
	// 		columns: response.columns,
 //            result: response.result,
 //            price_list:response.price_list,
 //            item_details:response.item_details,
 //            doc:frm.doc,
 //            data:data
	// 	}));
	// 	result_table.appendTo(frm.fields_dict.requisition_analysis_html.wrapper);
 //    },
    // update_items:function(frm){
    //     frm.set_value('items',[]);
    //     frm.set_value('item_shipment',[]);
    //     let html_values=cur_frm.fields_dict.requisition_analysis_html.wrapper;
    //     frappe.call({
    //         method: 'mfi_customization.mfi.doctype.material_request.run',
    //         type: 'GET',
    //         args: {
    //             report_name: cur_frm.doc.report_name,
    //             filters: cur_frm.doc.filters,
    //         },
    //         callback: function(r) {
    //             var first_approval=false;
    //             var second_approval=false;
    //             if(r.message){
    //                 var qty_field_mapping={"Courier":"courier_qty","AIR":"air_qty","SEA":"sea_qty"};
    //                 var validation=false;
    //                 ((r.message).result).forEach(resp => {
    //                     var item_qty=0;
    //                     var uom="";
    //                     var price_list="";
    //                     var unit_price="";
    //                     var carton_qty="";
    //                     var is_puchase_uom=false;
    //                     $(html_values).find(`[data-item_code="${resp.part_number}"].result-unit_price`).each(function(el, input){
    //                         unit_price=$(input).val();
    //                     })
    //                     $(html_values).find(`[data-item_code="${resp.part_number}"].result-price_list`).each(function(el, input){
    //                         price_list=$(input).val();
    //                     })
    //                     $(html_values).find(`[data-item_code="${resp.part_number}"].result-carton_qty`).each(function(el, input){
    //                         carton_qty=$(input).val();
    //                     })
    //                     $(html_values).find(`[data-item_code="${resp.part_number}"].result-must_buy_in_purchase_uom`).each(function(el, input){
    //                         is_puchase_uom=$(input).is(":checked");
    //                     })
    //                     $(html_values).find(`[data-item_code="${resp.part_number}"].result-uom`).each(function(el, input){
    //                         uom=$(input).val();
    //                     })
    //                     $(html_values).find(`[data-item_code="${resp.part_number}"].result-first_approval`).each(function(el, input){
    //                         if($(input).val() =="Approve"){
    //                             first_approval=true;
    //                         }
    //                     })
    //                     $(html_values).find(`[data-item_code="${resp.part_number}"].result-second_approval`).each(function(el, input){
    //                         if($(input).val() =="Approve"){
    //                             second_approval=true;
    //                         }
    //                     })
    //                     Object.keys(qty_field_mapping).forEach(shipment_type=>{
    //                         $(html_values).find(`[data-item_code="${resp.part_number}"].result-${qty_field_mapping[shipment_type]}`).each(function(el, input){
    //                             if ($(input).val()>0 && (frm.doc.__islocal || (!frm.doc.__islocal && !frm.doc.approval_status && first_approval)|| (!frm.doc.__islocal && frm.doc.approval_status && first_approval && second_approval))){
    //                                 var qty=parseFloat($(input).val());
    //                                 if (is_puchase_uom){
    //                                     qty=(parseFloat($(input).val())/parseFloat(carton_qty));
    //                                     if(parseFloat($(input).val())%parseFloat(carton_qty)!=0){
    //                                         validation=true;
    //                                         frappe.throw(`<b>${resp.part_number}</b> Item ${shipment_type} Qty Must Be Multiple of Carton Qty <b>${carton_qty}</b>`);
    //                                     }
    //                                 }
                                    
    //                                 item_qty+=qty

    //                                 var row=frm.add_child("item_shipment");
    //                                 row.item=resp.part_number
    //                                 row.shipment_type=shipment_type
    //                                 row.qty=qty
    //                                 row.uom=uom;
    //                                 row.price_list=price_list;
                                   
    //                                 frappe.db.get_doc("Price List", price_list).then(( pr ) => {
    //                                     (pr.price_list_supplier).forEach((  pr_row ) => {
    //                                         if (pr_row.company==cur_frm.doc.company){
    //                                             row.supplier=pr_row.supplier
    //                                             frm.refresh_field("item_shipment");
    //                                          }
    //                                     })
    //                                 });
    //                             }
    //                         });
    //                         frm.refresh_field("item_shipment");
    //                     });
                        
    //                     if (item_qty>0){
    //                         if (!validation){
    //                             var item_row=frm.add_child("items");
    //                             item_row.item_code=resp.part_number
    //                             item_row.item_name=resp.part_name
    //                             item_row.qty=item_qty
    //                             item_row.uom=((r.message).item_details)[resp.part_number]['uom']
    //                             item_row.price_list=price_list
    //                             item_row.description=((r.message).item_details)[resp.part_number]['description']
    //                             item_row.conversion_factor=((r.message).item_details)[resp.part_number]['conversion_factor']
    //                             item_row.rate=unit_price
    //                             item_row.warehouse=frm.doc.set_warehouse
    //                         }
    //                         else{
    //                             frm.set_value('items',[]);
    //                             frm.set_value('item_shipment',[]);
    //                         }
                           
    //                     }
    //                 }) 
    //                 frm.refresh_field("items");
    //             }
    //             if (!frm.doc.__islocal&&first_approval){
    //                 frm.set_value("approval_status","First Approved")
    //             }
    //             if (!frm.doc.__islocal&&first_approval&&second_approval){
    //                 frm.set_value("approval_status","Second Approved")
    //             }
    //         } 
    //     });
    // },
    // validate:function(frm){
    //     if (!frm.doc.__islocal) {
    //         frm.trigger("create_requisition_doc")
    //         // frm.trigger("update_title")

    //     }
    // },

    // before_save:function(frm){
        // frm.refresh()
        //frm.refresh_field("items_with_yeild")
       // items_with_yeild(frm)
    
    // },
    
    // after_save:function(frm){
    //     if (cur_frm.doc.report_name && cur_frm.doc.filters){
    //             frappe.call({
    //             method: 'mfi_customization.mfi.doctype.material_request.run',
    //             type: 'GET',
    //             args: {
    //                 report_name: cur_frm.doc.report_name,
    //                 filters: cur_frm.doc.filters,
    //             },
    //             callback: function(r) {
    //                 if(r.message){
    //                     var requisition_items={};
    //                     ((r.message).result).forEach(resp => {
    //                         requisition_items[String(resp.part_number)]={};
    //                         var row={};
    //                         var total_qty=0;
    //                         $(cur_frm.fields_dict.requisition_analysis_html.wrapper).find(`[data-item_code="${resp.part_number}"]`).each(function(el, input){
    //                             row[String((input.className).replace("result-",""))]=$(input).val();
    //                         })
    //                         $(cur_frm.fields_dict.requisition_analysis_html.wrapper).find(`[data-item_code="${resp.part_number}"].result-courier_qty`).each(function(el, input){
    //                             total_qty+=parseFloat($(input).val() || 0);
    //                         })
    //                         $(cur_frm.fields_dict.requisition_analysis_html.wrapper).find(`[data-item_code="${resp.part_number}"].result-air_qty`).each(function(el, input){
    //                             total_qty+=parseFloat($(input).val() || 0);
    //                         })
    //                         $(cur_frm.fields_dict.requisition_analysis_html.wrapper).find(`[data-item_code="${resp.part_number}"].result-sea_qty`).each(function(el, input){
    //                             total_qty+=parseFloat($(input).val() || 0);
    //                         })
    //                         row["total_qty"]=total_qty
    //                         requisition_items[resp.part_number]=row;
    //                     }) 
    //                     frappe.call({
    //                         method: 'mfi_customization.mfi.doctype.material_request.create_requisition_reference',
    //                         args: {
    //                             doc: frm.doc,
    //                             requisition_items: requisition_items,
    //                             table_format:r.message
    //                         },
    //                         callback: function(r) {
    //                             console.log("#############");
    //                         }
    //                     })
    //                     frm.refresh_field("items");
    //                 }
    //             } 
    //         });
    //     }
    // },
//     create_requisition_doc:function(frm){
//         if (cur_frm.doc.report_name && cur_frm.doc.filters){
//             frappe.call({
//                 method: 'mfi_customization.mfi.doctype.material_request.run',
//                 type: 'GET',
//                 args: {
//                     report_name: cur_frm.doc.report_name,
//                     filters: cur_frm.doc.filters,
//                 },
//                 callback: function(r) {
//                     if(r.message){
//                         var requisition_items={};
//                         ((r.message).result).forEach(resp => {
//                             requisition_items[String(resp.part_number)]={};
//                             var row={};
//                             var total_qty=0;
//                             $(cur_frm.fields_dict.requisition_analysis_html.wrapper).find(`[data-item_code="${resp.part_number}"]`).each(function(el, input){
//                                 row[String((input.className).replace("result-",""))]=$(input).val();
//                             })
//                             $(cur_frm.fields_dict.requisition_analysis_html.wrapper).find(`[data-item_code="${resp.part_number}"].result-courier_qty`).each(function(el, input){
//                                 total_qty+=parseFloat($(input).val() || 0);
//                             })
//                             $(cur_frm.fields_dict.requisition_analysis_html.wrapper).find(`[data-item_code="${resp.part_number}"].result-air_qty`).each(function(el, input){
//                                 total_qty+=parseFloat($(input).val() || 0);
//                             })
//                             $(cur_frm.fields_dict.requisition_analysis_html.wrapper).find(`[data-item_code="${resp.part_number}"].result-sea_qty`).each(function(el, input){
//                                 total_qty+=parseFloat($(input).val() || 0);
//                             })
//                             row["total_qty"]=total_qty
//                             requisition_items[resp.part_number]=row;
//                         }) 
//                         frappe.call({
//                             method: 'mfi_customization.mfi.doctype.material_request.create_requisition_reference',
//                             args: {
//                                 doc: frm.doc,
//                                 requisition_items: requisition_items,
//                                 table_format:r.message
//                             },
//                             callback: function(r) {
//                                 console.log("$$$$$$$$$$$$$$$$$$$$$$$$$$$1");
//                             }
//                         })
//                         frm.refresh_field("items");
//                     }
//                 } 
//             });
//         }
//     },
//     update_title:function(frm){
//         frappe.xcall("frappe.model.rename_doc.update_document_title", {
//             doctype: frm.doc.doctype,
//             docname: frm.doc.name,
//             title_field: 'title',
//             old_title: frm.doc['title'],
//             new_title: frm.doc.material_request_name,
//         }).then(function (new_docname) {
//             frm.reload_doc();
//         });
//     }
// });

// frappe.ui.form.on('Material Request Item', {
// 	items_add: function(frm, cdt, cdn){
//         var d = locals[cdt][cdn]
//         if (frm.doc.project){
//             d.project=frm.doc.project
//         }
// 	}
// })



frappe.ui.form.on("Material Request", 'onload_post_render', function(frm,cdt,cdn) {
       cur_frm.fields_dict['items'].grid.get_field('item_code').get_query =
        function() {
        return {

        query: "mfi_customization.mfi.doctype.material_request.item_child_table_filter",
        filters:{
            
            	"asset":frm.doc.asset
             }
          }
       }

    });



 frappe.ui.form.on("Material Request Item",{
       items_add:function(frm){
        cur_frm.fields_dict['items'].grid.get_field('item_code').get_query =
         function() {
         return {

         query: "mfi_customization.mfi.doctype.material_request.item_child_table_filter",
         filters:{
            
             "asset":frm.doc.asset   
               }
            }
         }
       }
   });


frappe.ui.form.on('Material Request', {
    refresh(frm) {
        if (!cur_frm.doc.mr_status) {
            frm.add_custom_button(__('Reject'), function() {
                frappe.call({
                    method: "mfi_customization.mfi.doctype.material_request.material_reject",
                    args: {
                        doc: cur_frm.doc,
                    }
                });
                setTimeout(function() {
                    location.reload(true);
                }, 1000);
            });
        }
    }
});
