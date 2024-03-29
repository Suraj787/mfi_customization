# Copyright (c) 2013, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate

def execute(filters=None):
	data = prepare_data(filters)
	columns = get_columns(filters)

	return columns, data

def get_columns(filters=None):
	return [
	{
	"label": "Issue",
	"fieldtype": "Link",
	"fieldname": "name",
	"options":"Issue",
	'width':120
	},
	{
	"label": "Status",
	"fieldtype": "Data",
	"fieldname": "status",
	'width':80
	},
	{
	"label": "Issue Type",
	"fieldtype": "Link",
	"fieldname": "issue_type",
	"options":"Issue Type",
	'width':110
	},
	{
	"label": "Customer Name",
	"fieldtype": "Data",
	"fieldname": "customer_name",
	'width':170
	},
	{
	"label": "Assigned Technician",
	"fieldtype": "Data",
	"fieldname": "technician",
	'width':170
	},
	{
	"label": "Description",
	"fieldtype": "Data",
	"fieldname": "description",
	'width':110
	},
	{
	"label": "Failure Date",
	"fieldtype": "Data",
	"fieldname": "failure_date_and_time",
	'width':180
	},
	{
	"label": "Opening Date",
	"fieldtype": "Data",
	"fieldname": "opening_date_time",
	'width':180
	},
	{
	"label": "First Responded On",
	"fieldtype": "Data",
	"fieldname": "first_responded_on",
	'width':180
	},
	{
	"label": "Response Time",
	"fieldtype": "Data",
	"fieldname": "response_time",
	'width':150
	},
	{
	"label": "Closing Date",
	"fieldtype": "Data",
	"fieldname": "resolution_date",
	'width':180
	},
	{
	"label": "Time Resolution",
	"fieldtype": "Data",
	"fieldname": "time_resolution",
	'width':150
	},
]

def prepare_data(filters):
	data=[]
	fltr={"type_of_call":"CM"}
	if filters.get("company"):
		fltr.update({"company":filters.get("company")})

	for i in frappe.get_all('Issue',filters=fltr,fields=["name","status","issue_type","description","failure_date_and_time","opening_date_time","first_responded_on","resolution_date","company","closing_date_time","assign_to","name_of_the_customer"]):
		attended_time=frappe.db.get_value("Task",{"issue":i.name,"type_of_call":"CM"},"attended_date_time")
		i.update({"technician":frappe.db.get_value("User",frappe.db.get_value("Task",{"issue":i.name,"type_of_call":"CM"},"completed_by"),"full_name")})
		i.update({"customer_name":i.name_of_the_customer})
		if i.closing_date_time:
			i.update({
						'resolution_date': (i.closing_date_time).strftime("%d/%m/%Y, %I:%M:%S %p")
					})
		if i.opening_date_time :
			company = fltr.get("company") if fltr.get("company") else ( i.get('company') if  i.get('company') else 'MFI MAROC SARL')
			if i.failure_date_and_time:
				i.update({
					'failure_date_and_time': (i.failure_date_and_time).strftime("%d/%m/%Y, %I:%M:%S %p")
				})
			if i.first_responded_on:
				i.update({
					'first_responded_on': (i.first_responded_on).strftime("%d/%m/%Y, %I:%M:%S %p")
				})
			if attended_time:
				response_time = attended_time - i.opening_date_time
				i.update({
					'response_time':get_working_hrs(response_time, i.opening_date_time, attended_time, company)
				})
				if i.closing_date_time:
					time_resolution = i.closing_date_time - attended_time
					i.update({
						'time_resolution':get_working_hrs(time_resolution, attended_time,i.closing_date_time, company),
					})
			i.update({
				'opening_date_time': (i.opening_date_time).strftime("%d/%m/%Y, %I:%M:%S %p")
			})
		data.append(i)
	return data

#calculate response_time_diff in hours with holiday validation 
def get_working_hrs(call_to,opening_date_time, attended_time, company):
	holidays = frappe.db.sql("""select count(distinct holiday_date) from `tabHoliday` h1, `tabHoliday List` h2
	where h1.parent = h2.name and h1.holiday_date between %s and %s
	and h2.company = %s""", (opening_date_time, attended_time, company))[0][0]
	total_hours=0
	if holidays:
		days = call_to.days - holidays
	else:
		days = call_to.days
	hrs = call_to.seconds//3600
	minutes = int(call_to.seconds % 3600 / 60.0)
	daily_hrs_data = frappe.db.get_all("Support Hours", {'parent': 'Support Setting', 'company':company}, ['start_time', 'end_time'])
	if daily_hrs_data:
		daily_hrs = daily_hrs_data[0].get('end_time') - daily_hrs_data[0].get('start_time')  
		daily_hrs = daily_hrs.seconds//3600
		daily_hrs = daily_hrs if daily_hrs else 9
		if days != 0 :
			total_hours = (days * daily_hrs) + hrs
		else:
			total_hours = hrs
	else:
		frappe.msgprint("Please set start time and end time in Support Setting for '{0}'".format(company))
	return ("<b>hours : </b> "+str(total_hours)+ ", <b>min : </b> "+str(minutes))