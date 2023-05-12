# Copyright (c) 2023, bizmap technologies and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    data = prepare_data(filters)
    columns=get_columns(filters)
    return columns,data
	



def get_columns(filters):
    
    return [
    
         {
            "label": "Project",
            "fieldname": "project",
            "fieldtype": "data",
            "width": 150
         
         },
         {
          
            "label": "Asset",
            "fieldname": "asset",
            "fieldtype": "data",
            "width": 150
         
         },
         {
            "label": "Asset Name",
            "fieldname": "asset_name",
            "fieldtype": "data",
            "width": 150
         
         },
         {
            "label": "Type of spares/toner",
            "fieldname": "tp_of_tnr_spr",
            "fieldtype": "data",
            "width": 150
           
         
         },
         {
            "label": "Item",
            "fieldname": "item",
            "fieldtype": "data",
            "width": 150
           
         
         },
         
         {
         
            "label": "Yeild",
            "fieldname": "yeild",
            "fieldtype": "data",
            "width": 150

         },
         {
            "label": "Replace Reading",
            "fieldname": "replace_reading",
            "fieldtype": "data",
            "width": 150
         
         },
         {
         
            "label": "Current Reading",
            "fieldname": "current_reading",
            "fieldtype": "data",
            "width": 150

         },
         {
         
            "label": "% Yield",
            "fieldname": "perw_yeild",
            "fieldtype": "data",
            "width": 150
         
         
         }
    
    ]	
    
    
    
    
def prepare_data(filters):
    data=[]
    fltr={}
    for i in frappe.get_all('Asset',filters={"docstatus":1},fields=['name','project','asset_name','item_code']):
        project_status= frappe.db.get_value("Project", i.project, "status")
        item = frappe.db.get_value("Item", i.item_code, "item_group")
        item_group =  frappe.db.get_value("Item Group",item, "parent_item_group")
        compatible_spare=[j for j in frappe.db.sql(f"""select item_code,yeild from `tabCompatible Spares Item` where parent='{i.item_code}' and yeild >=80""",as_dict=1)]
        compatible_toner=[l for l in frappe.db.sql(f"""select item_code,yeild from `tabAsset Item Child Table` where parent='{i.item_code}' and yeild >=80""",as_dict=1)]
        toner_spare_itm=compatible_spare + compatible_toner
        if len(toner_spare_itm) !=0 and item_group=="Consumable":
           for t in toner_spare_itm:
               check_Compatiblespare_prnt=frappe.db.get_value("Compatible Spares Item",{"item_code":f'{t.item_code}'},"parent")
               check_Compatibletoner_prnt=frappe.db.get_value("Asset Item Child Table",{"item_code":f'{t.item_code}'},"parent")
               if check_Compatiblespare_prnt or check_Compatibletoner_prnt:
                  rplc_nd_crnt_reading =[i.total for i in  frappe.db.sql(f"""select m.total, m.reading_date from `tabMachine Reading` as m inner join 
`tabAsset Item Child Table` as a on a.parent=m.name where a.item_code ='{t.item_code}' ORDER BY m.name DESC LIMIT 2 """,as_dict=1)if i.total is not None ]
                  row={}
                  row.update({"project":i.project,"asset":i.name,
                      'asset_name':i.asset_name,'tp_of_tnr_spr':t.item_code,'item':check_Compatiblespare_prnt or check_Compatibletoner_prnt,"yeild":t.yeild,"replace_reading":rplc_nd_crnt_reading[1]if len(rplc_nd_crnt_reading)==1 else "null","current_reading":rplc_nd_crnt_reading[0] if len(rplc_nd_crnt_reading)==1 else 'null'})
                  data.append(row) if row not in data else None
                  print(data)
    return data       
        

