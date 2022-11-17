# Copyright (c) 2022, bizmap technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    conditions, filters = get_conditions(filters)
    columns = get_columns(filters)
    data = get_data(conditions, filters)

    return columns, data


def get_data(conditions, filters):

    item = frappe.db.sql("""select mr.name,mr.reading_date,mr.asset,mr.project,mr.machine_type,mr.colour_reading,mr.black_and_white_reading,mr.total,
						mrt.item_code,mrt.item_name,mrt.item_group,mrt.yeild,mrt.total_reading,mrt.percentage_yeild
                        from `tabMachine Reading` mr
                        LEFT Join `tabAsset Item Child Table` mrt on mrt.parent = mr.name
                        where mrt.idx > 0 """)

    return item


def get_conditions(filters):
    conditions = ""
    # if filters.get("mr.name"): conditions += " and mr.name = %(name)s"

    return conditions, filters


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



    ]
