# Copyright (c) 2013, Scantechalaser.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from accounts_report.accounts_report.report.account_payable_report.account_recievable_custom import ReceivablePayableReport

def execute(filters=None):
	args = {
		"party_type": "Supplier",
		"naming_by": ["Buying Settings", "supp_master_name"],
	}
	return ReceivablePayableReport(filters).run(args)
