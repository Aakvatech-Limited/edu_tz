frappe.ui.form.on("Payment Reconciliation", {
  refresh: function (frm) {
    // Override ERPNext core filter which hard-codes only "Customer" → Asset.
    // Student (and any future Receivable party type) also needs Asset accounts.
    frm.set_query("receivable_payable_account", () => {
      return {
        filters: {
          company: frm.doc.company,
          is_group: 0,
          account_type: frappe.boot.party_account_types[frm.doc.party_type],
          root_type:
            frappe.boot.party_account_types[frm.doc.party_type] == "Receivable"
              ? "Asset"
              : "Liability",
        },
      };
    });
  },
});
