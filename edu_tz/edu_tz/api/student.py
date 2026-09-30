import frappe
from erpnext import get_default_currency
from frappe import _


def after_insert(doc, method):
	if doc.customer:
		return
	frappe.msgprint(_("Inserting customer"), alert=True)
	# set in memory too, so Education's Student.on_update does not create a second Customer
	doc.db_set("customer", create_customer(doc), update_modified=False)


def validate(doc, method):
	for field in ("first_name", "middle_name", "last_name"):
		if doc.get(field):
			doc.set(field, " ".join(doc.get(field).split()))
	doc.student_name = " ".join(filter(None, [doc.first_name, doc.middle_name, doc.last_name]))

	if doc.customer and not frappe.db.exists("Customer", doc.customer):
		doc.customer = frappe.db.get_value("Customer", {"student": doc.name}, "name")

	if not doc.customer and not doc.is_new():
		frappe.msgprint(_("Creating customer on validate"), alert=True)
		doc.customer = create_customer(doc)


def get_student_customer(student):
	"""Return the Student's Customer, falling back to the Customer linked to the Student."""
	customer = frappe.db.get_value("Student", student, "customer")
	if customer and frappe.db.exists("Customer", customer):
		return customer

	linked = frappe.db.get_value("Customer", {"student": student}, "name")
	if linked:
		return linked

	if customer:
		frappe.throw(
			_("Customer {0} set in Student {1} does not exist. Please update the Student record").format(
				customer, student
			)
		)
	frappe.throw(_("Please set Customer in Student record"))


def create_customer(doc):
	customer = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": doc.student_name,
			"customer_group": "Student" or frappe.db.get_single_value("Selling Settings", "customer_group"),
			"territory": frappe.db.get_single_value("Selling Settings", "territory"),
			"customer_type": "Individual",
			"default_currency": get_default_currency(),
			"default_price_list": frappe.db.get_single_value("Selling Settings", "selling_price_list"),
			"language": frappe.db.get_single_value("System Settings", "language"),
			"student": doc.name,
		}
	).insert(ignore_permissions=True, ignore_mandatory=True)

	frappe.msgprint(_("Customer {0} is created.").format(customer.name), alert=True)
	return customer.name
