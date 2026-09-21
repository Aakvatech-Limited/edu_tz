# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
from erpnext.accounts.utils import update_voucher_outstanding


def fix_stale_fees_outstanding():
	"""Recompute Fees.outstanding_amount from the Payment Ledger where it has drifted.

	Payment Reconciliation creates Payment Ledger Entries against Fees with
	update_outstanding="No" and patches Fees.outstanding_amount in a separate pass
	right after (erpnext.accounts.utils.reconcile_against_document). If that second
	pass doesn't complete for an entry (timeout, lock, worker restart), the Payment
	Ledger Entry stays correctly linked but Fees.outstanding_amount is left stale
	with no error raised anywhere. This task finds and corrects that drift daily.
	"""
	drifted = frappe.db.sql(
		"""
		select
			f.name,
			f.receivable_account,
			f.student,
			max(f.grand_total) as grand_total,
			max(f.outstanding_amount) as outstanding_amount,
			coalesce(sum(ple.amount), 0) as ple_net
		from `tabFees` f
		left join `tabPayment Ledger Entry` ple
			on ple.against_voucher_type = 'Fees'
			and ple.against_voucher_no = f.name
			and ple.delinked = 0
		where f.docstatus = 1
		group by f.name, f.receivable_account, f.student
		having outstanding_amount != grand_total + ple_net
		""",
		as_dict=True,
	)

	if not drifted:
		return

	corrected = []
	for row in drifted:
		try:
			update_voucher_outstanding(
				"Fees", row.name, row.receivable_account, "Student", row.student
			)
			corrected.append(row.name)
		except Exception:
			frappe.log_error(
				title="fix_stale_fees_outstanding: failed for {0}".format(row.name),
				message=frappe.get_traceback(),
			)

	if corrected:
		frappe.db.commit()
		frappe.log_error(
			title="fix_stale_fees_outstanding: corrected {0} Fees".format(len(corrected)),
			message="\n".join(corrected),
		)


def daily():
	fix_stale_fees_outstanding()
