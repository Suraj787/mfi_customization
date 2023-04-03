# Copyright (c) 2022, bizmap technologies and contributors
# For license information, please see license.txt

import frappe



def execute(filters=None):
    data = prepare_data(filters)
    columns = get_columns(filters)
    return columns, data

def get_columns(filters):

    return [

        {
            "label": ("Name"),
            "fieldname": "mr.name",
            "fieldtype": "Link",
            "options": "Machine Reading",
            "width": 200
        },
        {
            "label": ("Reading Date"),
            "fieldname": "mr.reading_date",
            "width": 200
        },
        {
            "label": ("Asset"),
            "fieldname": "mr.asset",
            "width": 200
        },
        {
            "label": ("Project"),
            "fieldname": "mr.project",
            "width": 200
        },
        {
            "label": ("Machine Type"),
            "fieldname": "mr.machine_type",
            "width": 200
        },
        {
            "label": ("Colour Reading"),
            "fieldname": "mr.colour_reading",
            "width": 100
        },
        {
            "label": ("Black And White Reading"),
            "fieldname": "mr.black_and_white_reading",
            "width": 100
        },
        {
            "label": ("Total"),
            "fieldname": "mr.total",
            "width": 100
        },
        {
            "label": ("Item Code"),
            "fieldname": "mrt.item_code",
            "width": 150
        },
        {
            "label": ("Item Name"),
            "fieldname": "mrt.item_name",
            "width": 150
        },
        {
            "label": ("Item Group"),
            "fieldname": "mrt.item_group",
            "width": 150
        },
        {
            "label": ("Yeild"),
            "fieldname": "mrt.yeild",
            "width": 100
        },
        {
            "label": ("Total Reading"),
            "fieldname": "mrt.total_reading",
            "width": 100
        },
        {
            "label": ("Percentage Yeild"),
            "fieldname": "mrt.percentage_yeild",
            "width": 100
        },
        {
        "label":("Rated Yeild"),
        "fieldname":"mr.rated_yeild",
        "width":100
        },
        {
        "label":("RatedCoverage%"),
        "fieldname":"mr.ratedcoverage",
        "width":100
        },
        {
        "label":("Actual Yeild"),
        "fieldname":"mr.actual_yeild",
        "width":100
        },
        {
        "label":("Actual Coverage"),
        "fieldname":"mr.actual_coverage",
        "width":100
        },


    ]
    
    
    
def prepare_data(filters):
    data=[]
    fltr={}
    
    conditions = get_conditions(filters)
    item = frappe.db.sql("""select mr.name,mr.task,mr.reading_date,mr.asset,mr.project,mr.machine_type,mr.colour_reading,mr.black_and_white_reading,
    mr.total,mrt.item_code,mrt.item_name,mrt.item_group,mrt.total_reading,mrt.percentage_yeild,mrt.yeild as yld
                        from `tabMachine Reading` mr
                        LEFT Join `tabAsset Item Child Table` mrt on mrt.parent = mr.name
                         where mr.docstatus!=2 %s ORDER BY mr.reading_date DESC"""%conditions,filters,as_dict=1)
                                            
    for i in item:             
        row={}
        row.update(i)
        
        row.update({"mr.name":i.name,"mr.reading_date":i.reading_date,"mr.asset":i.asset,"mr.project":i.project,
        "mr.machine_type":i.machine_type,"mr.colour_reading":i.colour_reading,
        "mr.black_and_white_reading":i.black_and_white_reading,"mr.total":i.total,"mrt.item_code":i.item_code,
      "mrt.item_name":i.item_name,"mrt.item_group":i.item_group,"mrt.yeild":i.yld,
      "mrt.total_reading":i.total_reading,"mrt.percentage_yeild":i.percentage_yeild})

        toner_type=frappe.db.get_value("Task", {"name":i.task},["toner_type"])
        if toner_type:
           rated_yeild=5000
           rated_cvrg=5
           last_rdng_tbl=[i.total for i in frappe.db.get_all('Past Reading',filters={"parent":i.task},fields=["total"])if i.total is not None]
           curnt_rdng_tbl=[i.total for i in frappe.db.get_all('Asset Readings',filters={"parent":i.task},fields=["total"])if i.total is not None]
           if last_rdng_tbl and curnt_rdng_tbl:
              print("ctrrrrrrrrrrr",curnt_rdng_tbl)
              Actual_Yeild=int(curnt_rdng_tbl[0]) - int(last_rdng_tbl[-1])
              if Actual_Yeild:
                 Actual_coverage=rated_yeild/Actual_Yeild*rated_cvrg
                 row.update({"mr.name":i.name,"mr.reading_date":i.reading_date,"mr.asset":i.asset,"mr.project":i.project,
        "mr.machine_type":i.machine_type,"mr.colour_reading":i.colour_reading,
        "mr.black_and_white_reading":i.black_and_white_reading,"mr.total":i.total,"mrt.item_code":i.item_code,
      "mrt.item_name":i.item_name,"mrt.item_group":i.item_group,"mrt.yeild":i.yld,
      "mrt.total_reading":i.total_reading,"mrt.percentage_yeild":i.percentage_yeild,
       "mr.rated_yeild":rated_yeild,"mr.ratedcoverage":rated_cvrg,"mr.actual_yeild":Actual_Yeild,
       "mr.actual_coverage":Actual_coverage})
                     

        data.append(row)
    return data
 
 
 
 
def get_conditions(filters):
    conditions = ""
    if filters.get("asset"): conditions += "and mr.asset = %(asset)s"
    if filters.get("project"): conditions += "and mr.project = %(project)s"
    if filters.get("task"): conditions += "and mr.task = %(task)s"
    return conditions





