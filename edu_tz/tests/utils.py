"""Fixture builders shared by the edu_tz test suite."""

import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.utils import today

NMB_SERIES = "TST"
NMB_URL = "https://nmb.invalid/"
ACADEMIC_YEAR = "2099-2100"
PROGRAM = "_Test Edu Tz Program"
STUDENT_CATEGORY = "_Test Edu Tz Category"
FEE_CATEGORY = "_Test Edu Tz Fee Category"


def get_company() -> str:
	return frappe.db.get_value("Company", {}, "name")


def enable_nmb(company: str):
	frappe.db.set_value(
		"Company",
		company,
		{"send_fee_details_to_bank": 1, "nmb_series": NMB_SERIES, "nmb_url": NMB_URL},
	)


def allow_fees_insert():
	"""Clears the education v16 fetch_from that points Fees.income_account at a missing Fee Structure field.

	Without it every Fees insert carrying a fee structure fails in `_validate_links`.
	"""
	if frappe.get_meta("Fees").get_field("income_account").fetch_from != "fee_structure.income_account":
		return
	make_property_setter("Fees", "income_account", "fetch_from", "", "Small Text")
	frappe.clear_cache(doctype="Fees")


def ensure(doctype: str, name: str, **values) -> str:
	if frappe.db.exists(doctype, name):
		return name
	doc = frappe.get_doc(doctype=doctype, **values)
	doc.insert(ignore_permissions=True, ignore_mandatory=True)
	return doc.name


def get_account(company: str, **filters) -> str:
	return frappe.db.get_value("Account", dict(company=company, is_group=0, **filters), "name")


def make_program(company: str) -> str:
	program = ensure("Program", PROGRAM, program_name=PROGRAM)
	frappe.db.set_value("Program", program, "company", company)
	return program


def make_student() -> "frappe.Document":
	student = frappe.get_doc(
		{
			"doctype": "Student",
			"first_name": "Edu Tz",
			"last_name": "Tester",
			"date_of_birth": "2005-01-01",
			"student_email_id": f"edu-tz-{frappe.generate_hash(length=8)}@example.com",
		}
	)
	student.insert(ignore_permissions=True, ignore_mandatory=True)
	return student


def make_fee_structure(company: str, program: str) -> "frappe.Document":
	fee_structure = frappe.get_doc(
		{
			"doctype": "Fee Structure",
			"company": company,
			"program": program,
			"academic_year": ensure("Academic Year", ACADEMIC_YEAR, academic_year_name=ACADEMIC_YEAR),
			"receivable_account": get_account(company, account_type="Receivable"),
			"sales_invoice_income_account": get_account(company, root_type="Income"),
			"cost_center": frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name"),
			"student_category": ensure("Student Category", STUDENT_CATEGORY, category=STUDENT_CATEGORY),
			"components": [
				{
					"fees_category": ensure("Fee Category", FEE_CATEGORY, category_name=FEE_CATEGORY),
					"amount": 100,
				}
			],
		}
	)
	fee_structure.insert(ignore_permissions=True, ignore_mandatory=True)
	fee_structure.submit()
	return fee_structure


def make_program_enrollment(student: str, program: str) -> "frappe.Document":
	enrollment = frappe.get_doc(
		{
			"doctype": "Program Enrollment",
			"student": student,
			"program": program,
			"academic_year": ensure("Academic Year", ACADEMIC_YEAR, academic_year_name=ACADEMIC_YEAR),
			"enrollment_date": today(),
			"student_category": ensure("Student Category", STUDENT_CATEGORY, category=STUDENT_CATEGORY),
		}
	)
	enrollment.insert(ignore_permissions=True, ignore_mandatory=True)
	enrollment.submit()
	return enrollment


def make_fees(company: str) -> "frappe.Document":
	"""Builds an unsubmitted Fees document with every link the education controller validates."""
	allow_fees_insert()
	program = make_program(company)
	student = make_student()
	fee_structure = make_fee_structure(company, program)
	enrollment = make_program_enrollment(student.name, program)

	fees = frappe.get_doc(
		{
			"doctype": "Fees",
			"student": student.name,
			"company": company,
			"program": program,
			"program_enrollment": enrollment.name,
			"academic_year": fee_structure.academic_year,
			"fee_structure": fee_structure.name,
			"posting_date": today(),
			"due_date": today(),
			"receivable_account": fee_structure.receivable_account,
			"income_account": fee_structure.sales_invoice_income_account,
			"cost_center": fee_structure.cost_center,
			"components": [{"fees_category": FEE_CATEGORY, "amount": 100}],
		}
	)
	fees.insert(ignore_permissions=True, ignore_mandatory=True)
	return fees
