"""Covers the NMB bank fee integration: token stamping, invoice submission and reference lookup."""

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from edu_tz.edu_tz.nmb.api import invoice_submission
from edu_tz.tests.utils import NMB_SERIES, enable_nmb, get_company, make_fees


class TestNMBAPI(IntegrationTestCase):
	def setUp(self):
		self.company = get_company()
		enable_nmb(self.company)

	def tearDown(self):
		frappe.db.rollback()

	def test_callback_token_is_persisted_on_insert(self):
		fees = make_fees(self.company)

		self.assertTrue(frappe.db.get_value("Fees", fees.name, "callback_token"))

	def test_bank_reference_is_persisted_on_insert(self):
		fees = make_fees(self.company)

		bank_reference = frappe.db.get_value("Fees", fees.name, "bank_reference")
		self.assertTrue(bank_reference.startswith(NMB_SERIES))
		self.assertEqual(bank_reference, fees.bank_reference)

	def test_nothing_is_stamped_when_the_company_does_not_use_the_bank(self):
		frappe.db.set_value("Company", self.company, "send_fee_details_to_bank", 0)

		fees = make_fees(self.company)

		self.assertFalse(frappe.db.get_value("Fees", fees.name, "callback_token"))
		self.assertFalse(frappe.db.get_value("Fees", fees.name, "bank_reference"))

	def test_missing_series_throws(self):
		frappe.db.set_value("Company", self.company, "nmb_series", "")

		with self.assertRaises(frappe.ValidationError):
			make_fees(self.company)

	def test_submit_sends_the_persisted_reference_to_the_bank(self):
		fees = make_fees(self.company)

		with patch("edu_tz.edu_tz.nmb.api.send_nmb") as send_nmb:
			fees.submit()

		payload = send_nmb.call_args[0][1]
		self.assertEqual(payload["reference"], frappe.db.get_value("Fees", fees.name, "bank_reference"))
		self.assertIn(frappe.db.get_value("Fees", fees.name, "callback_token"), payload["callback_url"])

	def test_submit_after_reload_does_not_bump_the_timestamp(self):
		fees = make_fees(self.company)
		fees.reload()

		with patch("edu_tz.edu_tz.nmb.api.send_nmb") as send_nmb:
			fees.submit()

		self.assertTrue(send_nmb.called)
		self.assertEqual(frappe.db.get_value("Fees", fees.name, "docstatus"), 1)

	def test_invoice_submission_by_name_reaches_the_bank(self):
		fees = make_fees(self.company)

		with patch("edu_tz.edu_tz.nmb.api.send_nmb") as send_nmb:
			invoice_submission(fees_name=fees.name)

		self.assertEqual(send_nmb.call_args[0][0], "invoice_submission")

	def test_disabled_company_never_reaches_the_bank(self):
		frappe.db.set_value("Company", self.company, "send_fee_details_to_bank", 0)
		fees = make_fees(self.company)

		with patch("edu_tz.edu_tz.nmb.api.send_nmb") as send_nmb:
			fees.submit()

		send_nmb.assert_not_called()
