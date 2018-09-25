# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from erpnext import get_company_currency, get_default_company
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from frappe.utils import getdate, cstr, flt, fmt_money
from frappe import _, _dict
from erpnext.accounts.utils import get_account_currency
import re

tempColoumn = []


def execute(filters=None):
	account_details = {}

	getTotal = 0.0

	if filters and filters.get('print_in_account_currency') and \
		not filters.get('account'):
		frappe.throw(_("Select an account to print in account currency"))

	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	filters = set_account_currency(filters)

	

	res, tempColoumn = get_result(filters, account_details)

	columns = get_columns(filters, tempColoumn)

	res = get_total(res, columns)

	return columns, res


def get_total(res, columns):

	
	tempDictCheck = ''
	tempDict = {}


	if res:


		for j in range(19, len(columns)):

			tempDictCheck = columns[int(j)]['fieldname']
			grandTotal = 0.0
			for i in res:

				if str(tempDictCheck) in i:

					grandTotal = grandTotal + float(i[str(tempDictCheck)])

				# getDuplicate = checkDuplicate(tempDictCheck, res)
				# if getDuplicate:

				# grandTotal = grandTotal + float(i.tempDictCheck)
			tempDict[str(tempDictCheck)] = grandTotal
			tempDict['particulars'] = 'Grand Total'

		res.append(tempDict)

		return res



def validate_filters(filters, account_details):
	if not filters.get('company'):
		frappe.throw(_('{0} is mandatory').format(_('Company')))

	if filters.get("account") and not account_details.get(filters.account):
		frappe.throw(_("Account {0} does not exists").format(filters.account))

	if filters.get("account") and filters.get("group_by_account") \
		and account_details[filters.account].is_group == 0:
		frappe.throw(_("Can not filter based on Account, if grouped by Account"))

	if filters.get("voucher_no") and filters.get("group_by_voucher"):
		frappe.throw(_("Can not filter based on Voucher No, if grouped by Voucher"))

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))


def validate_party(filters):
	party_type, party = filters.get("party_type"), filters.get("party")

	if party:
		if not party_type:
			frappe.throw(_("To filter based on Party, select Party Type first"))
		elif not frappe.db.exists(party_type, party):
			frappe.throw(_("Invalid {0}: {1}").format(party_type, party))


def set_account_currency(filters):
	if not (filters.get("account") or filters.get("party")):
		return filters
	else:
		filters["company_currency"] = frappe.db.get_value("Company", filters.company, "default_currency")
		account_currency = None

		if filters.get("account"):
			account_currency = get_account_currency(filters.account)
		elif filters.get("party"):
			gle_currency = frappe.db.get_value(
				"GL Entry", {
					"party_type": filters.party_type, "party": filters.party, "company": filters.company
				},
				"account_currency"
			)

			if gle_currency:
				account_currency = gle_currency
			else:
				account_currency = None if filters.party_type in ["Employee", "Student", "Shareholder"] else \
					frappe.db.get_value(filters.party_type, filters.party, "default_currency")

		filters["account_currency"] = account_currency or filters.company_currency

		if filters.account_currency != filters.company_currency:
			filters["show_in_account_currency"] = 1

		return filters

def get_result(filters, account_details):
	
	gl_entries, mydata = get_gl_entries(filters)

	# data = get_data_with_opening_closing(filters, account_details, gl_entries)
	data = gl_entries
	result = get_result_as_list(data, filters)

	return result, mydata


