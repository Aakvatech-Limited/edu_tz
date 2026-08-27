import frappe
from erpnext import get_default_currency
from frappe import _


def after_insert(doc, method):
	"""Stamps the Customer on the document so education reuses it instead of raising a second one."""
	doc.customer = create_customer(doc)


def validate(doc, method):
	if not doc.customer and not doc.is_new():
		doc.customer = create_customer(doc)


def get_customer_group() -> str:
	"""Prefers the Student group, since ERPNext only accepts a leaf group on a Customer."""
	default_group = frappe.db.get_single_value("Selling Settings", "customer_group")
	for customer_group in ("Student", default_group):
		if customer_group and frappe.db.get_value("Customer Group", customer_group, "is_group") == 0:
			return customer_group

	frappe.throw(_("Please set a Customer Group that is not a group in Selling Settings"))


def create_customer(doc):
	"""Returns the Student's Customer, creating one only when the Student has none."""
	customer_name = doc.customer or frappe.db.get_value("Customer", {"student": doc.name}, "name")
	if customer_name:
		frappe.db.set_value("Customer", customer_name, "student", doc.name)
		frappe.db.set_value("Student", doc.name, "customer", customer_name)
		return customer_name

	customer = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": doc.student_name,
			"customer_group": get_customer_group(),
			"territory": frappe.db.get_single_value("Selling Settings", "territory"),
			"customer_type": "Individual",
			"default_currency": get_default_currency(),
			"default_price_list": frappe.db.get_single_value("Selling Settings", "selling_price_list"),
			"language": frappe.db.get_single_value("System Settings", "language"),
			"student": doc.name,
		}
	).insert(ignore_permissions=True, ignore_mandatory=True)

	frappe.db.set_value("Student", doc.name, "customer", customer.name)
	frappe.msgprint(_("Customer {0} is created.").format(customer.name), alert=True)
	return customer.name
