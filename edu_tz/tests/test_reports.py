"""Covers the report entry points, which the v16 query builder and empty result sets both break."""

import frappe
from frappe.tests import IntegrationTestCase

from edu_tz.edu_tz.report.schools_kpi.schools_kpi import execute as schools_kpi
from edu_tz.tests.utils import ACADEMIC_YEAR, get_company, make_program, make_program_enrollment, make_student


class TestSchoolsKPI(IntegrationTestCase):
	def setUp(self):
		self.company = get_company()
		self.program = make_program(self.company)

	def tearDown(self):
		frappe.db.rollback()

	def make_room(self, seating_capacity: int):
		room = frappe.get_doc(
			{
				"doctype": "Room",
				"room_name": "_Test Edu Tz Room",
				"seating_capacity": seating_capacity,
				"edu_tz_program": self.program,
			}
		)
		room.insert(ignore_permissions=True, ignore_mandatory=True)
		return room

	def test_report_runs_without_data(self):
		columns, data = schools_kpi(frappe._dict(academic_year=ACADEMIC_YEAR, company=self.company))

		self.assertTrue(columns)
		self.assertEqual(data, [])

	def test_report_counts_enrolled_students_per_program(self):
		self.make_room(seating_capacity=40)
		make_program_enrollment(make_student().name, self.program)

		_columns, data = schools_kpi(frappe._dict(academic_year=ACADEMIC_YEAR, company=self.company))

		row = next(row for row in data if row["class_name"] == self.program)
		self.assertEqual(row["no_of_students"], 1)
		self.assertEqual(row["class_capacity"], 40)

	def test_enrollments_of_another_company_are_excluded(self):
		self.make_room(seating_capacity=40)
		make_program_enrollment(make_student().name, self.program)
		frappe.db.set_value("Program", self.program, "company", "_Test Edu Tz Other Company")
		frappe.db.set_value(
			"Program Enrollment", {"program": self.program}, "company", "_Test Edu Tz Other Company"
		)

		_columns, data = schools_kpi(frappe._dict(academic_year=ACADEMIC_YEAR, company=self.company))

		self.assertEqual(data, [])