def get_gl_entries(filters):

	if filters.get("presentation_currency"):
		currency = filters["presentation_currency"]
	else:
		if filters.get("company"):
			currency = get_company_currency(filters["company"])
		else:
			company = get_default_company()
			currency = get_company_currency(company)

	currency_map = get_currency(filters)
	tempDict = []
	tempVar = 0
	oldVar= ""
	temp = 1
	temp1 = False
	columns = []
	tempColoumn = []
	totalGross = 0.0
	setParticulars = []

	# select_fields = """, (B.debit_in_account_currency) as debit_in_account_currency, (B.credit_in_account_currency) as credit_in_account_currency""" \


	group_by_condition = " E.account, E.cost_center" \
		if filters.get("group_by_voucher") else "group by E.name"

	mydata = """SELECT * from `tabGL Entry` E where E.docstatus ='1' AND  {conditions} group by E.account,E.voucher_no order by E.posting_date, E.account """.format( conditions=get_conditions(filters))

	gl_entries = frappe.db.sql(mydata,filters, as_dict=1)
	if gl_entries:

		for j in gl_entries:

			party_type = ''
			party_name = ''
			pan_card = ''

			my_sql = "SELECT * FROM `tab"+str(j.voucher_type)+"` WHERE name = '"+str(j.voucher_no)+"'"
			getVoucher = frappe.db.sql(my_sql, as_dict=True)
			if getVoucher:

				getTitle = getVoucher[0].title

				if(str(j.voucher_type) =='Purchase Invoice'):
					voucher_no = j.against_voucher if j.against_voucher !=None else j.voucher_no

					address,gst_no, party_name, party_type, pan_card = getAddress('tabPurchase Invoice', voucher_no)

					j['address'] = address
					j['gst_no'] = gst_no
					j['party_name'] = party_name
					j['party_type'] = party_type
					j['pan_card'] = pan_card

				if(str(j.voucher_type) == 'Sales Invoice'):

					voucher_no = j.against_voucher if j.against_voucher !=None else j.voucher_no

					address, gst_no, party_name, party_type, pan_card = getAddress('tabSales Invoice', voucher_no)

					j['gst_no'] = gst_no
					j['address'] = address
					j['party_name'] = party_name
					j['party_type'] = party_type
					j['pan_card'] = pan_card

				if(str(j.voucher_type) == 'Journal Entry'):

					voucher_no = j.voucher_no

					address, gst_no, party_name, party_type, pan_card = getAddress('tabJournal Entry', voucher_no)

					j['gst_no'] = gst_no
					j['address'] = address
					j['party_name'] = party_name
					j['party_type'] = party_type
					j['pan_card'] = pan_card

				if str(j.voucher_type) == 'Payment Entry':

					voucher_no = j.voucher_no

					address, gst_no, party_name, party_type, pan_card = getAddress('tabPayment Entry', voucher_no)

					j['gst_no'] = gst_no
					j['address'] = address
					j['party_name'] = party_name
					j['party_type'] = party_type
					j['pan_card'] = pan_card


			if str(j.voucher_type) =='Journal Entry':

				bill_no, bill_date, ref_no, ref_date = getRef(j.voucher_no)

				j['bill_no'] = str(bill_no)
				j['bill_date'] = bill_date
				j['ref_no'] = str(ref_no)
				j['ref_date'] = str(ref_date)
				

			j['voucher_type_link'] = str(j.voucher_type)

			mykey = ''
			account = ''
			accountTotal = 0.0

			accountTotal = setPriorityOfAccount(j.voucher_no, j.account)

			j['particulars'] = str(j.account)
			j['gross'] = str(accountTotal)

			tempDict.append(j)

			tempVar = tempVar + 1

			# frappe.msgprint(tempVar)


			my_sql = "SELECT * FROM `tabGL Entry` WHERE voucher_no = '"+str(j.voucher_no)+"' and account != %s "
			getJournalEntry = frappe.db.sql(my_sql,(j.account), as_dict=True)
			if getJournalEntry:

				for i in getJournalEntry:

					mykey = str(i.account)

					cureentIndex = tempVar - 1

					alredyExist = True

					m = tempDict[int(cureentIndex)]

					if m.has_key(str(j['account'])):

						alredyExist = False

						if(str(j['credit']) !='0.0'):

							m[str(i['account'])] = float(m[str(i['account'])]) - float(i['credit'])
						else:

							m[str(i['account'])] = float(m[str(i['account'])]) + float(i['debit'])


					if alredyExist:


						mykey = str(i['account'])

						if (str(i['debit']) !='0.0'):

							m[mykey] =  float(i['debit'])

						else:

							m[mykey] =  '-'+str(float(i['credit']))

						columnsObj = {}

						columnsObj['label'] = ""+mykey+""
						columnsObj['fieldname'] = ""+mykey+""
						columnsObj['width'] = 90

						if columnsObj:
							if(checkDuplicate(columnsObj['fieldname'],tempColoumn)):
								tempColoumn.append(columnsObj)

		gl_entries = tempDict

	if filters.get('presentation_currency'):
		return convert_to_presentation_currency(gl_entries, currency_map)
	else:
		return gl_entries, tempColoumn


