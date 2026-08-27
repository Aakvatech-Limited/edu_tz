import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns(filters)

	if filters.summary_based_on_month:
		data, chart = get_summary_based_on_month(filters)
	else:
		data, chart = get_fees(filters), {}

	return columns, data, chart


def get_filter_condtions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND fe.company = %(company)s "
	if filters.get("academic_year"):
		conditions += " AND fe.academic_year = %(academic_year)s "
		conditions += " AND p_en.academic_year = %(academic_year)s "
		conditions += " AND sg.academic_year = %(academic_year)s "
	if filters.get("program"):
		conditions += " AND fe.program = %(program)s "
		conditions += " AND p_en.program = %(program)s "
		conditions += " AND sg.program = %(program)s "

	return conditions


def get_columns(filters):
	if filters.summary_based_on_month:
		columns = [
			{"fieldname": "year", "fieldtype": "Data", "label": _("Year of Due Date")},
			{"fieldname": "month", "fieldtype": "Data", "label": _("Month")},
			{"fieldname": "program", "fieldtype": "Data", "label": _("Program")},
			{
				"fieldname": "total_amount_to_be_paid",
				"fieldtype": "Currency",
				"label": _("Total Fee to be Collected"),
			},
			{"fieldname": "total_paid_amount", "fieldtype": "Currency", "label": _("Total Fee Collected")},
			{"fieldname": "outstanding_amount", "fieldtype": "Currency", "label": _("Outstanding Amount")},
		]

	else:
		columns = [
			{"fieldname": "academic_year", "fieldtype": "Data", "label": _("Academic Year")},
			{"fieldname": "student_name", "fieldtype": "Data", "label": _("Student Name")},
			{"fieldname": "program", "fieldtype": "Data", "label": _("Program")},
			{"fieldname": "class_name", "fieldtype": "Data", "label": _("Class Name")},
			{"fieldname": "student_category", "fieldtype": "Data", "label": _("Fee Category")},
			{
				"fieldname": "total_amount_to_be_paid",
				"fieldtype": "Currency",
				"label": _("Fee to be Collected"),
			},
			{
				"fieldname": "1st_installment_paid_amount",
				"fieldtype": "Currency",
				"label": _("1st Installment Paid"),
			},
			{
				"fieldname": "2nd_installment_paid_amount",
				"fieldtype": "Currency",
				"label": _("2nd Installment Paid"),
			},
			{
				"fieldname": "3rd_installment_paid_amount",
				"fieldtype": "Currency",
				"label": _("3rd Installment Paid"),
			},
			{
				"fieldname": "4th_installment_paid_amount",
				"fieldtype": "Currency",
				"label": _("4th Installment Paid"),
			},
			{
				"fieldname": "5th_installment_paid_amount",
				"fieldtype": "Currency",
				"label": _("5th Installment Paid"),
			},
			{"fieldname": "total_paid_amount", "fieldtype": "Currency", "label": _("Total Fee Collected")},
			{"fieldname": "outstanding_amount", "fieldtype": "Currency", "label": _("Outstanding Amount")},
		]
	return columns


def get_fees(filters):
	fees_record = []
	student_records = []
	if not filters.summary_based_on_program:
		student_details, student_name_list = get_fee_details(filters)

		first_installment_list = []
		second_installment_list = []
		third_installment_list = []
		fourth_installment_list = []
		fifth_installment_list = []

		for st_name in student_name_list:
			total_amount_to_be_paid = total_unpaid_amount = 0

			for student_row in student_details:
				if (
					st_name["student"] == student_row["student"]
					and st_name["program"] == student_row["program"]
					and st_name["class_name"] == student_row["class_name"]
				):
					total_amount_to_be_paid += student_row["grand_total"]
					total_unpaid_amount += student_row["outstanding_amount"]

					if st_name not in first_installment_list:
						st_name.update(
							{"paid_amount1": student_row["grand_total"] - student_row["outstanding_amount"]}
						)
						first_installment_list.append(st_name)

					elif st_name not in second_installment_list:
						st_name["paid_amount2"] = (
							student_row["grand_total"] - student_row["outstanding_amount"]
						)
						second_installment_list.append(st_name)

					elif st_name not in third_installment_list:
						st_name.update(
							{"paid_amount3": student_row["grand_total"] - student_row["outstanding_amount"]}
						)
						third_installment_list.append(st_name)

					elif st_name not in fourth_installment_list:
						st_name.update(
							{"paid_amount4": student_row["grand_total"] - student_row["outstanding_amount"]}
						)
						fourth_installment_list.append(st_name)

					else:
						st_name.update(
							{"paid_amount5": student_row["grand_total"] - student_row["outstanding_amount"]}
						)
						fifth_installment_list.append(st_name)

			st_name.update(
				{
					"total_amount_to_be_paid": total_amount_to_be_paid,
					"outstanding_amount": total_unpaid_amount,
				}
			)
			student_records.append(st_name)

		for record in student_records:
			paid_amount = 0
			for first in first_installment_list:
				if (
					record["student"] == first["student"]
					and record["program"] == first["program"]
					and record["class_name"] == first["class_name"]
				):
					record.update(
						{
							"1st_installment_paid_amount": first["paid_amount1"],
						}
					)
					paid_amount += first["paid_amount1"]

			for second in second_installment_list:
				if (
					record["student"] == second["student"]
					and record["program"] == second["program"]
					and record["class_name"] == second["class_name"]
				):
					record.update({"2nd_installment_paid_amount": second["paid_amount2"]})
					paid_amount += second["paid_amount2"]

			for third in third_installment_list:
				if (
					record["student"] == third["student"]
					and record["program"] == third["program"]
					and record["class_name"] == third["class_name"]
				):
					record.update({"3rd_installment_paid_amount": third["paid_amount3"]})
					paid_amount += third["paid_amount3"]

			for fourth in fourth_installment_list:
				if (
					record["student"] == fourth["student"]
					and record["program"] == fourth["program"]
					and record["class_name"] == fourth["class_name"]
				):
					record.update({"4th_installment_paid_amount": fourth["paid_amount4"]})
					paid_amount += fourth["paid_amount4"]

			for fifth in fifth_installment_list:
				if (
					record["student"] == fifth["student"]
					and record["program"] == fifth["program"]
					and record["class_name"] == fifth["class_name"]
				):
					record.update({"5th_installment_paid_amount": fifth["paid_amount5"]})
					paid_amount += fifth["paid_amount5"]

			record["total_paid_amount"] = paid_amount
			fees_record.append(record)
	return fees_record


