
frappe.ready(function() {


frappe.web_form.after_load = () =>{


     frappe.web_form.set_value("opening_date_time",frappe.datetime.now_datetime())
    
	    
frappe.call({

method: 'mfi_customization.mfi.web_form.issues.issues.get_logged_user',
    args: {

    },
    
    callback: function(r) {
     
       frappe.web_form.set_value("customer",r.message)
 
    }
})            


frappe.web_form.on('customer', () => {
  

		frappe.call({
    method: 'mfi_customization.mfi.web_form.issues.issues.get_Customer_name',
    args: {
        customer:frappe.web_form.get_value("customer")
    },
    async: true,
    callback: function(r) {
      frappe.web_form.set_value("name_of_the_customer",r.message)
        
    }
});

})

frappe.web_form.on('name_of_the_customer', () => {

location()
assetfunction()
serialnno()
})

frappe.web_form.on('location', () => {
assetfunction()
serialnno()
})

frappe.web_form.on('asset', () => {

//location()
get_location_serialnoby_asset()

})

frappe.web_form.on('serial_no', () => {

//location()
get_location_assetByseriaNo()

})

function location(){
		frappe.call({
    method: 'mfi_customization.mfi.web_form.issues.issues.get_location',
    args: {
        customerId:frappe.web_form.get_value("customer")
    },
      
    callback: function(r) {
        var options =[]
        
        for (const [key,value] of Object.entries(r.message)) {
            
         options.push({
         'label':value.location,
         'value':value.location
         
         });
   
   
        }

        var field = frappe.web_form.get_field("location")
         field._data = options;
         field.refresh();
        
    }
});




}

function assetfunction(){

		frappe.call({
    method: 'mfi_customization.mfi.web_form.issues.issues.get_Asset',
    args: {
        customerId:frappe.web_form.get_value("customer"),
        location:frappe.web_form.get_value("location")
    },
      
    callback: function(r) {
        var options =[]
        if (frappe.web_form.get_value("location")==""){
        
                for (const [key,value] of Object.entries(r.message[1])) {
         
            
         options.push({
         'label':value.name,
         'value':value.name
         
         });
   
   
        }
        
        
        }
        if (frappe.web_form.get_value("location")!=""){
        
               for (const [key,value] of Object.entries(r.message[1])) {     
         options.push({
         'label':value.name,
         'value':value.name
         
         });
   
   
        }
        
        }
        

     else {
        for (const [key,value] of Object.entries(r.message[0])) {   
         options.push({
         'label':value.name,
         'value':value.name
         
         });
   
  
        }
        }
        var field = frappe.web_form.get_field("asset")
         field._data = options;
         field.refresh();
        
        
    }
});


}

function serialnno(){

frappe.call({
     method: 'mfi_customization.mfi.web_form.issues.issues.get_serialNo',
     args: {
         customerId:frappe.web_form.get_value("customer"),
         location:frappe.web_form.get_value("location")
        },
  
  callback: function(r) {
      
        var options =[]
     if(frappe.web_form.get_value("location")==""){
           
          for (const [key,value] of Object.entries(r.message[0])) {
          
              options.push({
                'label':value.serial_no,
                 'value':value.serial_no
                 
                  });
             }
   
       }
        
     if(frappe.web_form.get_value("location")!=""){
         for (const [key,value] of Object.entries(r.message[0])) {
            options.push({
               'label':value.serial_no,
               'value':value.serial_no
             });
   
         }
    }
        
    else  {
         for (const [key,value] of Object.entries(r.message[1])) {
           options.push({
              'label':value.serial_no,
              'value':value.serial_no
               });
        }
    }
       
        var field = frappe.web_form.get_field("serial_no")
         field._data = options;
         field.refresh();   
      }
   });

}


function get_location_serialnoby_asset(){
        frappe.call({
            method: 'mfi_customization.mfi.web_form.issues.issues.get_location_serialnoby_asset',
      args: {
        asset:frappe.web_form.get_value("asset")

        },
       callback: function(r){
        
         for (let t of Object.values(r.message)){
   
          if(frappe.web_form.get_value("asset")){
           frappe.web_form.set_value("location",t.location)
           frappe.web_form.set_value("serial_no",t.serial_no)
           frappe.web_form.set_value("asset_name",t.asset_name)
           
             }
         
       }
        
    }
        
 });
}

function get_location_assetByseriaNo(){
        frappe.call({
            method: 'mfi_customization.mfi.web_form.issues.issues.get_location_assetByseriaNo',
      args: {
        serialno:frappe.web_form.get_value("serial_no")

        },
       callback: function(r){
       
       for (let i of Object.values(r.message)){
            if(frappe.web_form.get_value("serial_no")){
        
              frappe.web_form.set_value("location",i.location)
              frappe.web_form.set_value("asset",i.name)
            }
        }
    
     }
  });



 }
 
}

});







