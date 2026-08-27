"""Covers the daily NMB reconciliation job, which reads bank transactions as plain dictionaries."""

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from edu_tz.edu_tz.nmb.api import is_known_callback, reconciliation
from edu_tz.tests.utils import enable_nmb, get_company, make_fees

REFERENCE = "TSTRECON001"
RECEIPT = "RCPT001"


def make_response(reference: str) -> dict:
	return {
		"status": 1,
		"description": "success",
		"transactions": [
			{
				"reference": reference,
				"receipt": RECEIPT,
				"amount": 100,
				"timestamp": frappe.utils.now(),
			}
		],
	}


class TestNMBReconciliation(IntegrationTestCase):
	def setUp(self):
		self.company = get_company()
		enable_nmb(self.company)
		frappe.db.set_value("Company", self.company, "nmb_username", "edu-tz-test")

	def tearDown(self):
		frappe.db.rollback()

	def make_callback(self, reference: str):
		callback = frappe.get_doc(
			{
				"doctype": "NMB Callback",
				"reference": reference,
				"receipt": RECEIPT,
				"amount": 100,
			}
		)
		callback.insert(ignore_permissions=True)
		return callback

	def test_is_known_callback_reads_a_plain_transaction(self):
		transaction = make_response(REFERENCE)["transactions"][0]

		self.assertFalse(is_known_callback(transaction))

		self.make_callback(REFERENCE)
		self.assertTrue(is_known_callback(transaction))

	def test_unmatched_reference_enqueues_nothing(self):
		self.make_callback(REFERENCE)

		with (
			patch("edu_tz.edu_tz.nmb.api.send_nmb", return_value=make_response(REFERENCE)),
			patch("edu_tz.edu_tz.nmb.api.enqueue") as enqueue,
		):
			reconciliation()

		enqueue.assert_not_called()

	def test_matched_reference_enqueues_the_transaction(self):
		fees = make_fees(self.company)
		with patch("edu_tz.edu_tz.nmb.api.send_nmb"):
			fees.submit()
		reference = frappe.db.get_value("Fees", fees.name, "bank_reference")
		self.make_callback(reference)

		with (
			patch("edu_tz.edu_tz.nmb.api.send_nmb", return_value=make_response(reference)),
			patch("edu_tz.edu_tz.nmb.api.enqueue") as enqueue,
		):
			reconciliation()

		callback = enqueue.call_args.kwargs["kwargs"]
		self.assertEqual(callback.reference, reference)
		self.assertEqual(callback.receipt, RECEIPT)
		self.assertEqual(callback.fees_token, frappe.db.get_value("Fees", fees.name, "callback_token"))
