# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "mfi_customization"
app_title = "mfi"
app_publisher = "bizmap technologies"
app_description = "mfi"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "suraj@bizmap.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/mfi_customization/css/mfi_customization.css"
app_include_js = [
	"/assets/js/mfi_customization.min.js",
]
# include js, css files in header of web template
# web_include_css = "/assets/mfi_customization/css/mfi_customization.css"
# web_include_js = "/assets/mfi_customization/js/mfi_customization.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}
email_append_to = ["Job Applicant", "Lead", "Opportunity", "Issue"]

# include js in doctype views
doctype_js = {
				"Project":"public/js/project.js",
                "Issue":"public/js/issue.js",
                "Task":"public/js/task.js",
                "Asset Maintenance":"public/js/asset_maintenance.js",
                "Location":"public/js/location.js",
                "Asset Movement":"public/js/asset_movement.js",
                "Sales Order":"public/js/sales_order.js",
                "Sales Invoice":"public/js/sales_invoice.js",
                "Material Request":"public/js/material_request.js",
                "Item":"public/js/item.js",
                "Quotation":"public/js/quotation.js",
                "Price List":"public/js/price_list.js",
                "Purchase Order":"public/js/purchase_order.js",
                "Landed Cost Voucher":"public/js/landed_cost_voucher.js",
                "Asset":"public/js/asset.js",
                "Machine Reading":"public/js/machine_reading.js"
}	
doctype_list_js = {"Material Request":"public/js/material_request_list.js",
                   "Issue":"public/js/issue_list.js"


                 }
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "mfi_customization.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "mfi_customization.install.before_install"
# after_install = "mfi_customization.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mfi_customization.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Task":{
        "validate":"mfi_customization.mfi.doctype.task.validate",
        "after_insert":"mfi_customization.mfi.doctype.task.after_insert",
        "on_trash":"mfi_customization.mfi.doctype.task.after_delete",
        "on_change":"mfi_customization.mfi.doctype.task.on_change"
        #"before_save":"mfi_customization.mfi.doctype.task.before_save"
    },
    "Asset":{
        "after_insert":"mfi_customization.mfi.doctype.Asset.after_insert",
        "on_cancel":"mfi_customization.mfi.doctype.Asset.on_cancel",
        "on_update":"mfi_customization.mfi.doctype.Asset.on_update"
    },
    "Issue":{
        "validate":"mfi_customization.mfi.doctype.issue.validate",
        "on_change":"mfi_customization.mfi.doctype.issue.on_change"
    },
    "Material Request":{
        #"on_change":"mfi_customization.mfi.doctype.material_request.set_item_from_material_req",
        "on_submit":"mfi_customization.mfi.doctype.material_request.on_submit",
       # "after_save":"mfi_customization.mfi.doctype.material_request.after_save",
        # "onload":"mfi_customization.mfi.doctype.material_request.onload",
        "before_save":"mfi_customization.mfi.doctype.material_request.before_save"
        
        
    },
    # "Machine Reading":{
    #  "validate":"mfi_customization.mfi.doctype.machine_reading.machine_reading.validate"
    # },
    "Comment":{
		"validate":"mfi_customization.mfi.doctype.comment.comment"
	},
    "Communication":{
        "after_insert":"mfi_customization.mfi.doctype.communication.after_insert"
    },
    "File":{
        "after_insert":"mfi_customization.mfi.doctype.communication.after_insert_file"
    },
    # "Item":{
    #     "after_insert":"mfi_customization.mfi.doctype.item.validate"
    # },
    "Quotation":{
        "validate":"mfi_customization.mfi.doctype.quotation.validate"
    },
    "Project":{
        # "validate":"mfi_customization.mfi.doctype.project.validate"
    },
    "Purchase Order":{
        "after_insert":"mfi_customization.mfi.doctype.purchase_order.on_submit"
    },
    "Sales Invoice":{
        "on_submit":"mfi_customization.mfi.doctype.sales_invoice.on_submit",
        "on_cancel":"mfi_customization.mfi.doctype.sales_invoice.on_cancel"
    },
    "Sales Order":{
        "on_submit":"mfi_customization.mfi.doctype.sales_order.on_submit"
    },
    "Machine Reading":{
        "after_save":"mfi_customization.utils.machine_reading.repetitive_call"
    }
    # "Material Request":{
    #     "validate":"mfi_customization.mfi.doctype.material_request.validate",
    #     "after_insert":"mfi_customization.mfi.doctype.material_request.after_insert"
    # }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"mfi_customization.tasks.all"
# 	],
# 	"daily": [
# 		"mfi_customization.tasks.daily"
# 	],
# 	"hourly": [
# 		"mfi_customization.tasks.hourly"
# 	],
# 	"weekly": [
# 		"mfi_customization.tasks.weekly"
# 	]
# 	"monthly": [
# 		"mfi_customization.tasks.monthly"
# 	]

    "cron": {
        "0 9 * * *": [
            "mfi_customization.mfi.doctype.project.make_issues_on_PM_call_interval",
            "mfi_customization.mfi.doctype.Asset.make_task_on_PM_call_interval"
        ]
    }
}

# Testing
# -------
before_migrate=['mfi_customization.mfi.patch.migrate_patch.get_custom_role_permission']
after_migrate = ['mfi_customization.mfi.patch.migrate_patch.set_custom_role_permission']
fixtures = [
    {"dt": "Custom DocPerm", "filters": [
        [
            "parent", "not in", [
                "DocType"
            ]
        ]
    ]},
    {"dt": "Workflow", "filters": [[
      "document_type", "in", ("Issue")
      ]]
    }
    
]
#fixtures=["Custom Field"]

# before_tests = "mfi_customization.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_invoice": "mfi_customization.mfi.doctype.purchase_order.make_purchase_invoice"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "mfi_customization.task.get_dashboard_data"
# }

