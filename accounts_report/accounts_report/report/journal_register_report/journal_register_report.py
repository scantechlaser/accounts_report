# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from erpnext import get_company_currency, get_default_company
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from frappe.utils import getdate, cstr, flt, fmt_money
from frappe import _, _dict
from erpnext.accounts.utils import get_account_currency

tempColoumn = []


def execute(filters=None):
	account_details = {}

	if filters and filters.get('print_in_account_currency') and \
		not filters.get('account'):
		frappe.throw(_("Select an account to print in account currency"))

	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	filters = set_account_currency(filters)

	

	res, tempColoumn = get_result(filters, account_details)

	columns = get_columns(filters, tempColoumn)


	return columns, res


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
	tempVar = ""
	oldVar= ""
	temp = 1
	temp1 = False
	columns = []
	tempColoumn = []
	totalGross = 0.0
	setParticulars = []

	myVar = 0

	select_fields = """, (B.debit_in_account_currency) as debit_in_account_currency, (B.credit_in_account_currency) as credit_in_account_currency""" \


	group_by_condition = " B.account, B.cost_center" \
		if filters.get("group_by_voucher") else "group by E.name"

	mydata = """select E.posting_date, E.is_opening as is_opening, B.is_advance as is_advance, E.title, E.bill_no as bill_no, E.company as company, E.voucher_type as voucher_type, E.voucher_type as voucher_type_link, E.owner as created_by_whom, E.modified_by as modified_by_whom, B.party_type as party_type, E.bill_date as bill_date, B.parent as voucher_no, B.account, B.party as party_name,(E.total_debit) as debit, B.name as childId, B.credit as account_credit, B.debit as account_debit, (E.total_credit) as credit, B.cost_center, B.project,account_currency,E.remark, E.is_opening {select_fields} from `tabJournal Entry` E LEFT JOIN `tabJournal Entry Account` B ON B.parent = E.name where E.docstatus ='1' AND  {conditions} order by E.posting_date, B.account """.format(select_fields=select_fields, conditions=get_conditions(filters))

	gl_entries = frappe.db.sql(mydata,filters, as_dict=1)
	if gl_entries:


		for j in gl_entries:


			j['voucher_type_link'] = 'Journal Entry'
			mykey = ''
			setPriority = ''
			totalGross = 0.0
			
						
			if(temp == 1):


				temp = 2
				myVar = myVar +1

				j['particulars'] = ''
				
				setPriority, totalGross, isDuplicate = setPriorityOfAccount(j.voucher_no, setParticulars, tempColoumn)




				if setPriority and isDuplicate:

					setParticulars.append(setPriority)


				if setPriority:

					mykey = 'gross'

					j['particulars'] = str(setPriority)
					j['gross'] = str(totalGross)


				if(str(j['account']) != str(setPriority)):

					j['credit'] = float("-"+str(j['credit']))

					mykey = str(j['account'])

					j[mykey] = str(j['account_debit'])

					if(str(j['account_credit']) != '0.0'):

						j[mykey] = '-'+str(j['account_credit'])

					j['bill_no'] = j['bill_no']


				tempDict.append(j)

				columnsObj = {}
				if (mykey != 'gross' and mykey !=''):
					columnsObj['label'] = ""+mykey+""
					columnsObj['fieldname'] = ""+mykey+""
					columnsObj['fieldtype'] = "Float"
					columnsObj['width'] = 90

				if columnsObj:
					if(checkDuplicate(columnsObj['fieldname'],tempColoumn)):
						tempColoumn.append(columnsObj)

			else:
				if tempDict:
					temp1 = True
					for m in tempDict:
						if(m['voucher_no'] == j['voucher_no']):

							mykey = ''

							alredyExist = True

							if m.has_key(str(j['account'])):

								alredyExist = False

								if(str(j['account_credit']) !='0.0'):

									m[str(j['account'])] = float(m[str(j['account'])]) - float(j['account_credit'])
								else:

									m[str(j['account'])] = float(m[str(j['account'])]) + float(j['account_debit'])

							if alredyExist:

								if(str(m['particulars']) != str(j['account'])):

									mykey = str(j['account'])

									if (str(j['account_debit']) !='0.0'):

										m[mykey] =  float(j['account_debit'])

									else:

										m[mykey] =  '-'+str(float(j['account_credit']))


								columnsObj = {}


								if (mykey != 'gross' and mykey !=''):
									columnsObj['label'] = ""+mykey+""
									columnsObj['fieldname'] = ""+mykey+""
									columnsObj['fieldtype'] = "Float"
									columnsObj['width'] = 90

								if columnsObj:
									if(checkDuplicate(columnsObj['fieldname'],tempColoumn)):
										tempColoumn.append(columnsObj)


							temp1 = False

					if temp1:

						
						setPriority = ''
						myVar = myVar +1

						j['particulars'] = ''						

						setPriority, totalGross, isDuplicate = setPriorityOfAccount(j.voucher_no, setParticulars, tempColoumn)


						if setPriority != None and str(setPriority) != '' and isDuplicate == True:

							setParticulars.append(setPriority)

						if setPriority:

							mykey = 'gross'

							j['particulars'] = str(setPriority)
							j['gross'] = str(totalGross)


						if(str(j['account']) != str(setPriority)):

							if float(j['credit']) > 0.0:
								
								j['credit'] = float("-"+str(j['credit']))

							mykey = str(j['account'])

							j[mykey] = str(j['account_debit'])

							if(str(j['account_credit']) != '0.0'):

								j[mykey] = '-'+str(j['account_credit'])

							j['bill_no'] = j['bill_no']

						tempDict.append(j)

						columnsObj = {}
						if (mykey != 'gross' and mykey !=''):
							columnsObj['label'] = ""+mykey+""
							columnsObj['fieldname'] = ""+mykey+""
							columnsObj['fieldtype'] = "Float"
							columnsObj['width'] = 90
							
						if columnsObj:
							if(checkDuplicate(columnsObj['fieldname'],tempColoumn)):
								tempColoumn.append(columnsObj)


		gl_entries = tempDict

	if filters.get('presentation_currency'):
		return convert_to_presentation_currency(gl_entries, currency_map)
	else:
		return gl_entries, tempColoumn

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
	if filters.get("account"):
		lft, rgt = frappe.db.get_value("Account", filters["account"], ["lft", "rgt"])
		conditions.append("""account in (select name from tabAccount
			where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))

	if filters.get("voucher_no"):
		conditions.append("E.name=%(voucher_no)s")

	if filters.get("party_type"):
		conditions.append("B.party_type=%(party_type)s")

	if filters.get("party"):
		conditions.append("B.party=%(party)s")

	if not (filters.get("account") or filters.get("party") or filters.get("group_by_account")):
		conditions.append("E.posting_date >= %(from_date)s")
		conditions.append("E.posting_date <= %(to_date)s")

	if filters.get("project"):
		conditions.append("B.project=%(company)s")

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


def setPriorityOfAccount(parentId= '', setParticulars = [], tempDict = []):

	account_exist = True
	isDuplicate = True

	ifParticulars = True

	isCoulmn = False
	accountArray = []
	accountArrayType = []

	my_sql = "SELECT * FROM `tabJournal Entry Account` WHERE parent = '"+str(parentId)+"' group by account"
	getAccountDetails = frappe.db.sql(my_sql, as_dict= True)
	if getAccountDetails:

		for o in getAccountDetails:

			# my_sql = "SELECT * FROM `tabAccount` WHERE name = %s and report_type ='Balance Sheet'"
			# getAccountReport = frappe.db.sql(my_sql, (o.account), as_dict=True)
			# if getAccountReport:

			accountArray.append({"account": str(o.account), "type": str(o.account_type)})


	accountName, accountType = check_account(accountArray, parentId)

	if(accountName):
		if tempDict:

			for l in tempDict:

				if( str(accountName) != str(l['fieldname'])):

					isCoulmn = True
		else:
			isCoulmn = True

		if isCoulmn:

			if setParticulars:

				for n in setParticulars:
					
					if (str(n) == str(accountName)):

						account_exist = False

						returnTotal = 0.0

						isDuplicate =  False
						ifParticulars = False

						my_sql = "SELECT * FROM  `tabJournal Entry Account` WHERE parent = '"+str(parentId)+"' and account = '"+str(accountName)+"'"

						getAccountWise = frappe.db.sql(my_sql, as_dict=True)
						if getAccountWise:

							for k in getAccountWise:

								if (k['debit'] !='' and k['debit'] !=None):

									returnTotal = returnTotal + float(k['debit'])

								if (k['credit'] !='' and k['credit'] !=None):

									returnTotal = returnTotal + float(k['credit'])

						return str(n),returnTotal, isDuplicate

			if ifParticulars:

				account_exist = False

				returnTotal = 0.0

				my_sql = "SELECT * FROM  `tabJournal Entry Account` WHERE parent = '"+str(parentId)+"' and account = '"+str(accountName)+"'"
				getAccountWise = frappe.db.sql(my_sql, as_dict=True)
				if getAccountWise:

					for j in getAccountWise:

						if (j['debit'] !='' and j['debit'] !=None):

							returnTotal = returnTotal + float(j['debit'])

						if (j['credit'] !='' and j['credit'] !=None):

							returnTotal = returnTotal + float(j['credit'])

				return str(accountName),returnTotal, isDuplicate

	if(account_exist):

		return str(''),'', isDuplicate



def check_account(account = [], parentId=''):

	tempCount = 0

	account_type_list = ['Payable', 'Bank', 'Expense Account', 'Cash', 'Receivable']

	account_type = ['Creditors for Service - SLPL', 'Petty Cash - SLPL']

	if account:

		for n in account:

			accountType = '-'

			if(str(n['account']) == str(account_type[0])):

				if str(n['type']) =='' or str(n['type']) ==None:
					accountType = '-'

				return str(n['account']), str(accountType)

		for i in account_type_list:

			tempCount = tempCount +1

			for j in account:

				if (str(j['type']) !='' and str(j['type']) !=None):


					if str(i) == str(j['type']):

						return str(j['account']), str(j['type'])

			if (tempCount ==5):

				for k in account_type:

					for l in account:

						accountType = '-'

						if str(k)== str(l['account']):

							if str(j['type']) =='' or str(j['type']) ==None:

								accountType = '-'

							return str(l['account']), str(accountType)

		return '', ''










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
			"label": _("Address"),
			"fieldname": "address",
			"width": 100
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
			"label": _("Remarks"),
			"fieldname": "remark",
			"width": 400
		},
		{
			"label": _("Ref No."),
			"fieldname": "bill_no",
			"width": 100
		},
		{
			"label": _("Ref Date"),
			"fieldname": "bill_date",
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
			"fieldname": "created_by_whom",
			"width": 90
		},
		{
			"label": _("Modified by whom"),
			"fieldname": "modified_by_whom",
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
