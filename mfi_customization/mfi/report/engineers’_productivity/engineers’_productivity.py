# Copyright (c) 2023, bizmap technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns  = get_column()
	data	 = get_data(filters)
	return columns, data

def get_column(filters = None):
	return[
		{
			"label":"Technician Name",
			"fieldname":"technician_name",
			"fieldtype":"Data"	

		},
		{
			"label":"No. of Machines",
			"fieldname":"no_of_machines",
			"fieldtype":"Data"
		},
		{
			"label":"No. of Corrective Maintenance Calls(CM)",
			"fieldname":"cm",
			"fieldtype":"Data"
		},
		{
			"label":"No. of Preventive Maintenance Calls(PM)",
			"fieldname":"pm",
			"fieldtype":"Data"
		},
		{
			"label":"No. Of Parts Replacement Calls (MIS)",
			"fieldname":"mis",
			"fieldtype":"Data"
		},
		{
			"label":"No. of Installations (Inst. Calls)",
			"fieldname":"ins",
			"fieldtype":"Data"
		},
		{
			"label":"Average Number of Calls Per Day",
			"fieldname":"avg_per_day",
			"fieldtype":"Data"
		},
		{
			"label":"Average travel time per day",
			"fieldname":"avg_travel_time_per_day",
			"fieldtype":"Data"
		},
		{
			"label":"Average repeat calls in a month",
			"fieldname":"repetitive_call",
			"fieldtype":"Data"
		}
]
def get_data(filters):
	data = []
	fltr = {}
	if filters.get("technician_name"):
		fltr.update({"technician_name":filters.get("technician_name")})
	technician_list =[t['completed_by'] for t in frappe.db.get_list("Task", 'completed_by',distinct=1)]

	for tech in technician_list:
		row = frappe.db.sql("""SELECT t.completed_by, 
		(SELECT technician_name FROM `tabTask` WHERE completed_by='{0}' limit 1) as technician_name,	
		(SELECT COUNT(asset) FROM `tabTask` WHERE completed_by='{0}') as no_of_machines,	
	    (SELECT COUNT(*) FROM `tabTask` WHERE type_of_call='CM' and completed_by='{0}') as cm,
	    (SELECT COUNT(*) FROM `tabTask` WHERE type_of_call='PM' and completed_by='{0}') as pm,
	    (SELECT COUNT(*) FROM `tabTask` WHERE type_of_call ='MIS' and completed_by='{0}') as mis,
	    (SELECT COUNT(*) FROM `tabTask` WHERE type_of_call ='Ins' and completed_by='{0}') as ins,
	    
	    (SELECT AVG(date_count) from (SELECT date(attended_date_time), 
	    COUNT(date(attended_date_time)) as date_count FROM `tabTask`
        where completed_by = '{0}' GROUP BY date(attended_date_time) 
        HAVING COUNT(date(attended_date_time)) > 0) As d) as avg_per_day,

        (SELECT AVG(travel_time) from (SELECT (working_end_time - working_start_time), 
	    count(working_end_time - working_start_time) as travel_time  
        FROM `tabTask` where completed_by = '{0}'           
        and (working_end_time - working_start_time) > 0) as t) as avg_travel_time_per_day,

        (SELECT AVG(rep_call) AS repetitive_call FROM (SELECT attended_date_time,COUNT(name) 
        AS rep_call FROM `tabTask` where completed_by = '{0}' and repetitive_call =1 
        GROUP BY name) AS x ) as repetitive_call

	    FROM (SELECT DISTINCT completed_by FROM `tabTask`) t
	    WHERE completed_by = '{0}'""".format(tech), as_dict=1, debug=1)
		
		data.append(row[0])
	return data
		

