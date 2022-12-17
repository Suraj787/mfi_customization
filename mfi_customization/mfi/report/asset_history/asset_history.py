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
            "label": ("Yield"),
            "fieldname": "mrt.yield",
            "width": 100
        },
        {
            "label": ("Total Reading"),
            "fieldname": "mrt.total_reading",
            "width": 100
        },
        {
            "label": ("Percentage Yield"),
            "fieldname": "mrt.percentage_yield",
            "width": 100
        },



    ]
    
    
    
def prepare_data(filters):
    data=[]
    fltr={}
    #if filters.get('task'):
     #  fltr.update({"task":filters.get("task")})
    #if filters.get('project'):
    #if filters.get('asset'):
    conditions = get_conditions(filters)
    item = frappe.db.sql("""select mr.name,mr.reading_date,mr.asset,mr.project,mr.machine_type,mr.colour_reading,mr.black_and_white_reading,
    mr.total,mrt.item_code,mrt.item_name,mrt.item_group,mrt.total_reading,mrt.percentage_yield,mrt.yield as yld
                        from `tabMachine Reading` mr
                        LEFT Join `tabAsset Item Child Table` mrt on mrt.parent = mr.name
                        where mrt.idx > 0 %s"""%conditions,filters,as_dict=1)
    for i in item:             
        row={}
        row.update(i)

        row.update({"mr.name":i.name,"mr.reading_date":i.reading_date,"mr.asset":i.asset,"mr.project":i.project,
        "mr.machine_type":i.machine_type,"mr.colour_reading":i.colour_reading,
        "mr.black_and_white_reading":i.black_and_white_reading,"mr.total":i.total,"mrt.item_code":i.item_code,
      "mrt.item_name":i.item_name,"mrt.item_group":i.item_group,"mrt.yield":i.yld,
      "mrt.total_reading":i.total_reading,"mrt.percentage_yield":i.percentage_yield})

        data.append(row)


    return data
 
 
 
 
def get_conditions(filters):
    conditions = ""
    if filters.get("asset"): conditions += "and mr.asset = %(asset)s"
    if filters.get("project"): conditions += "and mr.project = %(project)s"
    if filters.get("task"): conditions += "and mr.task = %(task)s"
    return conditions