def setPriorityOfAccount(voucher_no='', account=''):

	total = 0.0

	my_sql ="SELECT * FROM `tabGL Entry` WHERE voucher_no ='"+str(voucher_no)+"' and account = %s"
	getEnrtyAccount = frappe.db.sql(my_sql, (account),as_dict=True)
	if getEnrtyAccount:

		for i in getEnrtyAccount:

			if (str(i['debit']) !='0.0'):

				total =  total + float(i['debit'])

			else:

				total =  total - float(i['credit'])

		return total


def getAddress(voucher_type, voucher_no):

	data = ''
	gst_no = ''

	address_title = ''
	party_name = ''
	party_type = ''
	pan_card = ''

	my_sql = "SELECT * FROM `"+voucher_type+"` WHERE name = '"+str(voucher_no)+"'"

	getAddressDetails = frappe.db.sql(my_sql, as_dict=True)
	if getAddressDetails:

		address = ''


		if str(voucher_type) !='tabJournal Entry' and str(voucher_type) !='tabPayment Entry':
			if(getAddressDetails[0].address_display !=None):
				address = getAddressDetails[0].address_display.encode('ascii', 'ignore').decode('ascii')
		else:

			my_sql = "SELECT * FROM `tabJournal Entry Account` WHERE parent = '"+str(voucher_no)+"' AND party !=''"

			if str(voucher_type) =='tabPayment Entry':

				my_sql = "SELECT * FROM `tabPayment Entry` WHERE name = '"+str(voucher_no)+"'"
			
			getJournalEnryAccount = frappe.db.sql(my_sql, as_dict=True)
			if getJournalEnryAccount:

				party_type = getJournalEnryAccount[0].party_type if getJournalEnryAccount[0].party_type !=None else ''
				party_name = getJournalEnryAccount[0].party if getJournalEnryAccount[0].party !=None else ''

				if str(party_type) =='Supplier' or str(party_type) =='Customer':

					if(str(party_type) =='Supplier'):
						my_sql = "SELECT * FROM `tabSupplier` WHERE name = '"+str(getJournalEnryAccount[0].party)+"'"

					else:
						my_sql = "SELECT * FROM `tabCustomer` WHERE name = '"+str(getJournalEnryAccount[0].party)+"'"

					getInfo = frappe.db.sql(my_sql, as_dict=True)
					if getInfo:

						parentId = ''

						if str(party_type) =='Supplier':

							address_title = getInfo[0].supplier_name
						else:
							address_title = getInfo[0].customer_name

						my_sql = "SELECT * FROM `tabDynamic Link` WHERE link_name = '"+str(address_title)+"'"
						getDynamicLink = frappe.db.sql(my_sql, as_dict=True)
						if getDynamicLink:

							parentId = getDynamicLink[0].parent

						address = frappe.db.sql("SELECT name, address_line1, address_line2, city, state, country FROM `tabAddress` WHERE name = '"+str(parentId)+"'", as_dict = True)

						if address:

							if 'address_line1' in address[0]:

								address = str(address[0].address_line1.encode('ascii', 'ignore').decode('ascii')) 

							if 'address_line2' in address[0]:
								address = address +', '+ str(address[0].address_line2.encode('ascii', 'ignore').decode('ascii'))


							if 'city' in address[0]:
								address = address +', '+ str(address[0].city.encode('ascii', 'ignore').decode('ascii'))

							if 'state' in address[0]:
								address = address +', '+ str(address[0].state.encode('ascii', 'ignore').decode('ascii'))


							if 'country' in address[0]:
								address = address +', '+ str(address[0].country.encode('ascii', 'ignore').decode('ascii'))

						else:
							address = ''

						address = address.encode('ascii', 'ignore').decode('ascii')

						
		
		data = re.sub(r'<.*?>', '', address)
		my_sql = ''
		getGST = ''

		if str(voucher_type) == 'tabPurchase Invoice':

			party_type = 'Supplier'

			my_sql = "SELECT * FROM `tabAddress` WHERE name = '"+str(getAddressDetails[0].supplier_address)+"'"

		elif str(voucher_type) == 'tabSales Invoice':
			my_sql = "SELECT * FROM `tabAddress` WHERE name = '"+str(getAddressDetails[0].customer_address)+"'"
			party_type = 'Customer'

		if address_title:
			my_sql = "SELECT * FROM `tabAddress` WHERE address_title = '"+str(address_title)+"'"

		if my_sql:
			getGST = frappe.db.sql(my_sql, as_dict=True)

		if getGST:

			party_name = getGST[0].address_title if getGST[0].address_title !=None else ''
			
			gst_no = getGST[0].gstin if getGST[0].gstin !=None else ''

			pan_card = getGST[0].incom_tax_number if getGST[0].incom_tax_number !=None else ''

		return data, gst_no, party_name, party_type, pan_card

