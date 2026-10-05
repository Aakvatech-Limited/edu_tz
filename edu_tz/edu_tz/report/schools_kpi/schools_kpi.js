// Copyright (c) 2016, Aakvatech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Schools KPI"] = {
  filters: [
    {
      fieldname: "academic_year",
      label: __("Academic Year"),
      fieldtype: "Data",
      default: "",
      reqd: 1,
    },
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      reqd: 1,
    },
  ],
};
