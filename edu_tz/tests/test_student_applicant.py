"""Covers the Student Applicant Fees document raised when an applicant awaits registration fees."""

import frappe
from frappe.tests import IntegrationTestCase

from edu_tz.tests.utils import ACADEMIC_YEAR, ensure, get_company, make_fee_structure, make_program


class TestStudentApplicantFeesCreation(IntegrationTestCase):
	def setUp(self):
		self.company = get_company()
		frappe.db.set_value("Company", self.company, "send_fee_details_to_bank", 0)
		self.program = make_program(self.company)
		self.fee_structure = make_fee_structure(self.company, self.program)

	def tearDown(self):
		frappe.db.rollback()

	def make_applicant(self):
		applicant = frappe.get_doc(
			{
				"doctype": "Student Applicant",
				"first_name": "Edu Tz",
				"last_name": "Applicant",
				"student_email_id": f"applicant-{frappe.generate_hash(length=8)}@example.com",
				"program": self.program,
				"academic_year": ensure("Academic Year", ACADEMIC_YEAR, academic_year_name=ACADEMIC_YEAR),
				"fee_structure": self.fee_structure.name,
			}
		)
		applicant.insert(ignore_permissions=True, ignore_mandatory=True)
		applicant.submit()
		return applicant

	def test_awaiting_registration_fees_raises_a_fee_document(self):
		applicant = self.make_applicant()

		applicant.db_set("application_status", "Awaiting Registration Fees")
		applicant.reload()
		applicant.run_method("on_update_after_submit")

		applicant.reload()
		self.assertTrue(applicant.student_applicant_fee)
		fees = frappe.get_doc("Student Applicant Fees", applicant.student_applicant_fee)
		self.assertEqual(fees.docstatus, 1)
		self.assertEqual(fees.income_account, self.fee_structure.sales_invoice_income_account)
		self.assertEqual(fees.receivable_account, self.fee_structure.receivable_account)
		self.assertEqual(fees.grand_total, self.fee_structure.total_amount)

	def test_no_fee_document_while_the_applicant_is_still_applied(self):
		applicant = self.make_applicant()

		applicant.run_method("on_update_after_submit")

		applicant.reload()
		self.assertFalse(applicant.student_applicant_fee)
