
frappe.ready(function() {


frappe.web_form.after_load = () =>{
	    
frappe.call({

method: 'mfi_customization.mfi.web_form.issues.issues.get_logged_user',
    args: {

    },
    
    callback: function(r) {
        
       frappe.web_form.set_value("customer",r.message[0].name)

        
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
Asset()
SerianNo()
})

frappe.web_form.on('location', () => {
Asset()
SerianNo()
})

frappe.web_form.on('asset', () => {

location()
Get_Location_SerialNoBy_Asset()
})

frappe.web_form.on('serial_no', () => {

location()
Get_Location_AssetBySeriaNo()

})

function location(){
		frappe.call({
    method: 'mfi_customization.mfi.web_form.issues.issues.get_location',
    args: {
        CustomerID:frappe.web_form.get_value("customer")
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

function Asset(){

		frappe.call({
    method: 'mfi_customization.mfi.web_form.issues.issues.get_Asset',
    args: {
        CustomerID:frappe.web_form.get_value("customer"),
        Location:frappe.web_form.get_value("location")
    },
      
    callback: function(r) {
        var options =[]
        console.log(r)
        console.log(r.message[2])
        if (frappe.web_form.get_value("location")==""){
        
                for (const [key,value] of Object.entries(r.message[3])) {
         console.log("k",value.name)
            
         options.push({
         'label':value.name,
         'value':value.name
         
         });
   
   
        }
        
        
        }
        if (frappe.web_form.get_value("location")!=""){
        
               for (const [key,value] of Object.entries(r.message[3])) {
         console.log("k",value.name)
            
         options.push({
         'label':value.name,
         'value':value.name
         
         });
   
   
        }
        
        }
        

     else {
        for (const [key,value] of Object.entries(r.message[2])) {
         console.log("k",value.name)
            
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

function SerianNo(){

		frappe.call({
    method: 'mfi_customization.mfi.web_form.issues.issues.get_serialNo',
    args: {
        CustomerID:frappe.web_form.get_value("customer"),
        Location:frappe.web_form.get_value("location")
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
        
        else{
        
        
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


function Get_Location_SerialNoBy_Asset(){
        frappe.call({
            method: 'mfi_customization.mfi.web_form.issues.issues.Get_Location_SerialNoBy_Asset',
      args: {
        Asset:frappe.web_form.get_value("asset")

        },
       callback: function(r){
        
        
        let   Location1=r.message[0]
        let   Asset1=r.message[1]
        let   AssetName1=r.message[2]
           
        
        
        console.log(r)
        if(frappe.web_form.get_value("asset")!=""){
           frappe.web_form.set_value("location",Location1)
           frappe.web_form.set_value("serial_no",Asset1)
           frappe.web_form.set_value("asset_name",AssetName1)
          console.log("asset trigger")
        
        }
        

        }
        
        
        });



}

function Get_Location_AssetBySeriaNo(){
        frappe.call({
            method: 'mfi_customization.mfi.web_form.issues.issues.Get_Location_AssetBySeriaNo',
      args: {
        SerialNo:frappe.web_form.get_value("serial_no")

        },
       callback: function(r){
        
         let  Location2=r.message[0]
         let  Asset2=r.message[1]
         let   AssetName2=r.message[2]
           
        
        console.log(r)
        if(frappe.web_form.get_value("serial_no")!=""){
        
           frappe.web_form.set_value("location",Location2)
           frappe.web_form.set_value("asset",Asset2)
        }
        
        
        }
        
        
        
        });



}


});









