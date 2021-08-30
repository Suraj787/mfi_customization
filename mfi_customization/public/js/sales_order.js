// cur_frm.remove_custom_button("Delivery Note",'Create');
cur_frm.cscript.custom_refresh = function(doc) {
    cur_frm.remove_custom_button("Delivery Note",'Create');
};
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
                if(flt(frm.doc.per_delivered, 6) < 100 && (order_is_a_sale || order_is_a_custom_sale) && allow_delivery) {
                    frm.add_custom_button(__('Delivery-Note'), () => frm.trigger("make_delivery_note_on_delivery_date"), __('Create'));
                }
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
    }
});