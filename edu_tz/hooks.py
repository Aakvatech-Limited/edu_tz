# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "edu_tz"
app_title = "Edu Tz"
app_publisher = "Aakvatech"
app_description = "edu_tz"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@aakvatech.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/edu_tz/css/edu_tz.css"
# app_include_js = "/assets/edu_tz/js/edu_tz.js"

# include js, css files in header of web template
# web_include_css = "/assets/edu_tz/css/edu_tz.css"
# web_include_js = "/assets/edu_tz/js/edu_tz.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "edu_tz/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "edu_tz.install.before_install"
# after_install = "edu_tz.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "edu_tz.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Student": {
        "after_insert": "edu_tz.edu_tz.api.student.after_insert",
        "validate": "edu_tz.edu_tz.api.student.validate",
    },
    "Payment Entry": {
        "on_submit": "edu_tz.edu_tz.api.payment.on_submit",
    },
    "Sales Invoice": {
        "on_submit": "edu_tz.edu_tz.api.sales_invoice.on_submit",
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"daily": [
		"edu_tz.tasks.daily",
	],
}

# Testing
# -------

# before_tests = "edu_tz.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "edu_tz.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "edu_tz.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype_1}",
        "filter_by": "{filter_by}",
        "redact_fields": ["{field_1}", "{field_2}"],
        "partial": 1,
    },
    {
        "doctype": "{doctype_2}",
        "filter_by": "{filter_by}",
        "partial": 1,
    },
    {
        "doctype": "{doctype_3}",
        "strict": False,
    },
    {"doctype": "{doctype_4}"},
]


fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                (
                    "Customer-student",
                    "Student-customer",
                    "Fees-sales_invoice_income_account",
                    "Fee Structure-sales_invoice_income_account",
                    "Sales Invoice-payment_entry",
                    "Sales Invoice-fees",
                ),
            ]
        ],
    },
    {
        "doctype": "Property Setter",
        "filters": [
            [
                "name",
                "in",
                (
                    "Fee Structure-search_fields",
                    "Fee Structure-title_field",
                    "Fees-letter_head-fetch_from",
                    "Fees-main-track_changes",
                    "Guardian-naming_series-default",
                    "Guardian-students-read_only",
                    "Program Enrollment-enrolled_courses-collapsible",
                    "Program Enrollment-section_break_7-collapsible",
                    "Program Fee-due_date-columns",
                    "Program Fee-student_category-columns",
                    "Program Fee-student_category-fetch_from",
                    "Program-program_fee-allow_bulk_edit",
                ),
            ]
        ],
    },
]