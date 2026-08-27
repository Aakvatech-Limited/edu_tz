import frappe
from erpnext.accounts.party import get_party_account
from frappe import _
from frappe.utils import flt, nowdate


def on_submit(doc, method):
	create_journal_entry(doc)


def create_journal_entry(doc):
	if not doc.fees:
		return
	amount = doc.base_net_total
	debit_account = frappe.get_value("Fees", doc.fees, "sales_invoice_income_account")
	if not debit_account:
		frappe.throw(_("Please set Sales Invoice Income Account on Fees document {0}").format(doc.fees))
	party_account = get_party_account("Customer", doc.customer, doc.company)

	jl_rows = []
	debit_row = dict(
		account=debit_account,
		debit_in_account_currency=flt(amount, doc.precision("base_net_total")),
		exchange_rate=1,
		cost_center=doc.cost_center,
	)
	jl_rows.append(debit_row)

	credit_row = dict(
		party_type="Customer",
		party=doc.customer,
		account=party_account,
		credit_in_account_currency=flt(amount, doc.precision("base_net_total")),
		exchange_rate=1,
		cost_center=doc.cost_center,
		reference_type="Sales Invoice",
		reference_name=doc.name,
	)
	jl_rows.append(credit_row)

	user_remark = "Against Sales Inoice " + doc.name + " For Customer " + doc.customer

	jv_doc = frappe.get_doc(
		doctype="Journal Entry",
		posting_date=nowdate(),
		accounts=jl_rows,
		company=doc.company,
		multi_currency=0,
		user_remark=user_remark,
	)

	jv_doc.flags.ignore_permissions = True
	frappe.flags.ignore_account_permission = True
	jv_doc.save()
	jv_doc.submit()
	jv_url = frappe.utils.get_url_to_form(jv_doc.doctype, jv_doc.name)
	si_msgprint = _("Journal Entry Created <a href='{0}'>{1}</a>").format(jv_url, jv_doc.name)
	frappe.msgprint(si_msgprint)
	return jv_doc.name
