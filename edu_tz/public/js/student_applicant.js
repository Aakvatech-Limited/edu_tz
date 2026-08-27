frappe.ui.form.on('Student Applicant', {
	onload: function(frm) {
		frm.trigger("setup_btns");
	},
	refresh: function(frm) {
		frm.trigger("setup_btns");
	},
	fee_structure: function(frm) {
		frm.trigger("setup_btns");
	},
	setup_btns: async function(frm) {
		if (!await sends_fee_details_to_bank(frm)) {
			return;
		}
		if(frm.doc.docstatus == 1 && frm.doc.application_status != "Approved") {
			frm.clear_custom_buttons();
			if(frm.doc.application_status == "Applied") {
				frm.add_custom_button(__("Reject"), function() {
					frm.set_value("application_status", "Rejected");
					frm.save_or_update();
				}, 'Student Applicant Actions');
			}
			if(["Applied", "Rejected"].includes(frm.doc.application_status)) {
				frm.add_custom_button(__("Awaiting Registration Fees"), function() {
					frm.set_value("application_status", "Awaiting Registration Fees");
					frm.save_or_update();
				}, 'Student Applicant Actions');
			}
		}
	},
});

// Resolved on demand: the buttons render before an answer fetched in `setup` comes back.
async function sends_fee_details_to_bank(frm) {
	if (!frm.doc.fee_structure) {
		return false;
	}
	const structure = await frappe.db.get_value('Fee Structure', frm.doc.fee_structure, 'company');
	const company = structure.message && structure.message.company;
	if (!company) {
		return false;
	}
	const settings = await frappe.db.get_value('Company', company, 'send_fee_details_to_bank');
	return Boolean(settings.message && settings.message.send_fee_details_to_bank);
}
