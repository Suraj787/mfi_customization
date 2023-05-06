frappe.ui.form.on('Landed Cost Voucher', {
    onload(frm) {
        if(frappe.user.has_role("Customer")==1 || frappe.user.has_role("Technicians")==1 || frappe.user.has_role("Area Technical Manager")==1 && frappe.user!="Administrator"){
            $(".form-control").hide();
            $(".search-icon").hide();
        }
    },
    setup:function(frm){
        frm.set_query("landed_cost_component_template", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			
		}
		});
        frm.set_query("cost_center","items", function() {
			return {
				filters: {
					"company": frm.doc.company
				}
			
		}
		});
    },
    calculate_cost:function(frm){
        if (frm.doc.distribute_charges_based_on=="Distribute Manually"){
                frappe.call({
                    method: "mfi_customization.mfi.doctype.landed_cost_voucher.calculate_cost",
                    args:{
                        doc:frm.doc
                    },
                    callback: function(r) {
                        if(r.message) {
                            frm.clear_table("items");
                            (r.message['items']).forEach(( item_row ) => {
                                var item=frm.add_child("items")
                                let key_list=["item_code","description","qty","amount","rate","receipt_document_type","receipt_document","applicable_charges","cost_centery"];
                                for (let x in key_list) {
                                    item[key_list[x]]=item_row[key_list[x]]
                                }
                                frm.refresh_field("items");
                            })
                            frm.clear_table("taxes");
                            (r.message['taxes']).forEach(( tax_row ) => {
                                var taxes=frm.add_child("taxes")
                                let key_list=["landed_cost_component","expense_account","base_amount","amount","description"];
                                for (let x in key_list) {
                                    taxes[key_list[x]]=tax_row[key_list[x]]
                                }
                                frm.refresh_field("taxes");
                            })
                        }
                    }
            })
        }
    },
    calculate_customs_value_air:function(frm,amount,tax_row,item_insurance,insurance_not_exists){
        if (tax_row.landed_cost_component=="Customs value air"){
            (frm.doc.items).forEach(( item_row ) => {
                amount+=(item_row.amount+item_insurance[item_row.item_code])
            });
            if (Boolean(insurance_not_exists)){
                frappe.throw(__("<b>Insurance</b> Not Exist For Calculate <b>{0}</b>",[tax_row.landed_cost_component]))
            }
            tax_row.amount=amount
            frm.refresh_field("taxes");
        }
    },
    calculate_freightLocal:function(frm,amount,tax_row,weight_total){
        if (tax_row.landed_cost_component=="FreightLocal"){
            (frm.doc.items).forEach(( item_row ) => {
                frappe.db.get_doc("Item", item_row.item_code).then(( item_master ) => {
                    amount+=((item_master.item_weight/weight_total)*(frm.doc.freight_charges*frm.doc.currency_exchange_rate))
                    tax_row.amount=amount
                    frm.refresh_field("taxes");
                })
            });
            
        }
    },
    get_items_from_purchase_receipts:function(frm){
        frappe.call({
                method: "mfi_customization.mfi.doctype.landed_cost_voucher.get_receipt_shipments",
                args:{
                    doc:frm.doc
                },
                callback: function(r) {
                    if(r.message) {
                        frm.clear_table("shipments_of_landed_cost");
                        frm.clear_table("shipment_parcel");
                        $.each(r.message || [], function(i, d) {
                        var row=frm.add_child("shipments_of_landed_cost")
                        row.shipment=d
                        frappe.db.get_doc("Shipment", d).then(( resp ) => {
                            (resp.shipment_parcel).forEach(( parcel_row ) => {
                                var parcel=frm.add_child("shipment_parcel")
                                parcel.length=parcel_row.length
                                parcel.width=parcel_row.width
                                parcel.height=parcel_row.height
                                parcel.weight=parcel_row.weight
                                parcel.count=parcel_row.count
                            })
                            frm.refresh_field("shipment_parcel")
                        })
                        });
                        frm.refresh_field("shipments_of_landed_cost")
        
                    }
                }
        })
    },
	currency: function (frm) {
		var company_currency;
		if (!frm.doc.company) {
			company_currency = erpnext.get_currency(frappe.defaults.get_default("Company"));
		} else {
			company_currency = erpnext.get_currency(frm.doc.company);
		}
		if (frm.doc.currency) {
			if (company_currency != frm.doc.currency) {
				frappe.call({
					method: "erpnext.setup.utils.get_exchange_rate",
					args: {
						from_currency: frm.doc.currency,
						to_currency: company_currency,
					},
					callback: function (r) {
						frm.set_value("currency_exchange_rate", flt(r.message));
					}
				});
			} else {
				frm.set_value("currency_exchange_rate", 1.0);
			}
		}
	},
    landed_cost_component_template:function(frm){
        if (frm.doc.landed_cost_component_template){
            frm.clear_table("taxes");
            frappe.db.get_doc("Landed Cost Component Template", frm.doc.landed_cost_component_template).then(( resp ) => {
                (resp.landed_cost_component).forEach((  temp_row ) => {
                    var tax=frm.add_child("taxes")
                    tax.landed_cost_component=temp_row.landed_cost_component
                    frappe.db.get_doc("Landed Cost Component", temp_row.landed_cost_component).then(( r ) => {
                        (r.landed_cost_component_account).forEach((  row ) => {
                            if (row.company==frm.doc.company){
                                tax.expense_account=row.account
                                frm.refresh_field("taxes")
                             }
                        })
                    });
                    frm.refresh_field("taxes")
                })
            })
        }
    }
});

frappe.ui.form.on('Landed Cost Taxes and Charges','landed_cost_component',function(frm,cdt,cdn){
	var d = locals[cdt][cdn];
	if (frm.doc.company && d.landed_cost_component){
		frappe.db.get_doc("Landed Cost Component", d.landed_cost_component).then(( resp ) => {
			(resp.landed_cost_component_account).forEach((  row ) => {
				if (row.company==frm.doc.company){
					d.expense_account=row.account
					refresh_field("expense_account", d.name, d.parentfield);
				 }
			})
		});
	}
});