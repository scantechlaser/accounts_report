# -*- coding: utf-8 -*-
# Copyright (c) 2019, Scantechalaser.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt, cint, getdate, now_datetime, formatdate, strip,time_diff_in_hours
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from frappe.utils import getdate
import calendar
import datetime
from datetime import *

class AssetCancellation(Document):
	def validate(self):

		my_sql = "SELECT * FROM `tabAsset` WHERE name='"+str(self.doctype_name)+"'"
		get_assets = frappe.db.sql(my_sql, as_dict=True)
		if get_assets:
			if get_assets[0].purchase_receipt:
				my_sql = "SELECT * FROM `tabPurchase Receipt Item` WHERE parent ='"+str(get_assets[0].purchase_receipt)+"' and asset='"+str(self.doctype_name)+"' "
				get_reciept = frappe.db.sql(my_sql, as_dict=True)
				if get_reciept:
					frappe.db.sql("UPDATE `tabAsset` SET purchase_receipt =''")
					frappe.msgprint(_(get_reciept[0].name))
					# doc = frappe.get_doc('Purchase Receipt', get_assets[0].purchase_receipt)
					# doc.cancel()

			if get_assets[0].purchase_invoice:

				my_sql = "SELECT * FROM `tabPurchase Invoice Item` WHERE parent ='"+str(get_assets[0].purchase_invoice)+"' and asset='"+str(self.doctype_name)+"' "
				get_invoice = frappe.db.sql(my_sql, as_dict=True)
				if get_invoice:
					frappe.db.sql("UPDATE `tabAsset` SET purchase_invoice =''")
					frappe.msgprint(_(get_invoice[0].name))
					doc = frappe.get_doc('Purchase Invoice', get_assets[0].purchase_invoice)
					doc.cancel()
			doc = frappe.get_doc('Asset', self.doctype_name)
			doc.cancel()
			frappe.msgprint(_("Cancellation Successfully Done!"))
			# frappe.throw(_('Ok'))
