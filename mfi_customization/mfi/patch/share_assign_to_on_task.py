# -*- coding: utf-8 -*-
# Copyright (c) 2020, bizmap technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute():
    # lst = []
    # for i in frappe.get_all("Task",['completed_by','name','assign_date','issue']):
    for tk in  frappe.get_all('Task',['name','completed_by']):
        if len(frappe.get_all('DocShare',{'user':tk.get('completed_by'),"share_doctype": 'Task',"share_name": tk.get('name')})) == 0: 
            docshare = frappe.new_doc("DocShare")
            docshare.update({
                  "user": tk.get('completed_by'),
                  "share_doctype": 'Task',
                  "share_name": tk.get('name'),
                  "read": 1,
                  "write": 1
            })
                
            docshare.save(ignore_permissions=True)
            print(tk.get('name')+" "+tk.get('completed_by')+" "+docshare.get('user'))
    