def getRef(voucher_no):
 
	my_sql = "SELECT * FROM `tabJournal Entry` where name = '"+str(voucher_no)+"'"
	getRefData = frappe.db.sql(my_sql, as_dict=True)
	if getRefData:

		return getRefData[0].bill_no if getRefData[0].bill_no !=None else '', getRefData[0].bill_date if getRefData[0].bill_date !=None else '', getRefData[0].cheque_no if getRefData[0].cheque_no !=None else '', getRefData[0].cheque_date if getRefData[0].cheque_date !=None else ''


def checkDuplicate(fieldName = '', tempColoumn=[]):
	tempData = True
	if tempColoumn:
		for i in tempColoumn:
			if (str(i['fieldname']) == str(fieldName)):
				tempData = False
				return False
	if tempData:
		return True

		

def get_conditions(filters):
	conditions = []
	if filters.get("account_type"):
		lft, rgt = frappe.db.get_value("Account", filters["account_type"], ["lft", "rgt"])
		conditions.append("""E.account in (select name from tabAccount
			where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))

	if filters.get("voucher_no"):
		conditions.append("E.voucher_no = %(voucher_no)s")

	# if filters.get("account_type"):
	# 	conditions.append("E.account=%(account_type)s")

	if not (filters.get("account") or filters.get("party") or filters.get("group_by_account")):
		conditions.append("E.posting_date >= %(from_date)s")
		conditions.append("E.posting_date <= %(to_date)s")

	if filters.get("project"):
		conditions.append("E.project=%(company)s")

	if filters.get("company"):
		conditions.append("E.company=%(company)s")


	return " {}".format(" and ".join(conditions)) if conditions else ""


def get_data_with_opening_closing(filters, account_details, gl_entries):
	data = []
	gle_map = initialize_gle_map(gl_entries)

	totals, entries = get_accountwise_gle(filters, gl_entries, gle_map)

	# Opening for filtered account
	data.append(totals.opening)

	if filters.get("group_by_account"):
		for acc, acc_dict in gle_map.items():
			if acc_dict.entries:
				# opening
				data.append({})
				data.append(acc_dict.totals.opening)

				data += acc_dict.entries

				# totals
				data.append(acc_dict.totals.total)

				# closing
				data.append(acc_dict.totals.closing)
		data.append({})

	else:
		data += entries

	# totals
	data.append(totals.total)

	# closing
	data.append(totals.closing)

	return data


def get_totals_dict():
	def _get_debit_credit_dict(label):
		return _dict(
			account="'{0}'".format(label),
			debit=0.0,
			credit=0.0,
			debit_in_account_currency=0.0,
			credit_in_account_currency=0.0
		)
	return _dict(
		opening = _get_debit_credit_dict(_('Opening')),
		total = _get_debit_credit_dict(_('Total')),
		closing = _get_debit_credit_dict(_('Closing (Opening + Total)'))
	)


def initialize_gle_map(gl_entries):
	gle_map = frappe._dict()
	for gle in gl_entries:
		gle_map.setdefault(gle.account, _dict(totals=get_totals_dict(), entries=[]))
	return gle_map


def get_accountwise_gle(filters, gl_entries, gle_map):
	totals = get_totals_dict()
	entries = []

	def update_value_in_dict(data, key, gle):
		data[key].debit += flt(gle.debit)
		data[key].credit += flt(gle.credit)

		data[key].debit_in_account_currency += flt(gle.debit_in_account_currency)
		data[key].credit_in_account_currency += flt(gle.credit_in_account_currency)

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	for gle in gl_entries:
		if gle.posting_date < from_date or cstr(gle.is_opening) == "Yes":
			update_value_in_dict(gle_map[gle.account].totals, 'opening', gle)
			update_value_in_dict(totals, 'opening', gle)

			update_value_in_dict(gle_map[gle.account].totals, 'closing', gle)
			update_value_in_dict(totals, 'closing', gle)

		elif gle.posting_date <= to_date:
			update_value_in_dict(gle_map[gle.account].totals, 'total', gle)
			update_value_in_dict(totals, 'total', gle)
			if filters.get("group_by_account"):
				gle_map[gle.account].entries.append(gle)
			else:
				entries.append(gle)

			update_value_in_dict(gle_map[gle.account].totals, 'closing', gle)
			update_value_in_dict(totals, 'closing', gle)

	return totals, entries


def get_result_as_list(data, filters):
	balance, balance_in_account_currency = 0, 0
	inv_details = get_supplier_invoice_details()

	for d in data:
		if not d.get('posting_date'):
			balance, balance_in_account_currency = 0, 0

		balance = get_balance(d, balance, 'debit', 'credit')
		d['balance'] = balance

		if filters.get("show_in_account_currency"):
			balance_in_account_currency = get_balance(d, balance_in_account_currency,
				'debit_in_account_currency', 'credit_in_account_currency')
			d['balance_in_account_currency'] = balance_in_account_currency
		else:
			d['debit_in_account_currency'] = d.get('debit', 0)
			d['credit_in_account_currency'] = d.get('credit', 0)
			d['balance_in_account_currency'] = d.get('balance')

		d['account_currency'] = filters.account_currency
		# d['bill_no'] = inv_details.get(d.get('against_voucher'), '')

	return data

def get_supplier_invoice_details():
	inv_details = {}
	for d in frappe.db.sql(""" select name, bill_no from `tabPurchase Invoice`
		where docstatus = 1 and bill_no is not null and bill_no != '' """, as_dict=1):
		inv_details[d.name] = d.bill_no

	return inv_details

def get_balance(row, balance, debit_field, credit_field):
	balance += (row.get(debit_field, 0) -  row.get(credit_field, 0))

	return balance

def getAccountType():
	accountData = []
	mysql = "SELECT * FROM  `tabAccount` where docstatus='0'"
	getAccountDetails = frappe.db.sql(mysql,as_dict=True)
	if getAccountDetails:
		for i in getAccountDetails:
			accountData.append({"name":i.name,
				"account_name":i.account_name,
				"parent":i.parent})

	return accountData


def get_columns(filters, tempColoumn):
	columns = []
	# tempColoumn = []
	frappe.msgprint(len(tempColoumn))
	if filters.get("presentation_currency"):
		currency = filters["presentation_currency"]
	else:
		if filters.get("company"):
			currency = get_company_currency(filters["company"])
		else:
			company = get_default_company()
			currency = get_company_currency(company)

	columns = [
		{
			"label": _("Jv Ref"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type_link",
			"width": 180
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 90
		},
		{
			"label": _("Particulars"),
			"fieldname": "particulars",
			"width": 120
		},
		{
			"label": _("Party Name"),
			"fieldname": "party_name",
			"width": 100
		},
		{
			"label": _("Party"),
			"fieldname": "party_type",
			"width": 100
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"width": 180
		},
		{
			"label": _("Voucher Type"),
			"fieldname": "voucher_type",
			"width": 120
		},
		{
			"label": _("Address"),
			"fieldname": "address",
			"fieldtype": "Small Text",
			"width": 400
		},
		{
			"label": _("Pan Card"),
			"fieldname": "pan_card",
			"width": 100
		},
		{
			"label": _("GST NO."),
			"fieldname": "gst_no",
			"width": 100
		},
		{
			"label": _("Bill No"),
			"fieldname": "bill_no",
			"width": 100
		},
		{
			"label": _("Bill Date"),
			"fieldname": "bill_date",
			"fieldtype": "Date",
			"width": 90
		},
		{
			"label": _("Remarks"),
			"fieldname": "remarks",
			"width": 400
		},
		{
			"label": _("Ref No."),
			"fieldname": "ref_no",
			"width": 100
		},
		{
			"label": _("Ref Date"),
			"fieldname": "ref_date",
			"fieldtype": "Date",
			"width": 90
		},
		{
			"label": _("Is Advance"),
			"fieldname": "is_advance",
			"width": 90
		},
		{
			"label": _("Is Opening"),
			"fieldname": "is_opening",
			"width": 90
		},
		{
			"label": _("Created by whom"),
			"fieldname": "owner",
			"width": 90
		},
		{
			"label": _("Modified by whom"),
			"fieldname": "modified_by",
			"width": 90
		},
		{
			"label": _("Gross ({0})".format(currency)),
			"fieldname": "gross",
			"fieldtype": "Float",
			"width": 100
		}
	]

	if tempColoumn:
		for i in tempColoumn:
			columns.append(i)

	return columns
