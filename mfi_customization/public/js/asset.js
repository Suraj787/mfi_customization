frappe.ui.form.on('Asset', {

   item_code(frm){
      frappe.model.with_doc("Item",frm.doc.item_code,function(){
       var itemschild_data = frappe.model.get_doc("Item",frm.doc.item_code)
       if(itemschild_data.items){
	  frm.clear_table('items');
	  $.each(itemschild_data.items,
	  function(index,row){
	     var d = frm.add_child('items');
	     d.item_code = row.item_code
	     d.item_name = row.item_name
	     d.item_group = row.item_group;
	     frm.refresh_field("items")
	          })
	   
             }

        })

    }
	
 })



	
