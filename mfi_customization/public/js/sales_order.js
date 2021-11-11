// cur_frm.remove_custom_button("Delivery Note",'Create');
// cur_frm.cscript.custom_refresh = function(doc) {
//     cur_frm.remove_custom_button("Delivery Note",'Create');
// };
frappe.ui.form.on('Sales Order', {
    refresh:function(frm){
        let allow_delivery = false;
        if(frm.doc.status !== 'Closed') {
            if(frm.doc.status !== 'On Hold') {
                allow_delivery = frm.doc.items.some(item => item.delivered_by_supplier === 0 && item.qty > flt(item.delivered_qty))
						&& !frm.doc.skip_delivery_note

                const order_is_a_sale = ["Sales", "Shopping Cart"].indexOf(frm.doc.order_type) !== -1;
                const order_is_a_custom_sale = ["Sales", "Shopping Cart", "Maintenance"].indexOf(frm.doc.order_type) === -1;
 
                // delivery note
                // if(flt(frm.doc.per_delivered, 6) < 100 && (order_is_a_sale || order_is_a_custom_sale) && allow_delivery) {
                //     frm.add_custom_button(__('Delivery-Note'), () => frm.trigger("make_delivery_note_on_delivery_date"), __('Create'));
                // }
            }
        }
    },

	make_delivery_note_on_delivery_date: function(frm) {
		
		var delivery_dates = [];
		$.each(frm.doc.items || [], function(i, d) {
			if(!delivery_dates.includes(d.delivery_date)) {
				delivery_dates.push(d.delivery_date);
			}
		});

		var item_grid = frm.fields_dict["items"].grid;
		if(!item_grid.get_selected().length && delivery_dates.length > 1) {
			var dialog = new frappe.ui.Dialog({
				title: __("Select Items based on Delivery Date"),
				fields: [{fieldtype: "HTML", fieldname: "dates_html"}]
			});

			var html = $(`
				<div style="border: 1px solid #d1d8dd">
					<div class="list-item list-item--head">
						<div class="list-item__content list-item__content--flex-2">
							${__('Delivery Date')}
						</div>
					</div>
					${delivery_dates.map(date => `
						<div class="list-item">
							<div class="list-item__content list-item__content--flex-2">
								<label>
								<input type="checkbox" data-date="${date}" checked="checked"/>
								${frappe.datetime.str_to_user(date)}
								</label>
							</div>
						</div>
					`).join("")}
				</div>
			`);

			var wrapper = dialog.fields_dict.dates_html.$wrapper;
			wrapper.html(html);

			dialog.set_primary_action(__("Select"), function() {
				var dates = wrapper.find('input[type=checkbox]:checked')
					.map((i, el) => $(el).attr('data-date')).toArray();

				if(!dates) return;

				$.each(dates, function(i, d) {
					$.each(item_grid.grid_rows || [], function(j, row) {
						if(row.doc.delivery_date == d) {
							row.doc.__checked = 1;
						}
					});
				})
				frm.trigger("delivery_note");
				dialog.hide();
			});
			dialog.show();
		} else {
			frm.trigger("delivery_note");
		}
	},
    delivery_note:function(frm){
        var d = new frappe.ui.Dialog({
            fields: [
				{
					"label": "Shipment Type",
					"fieldname": "shipment_type",
					"fieldtype": "Link",
					"options": "Shipment Type"
				}
            ],
            primary_action: function(){
                d.hide();
                frappe.model.open_mapped_doc({
                    method: "mfi_customization.mfi.doctype.sales_order.make_delivery_note",
                    frm: frm,
                    args: {
                    shipment_type: d.get_value('shipment_type')
                    }
                })
            }
        });
        d.show();
    },
	setup:function(frm){
		frm.fields_dict['items'].grid.get_field('ship_to').get_query = function(doc, cdt, cdn) {
            var child = locals[cdt][cdn];
            return {    
				query: 'mfi_customization.mfi.doctype.sales_order.get_customer_by_price_list',
                filters:
					{
						'price_list': child.price_list
					}
                
            }
        }
		frm.fields_dict['items'].grid.get_field('price_list').get_query = function(doc, cdt, cdn) {
            return {    
                filters:
					{
						'company': frm.doc.company
					}
                
            }
        }
	}
});

frappe.ui.form.on('Sales Order Item','price_list',function(frm,cdt,cdn){
	var d = locals[cdt][cdn];
	frappe.db.get_value('Item Price',{'item_code':d.item_code,"price_list":d.price_list},['price_list_rate'],(val) =>{
		d.item_purchase_rate=val.price_list_rate||0
		refresh_field("item_purchase_rate", d.name, d.parentfield);
	})
});

frappe.ui.form.on('Sales Order Item','ship_to',function(frm,cdt,cdn){
	var d = locals[cdt][cdn];
	if (d.ship_to && d.price_list){
		frappe.db.get_doc("Price List", d.price_list).then(( pr ) => {
			(pr.countries).forEach((  pr_row ) => {
				if (pr_row.customer==d.ship_to){
					d.address=pr_row.address
					refresh_field("address", d.name, d.parentfield);
				 }
			})
		});
	}
});

frappe.ui.form.on('Sales Order Item','purchase_detail',function(frm,cdt,cdn){
	var child = locals[cdt][cdn];
	var dialog = new frappe.ui.Dialog({
		title: __("Add Purchase Details"),
		fields: [
			{fieldtype: "Link", fieldname: "price_list", label:"Price List", options:"Price List", default: child.price_list, get_query:function(){
				return {    
					filters:
						{
							'company': frm.doc.company
						}
					
				}},
				onchange:function(){
					var price_list=dialog.get_value("price_list");
					if (price_list && child.item_code){
						frappe.db.get_value('Item Price',{'item_code':child.item_code,"price_list":price_list},['price_list_rate'],(val) =>{
							dialog.set_value("rate",val.price_list_rate||0)
							child.item_purchase_rate=val.price_list_rate||0
							refresh_field("item_purchase_rate", child.name, child.parentfield);
						})
					}
					if (!child.item_code){
						dialog.hide();
						frappe.throw("Please Specify Item First")
					}
				}
			},
			{fieldtype: "Currency", fieldname: "rate", label:"Rate",read_only:1},
			{fieldtype: "Link", fieldname: "ship_to", label:"Ship To", options:"Customer", default: child.ship_to, get_query:function(){
				return {    
					query: 'mfi_customization.mfi.doctype.sales_order.get_customer_by_price_list',
					filters:
						{
							'price_list': dialog.get_value("price_list")
						}
					
				}}
			},
		],
		primary_action: function() {
			child.price_list=dialog.get_value("price_list")
			child.ship_to=dialog.get_value("ship_to")
			dialog.hide();

			if (child.price_list && child.ship_to){
				frappe.db.get_doc("Price List", child.price_list).then(( pr ) => {
					(pr.countries).forEach((  pr_row ) => {
						if (pr_row.customer==child.ship_to){
							child.address=pr_row.address
							refresh_field("address", child.name, child.parentfield);
						 }
					})
				});
			}

			refresh_field("price_list", child.name, child.parentfield);
			refresh_field("ship_to", child.name, child.parentfield);
		},
		primary_action_label: __('Add')
	});
	dialog.show();
});
