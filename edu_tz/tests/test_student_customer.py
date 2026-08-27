"""Covers the Customer raised for every Student."""

import frappe
from frappe.tests import IntegrationTestCase

from edu_tz.edu_tz.api.student import create_customer, get_customer_group
from edu_tz.tests.utils import make_student


class TestStudentCustomer(IntegrationTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_customer_group_is_never_a_group_node(self):
		student = make_student()

		customer_group = frappe.db.get_value("Customer", {"student": student.name}, "customer_group")
		self.assertEqual(frappe.db.get_value("Customer Group", customer_group, "is_group"), 0)

	def test_student_group_is_preferred(self):
		self.assertEqual(get_customer_group(), "Student")

	def test_selling_settings_default_is_used_when_student_is_a_group(self):
		frappe.db.set_value("Customer Group", "Student", "is_group", 1)
		frappe.db.set_single_value("Selling Settings", "customer_group", "Individual")

		self.assertEqual(get_customer_group(), "Individual")

	def test_one_customer_per_student(self):
		before = frappe.db.count("Customer")

		student = make_student()

		self.assertEqual(frappe.db.count("Customer"), before + 1)
		self.assertEqual(
			frappe.get_all("Customer", filters={"student": student.name}, pluck="name"),
			[frappe.db.get_value("Student", student.name, "customer")],
		)

	def test_the_linked_customer_carries_the_student_back_link(self):
		student = make_student()

		customer = frappe.db.get_value("Student", student.name, "customer")
		self.assertEqual(frappe.db.get_value("Customer", customer, "student"), student.name)

	def test_a_second_call_reuses_the_linked_customer(self):
		student = make_student()
		customer = frappe.db.get_value("Student", student.name, "customer")

		student.reload()
		before = frappe.db.count("Customer")

		self.assertEqual(create_customer(student), customer)
		self.assertEqual(frappe.db.count("Customer"), before)

	def test_throws_when_no_leaf_group_is_configured(self):
		frappe.db.set_value("Customer Group", "Student", "is_group", 1)
		frappe.db.set_single_value("Selling Settings", "customer_group", "")

		with self.assertRaises(frappe.ValidationError):
			get_customer_group()
