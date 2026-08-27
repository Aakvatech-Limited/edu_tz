"""Covers the Fee Collection Report, which reads Student Group names that may be missing."""

import frappe
from frappe.tests import IntegrationTestCase

from edu_tz.edu_tz.report.fee_collection_report.fee_collection_report import execute, get_class_name
from edu_tz.tests.utils import ACADEMIC_YEAR, get_company


def make_filters(**overrides):
	filters = frappe._dict(
		company=get_company(),
		academic_year=ACADEMIC_YEAR,
		program=None,
		summary_based_on_month=0,
		summary_based_on_program=0,
		from_date="2099-01-01",
		to_date="2099-12-31",
	)
	filters.update(overrides)
	return filters


class TestFeeCollectionReport(IntegrationTestCase):
	def test_report_runs_without_data(self):
		columns, data, chart = execute(make_filters())

		self.assertTrue(columns)
		self.assertEqual(data, [])
		self.assertEqual(chart, {})

	def test_monthly_summary_runs_without_data(self):
		columns, data, chart = execute(make_filters(summary_based_on_month=1))

		self.assertTrue(columns)
		self.assertEqual(data, [])
		self.assertIsNone(chart)

	def test_class_name_of_a_student_outside_a_group(self):
		self.assertEqual(get_class_name(frappe._dict(parent=None, academic_year="2099-2100")), "")

	def test_class_name_takes_the_stream_of_a_form_group(self):
		student = frappe._dict(parent="2099-FORM ONE", academic_year="2099-2100")

		self.assertEqual(get_class_name(student), "FORM ONE")

	def test_class_name_joins_program_and_stream(self):
		student = frappe._dict(parent="2099-PRIMARY-STANDARD ONE", academic_year="2099-2100")

		self.assertEqual(get_class_name(student), "PRIMARY - STANDARD ONE")

	def test_unexpected_group_name_is_reported_as_it_stands(self):
		student = frappe._dict(parent="2099-PRIMARY-STANDARD-ONE", academic_year="2099-2100")

		self.assertEqual(get_class_name(student), "2099-PRIMARY-STANDARD-ONE")