def get_fee_details(filters):
	name_list = []
	student_list = []
	student_details = []

	conditions = get_filter_condtions(filters)

	# conditions only add %(name)s placeholders, values are bound via filters
	fee_details = frappe.db.sql(  # nosemgrep
		f"""
		SELECT fe.due_date, fe.student, fe.student_name, fe.program,
			fe.grand_total, fe.outstanding_amount, p_en.student_category,
			sg.academic_year, sgs.parent
		FROM `tabFees` fe
			INNER JOIN `tabProgram Enrollment` p_en ON fe.student = p_en.student
			LEFT JOIN `tabStudent Group Student` sgs ON sgs.student = fe.student AND sgs.active = 1
			LEFT JOIN `tabStudent Group` sg ON sgs.parent = sg.name AND sg.disabled = 0
		WHERE fe.docstatus = 1
		AND p_en.docstatus = 1 {conditions}
		ORDER BY fe.due_date asc, fe.student asc
	""",
		filters,
		as_dict=1,
	)

	for student in fee_details:
		student.update({"class_name": get_class_name(student)})

		student_details.append(student)

		if student.student not in name_list:
			name_list.append(student.student)
			student_list.append(student)

	return student_details, student_list


def get_class_name(student) -> str:
	"""Derives the class from the Student Group name, which encodes the year, program and stream.

	Students outside an active group have no name to derive from, and a name that does not
	split into the expected parts is reported as it stands.
	"""
	group_name = student.parent
	if not group_name:
		return ""

	has_form = "FORM" in group_name
	has_toddlers = "TODDLERS" in group_name
	parts = group_name.split("-")

	if student.academic_year == 2020 or (has_form and has_toddlers):
		return group_name
	if has_form != has_toddlers:
		return parts[1] if len(parts) == 2 else group_name
	return f"{parts[1]} - {parts[2]}" if len(parts) == 3 else group_name


def get_summary_based_on_month(filters):
	summary_data = []

	conditions = ""
	if filters.get("company"):
		conditions += " AND fe.company = %(company)s "
	if filters.get("academic_year"):
		conditions += " AND fe.academic_year = %(academic_year)s "
		conditions += " AND p_en.academic_year = %(academic_year)s "

	# conditions only add %(name)s placeholders, values are bound via filters
	fee_details = frappe.db.sql(  # nosemgrep
		f"""
		SELECT YEAR(fe.due_date) as year, MONTHNAME(fe.due_date) AS month, fe.program, SUM(fe.grand_total) AS grand_total,
			SUM(fe.outstanding_amount) AS outstanding_amount
		FROM `tabFees` fe
		INNER JOIN `tabProgram Enrollment` p_en ON fe.student = p_en.student AND fe.program = p_en.program
		WHERE fe.docstatus = 1 AND p_en.docstatus = 1 {conditions}
		GROUP BY MONTHNAME(fe.due_date), fe.program
		ORDER BY YEAR(fe.due_date), MONTHNAME(fe.due_date), fe.program
		""",
		filters,
		as_dict=1,
	)

	for fee in fee_details:
		summary_data.append(
			{
				"year": fee.year,
				"month": fee.month,
				"program": fee.program,
				"total_paid_amount": fee.grand_total - fee.outstanding_amount,
				"outstanding_amount": fee.outstanding_amount,
				"total_amount_to_be_paid": fee.grand_total,
			}
		)

	chart = get_chart_data(summary_data)

	return summary_data, chart


def get_chart_data(summary_data):
	if not summary_data:
		return

	labels = []
	fees_collected = []
	outstanding_amount = []
	fees_to_be_collected = []

	for entry in summary_data:
		labels.append(entry.get("program"))
		fees_collected.append(entry.get("total_paid_amount"))
		outstanding_amount.append(entry.get("outstanding_amount"))
		fees_to_be_collected.append(entry.get("total_amount_to_be_paid"))

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Fee to be Collected"), "values": fees_to_be_collected},
				{"name": _("Fees Collected"), "values": fees_collected},
				{"name": _("Outstanding Amount"), "values": outstanding_amount},
			],
		},
		"type": "bar",
	}
