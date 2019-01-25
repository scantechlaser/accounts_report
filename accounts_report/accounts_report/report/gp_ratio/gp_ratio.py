# Copyright (c) 2013, Scantechalaser.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
from past.builtins import cmp
import functools
from frappe import _
from frappe.utils import flt, cint
from erpnext.accounts.report.utils import get_currency, convert_to_presentation_currency
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import (flt, getdate, get_first_day, add_months, add_days, formatdate)
from datetime import *


def execute(filters=None):

	temp = []
	data = []
	temp_dict = {}
	working_capital = 0
	period_list = get_period_list(filters.from_date, filters.to_date,
		filters.periodicity, company=filters.company)

	income = get_data(filters.company, "Income", "Credit", period_list, filters = filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)

	expense = get_data(filters.company, "Expense", "Debit", period_list, filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)

	net_profit_loss = get_net_profit_loss(income, expense, period_list, filters.company, filters.presentation_currency)

	for k in income:

		if k['account_name'] == 'Direct Income':

			k['account_name'] = 'Sales Accounts'
			temp.append(k)
			break

	for l in expense:

		if l['account_name'] == 'Stock Expenses':
			l['account_name'] = 'Purchase Accounts'
			temp.append(l)
			break

	asset = get_data(filters.company, "Asset", "Debit", period_list,
		only_current_fiscal_year=False, filters=filters,
		accumulated_values=filters.accumulated_values)

	for i in asset:

		if 'account_name' in i:

			if i['account_name'] == 'Current Assets':

				i['parent_account'] = ''
				# working_capital = i['total']

				temp.append(i)

			if i['account_name'] == 'Stock Assets':

				i['account_name'] = 'Stock-in-Hand '
				temp.append(i)

			if i['account_name'] == 'Accounts Receivable':

				i['account_name'] = 'Sundry Debtors'
				i['parent_account'] = ''
				temp.append(i)

			if i['account_name'] == 'Cash In Hand':

				i['parent_account'] = ''
				temp.append(i)


			if i['account_name'] == 'Bank Accounts':

				i['parent_account'] = ''
				temp.append(i)


	liability = get_data(filters.company, "Liability", "Credit", period_list,
		only_current_fiscal_year=False, filters=filters,
		accumulated_values=filters.accumulated_values)

	for j in liability:

		if j['account_name'] == 'Current Liabilities':

			j['parent_account'] = ''

			temp.append(j)


		if j['account_name'] == 'Accounts Payable':

			j['account_name'] = 'Sundry Creditors'

			j['parent_account'] = ''

			temp.append(j)


		if j['account_name'] == 'Loans & Liabilities':

			j['parent_account'] = ''
			temp.append(j)

			break
		

	equity = get_data(filters.company, "Equity", "Credit", period_list,
		only_current_fiscal_year=False, filters=filters,
		accumulated_values=filters.accumulated_values)

		
	provisional_profit_loss, total_credit = get_provisional_profit_loss(asset, liability, equity,
		period_list, filters.company)

	message, opening_balance = check_opening_balance(asset, liability, equity)


	temp_dict = {'account':'','account_name':'Working Capital (Current Assets-Current Liabilities)','currency':'INR'}
	for period in period_list:

		for i in temp:

			if str(i['account_name']) == 'Current Assets':

				temp_dict[""+period.key+""] = i[""+period.key+""]

				if i[""+period.key+""] < 0:

					temp_dict['warn_if_negative'] = True
					temp_dict['has_value'] = True

			if str(l['account_name']) == 'Current Liabilities':

				temp_dict[""+period.key+""] = temp_dict[""+period.key+""] - l[""+period.key+""]

				if l[""+period.key+""] < 0:

					temp_dict['warn_if_negative'] = True
	# b = reducedfraction(2.5)
		
	temp.append(temp_dict)

	net_profit_loss['account_name'] = 'Nett Profit'

	temp.append(net_profit_loss)


	data.extend(temp or [])

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, company=filters.company)

	chart = get_chart_data(filters, columns, asset, liability, equity)

	return columns, data, message, chart


def reducedfraction(d): 
  
    # function that converts a rational number 
    # to the reduced fraction 
    b = d.as_integer_ratio() 
  
    # reduced the list that contains the fraction 
    return b  



def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
	total = 0
	net_profit_loss = {
		"account_name": "'" + _("Profit for the year") + "'",
		"account": "'" + _("Profit for the year") + "'",
		"warn_if_negative": True,
		"currency": currency or frappe.get_cached_value('Company',  company,  "default_currency")
	}

	has_value = False

	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[-2][key], 3) if income else 0
		total_expense = flt(expense[-2][key], 3) if expense else 0

		net_profit_loss[key] = total_income - total_expense

		if net_profit_loss[key]:
			has_value=True

		total += flt(net_profit_loss[key])
		net_profit_loss["total"] = total

	if has_value:
		return net_profit_loss


def get_provisional_profit_loss(asset, liability, equity, period_list, company):
	provisional_profit_loss = {}
	total_row = {}
	if asset and (liability or equity):
		total = total_row_total=0
		currency = frappe.db.get_value("Company", company, "default_currency")
		total_row = {
			"account_name": "'" + _("Total (Credit)") + "'",
			"account": "'" + _("Total (Credit)") + "'",
			"warn_if_negative": True,
			"currency": currency
		}
		has_value = False

		for period in period_list:
			effective_liability = 0.0
			if liability:
				effective_liability += flt(liability[-2].get(period.key))
			if equity:
				effective_liability += flt(equity[-2].get(period.key))

			provisional_profit_loss[period.key] = flt(asset[-2].get(period.key)) - effective_liability
			total_row[period.key] = effective_liability + provisional_profit_loss[period.key]

			if provisional_profit_loss[period.key]:
				has_value = True

			total += flt(provisional_profit_loss[period.key])
			provisional_profit_loss["total"] = total

			total_row_total += flt(total_row[period.key])
			total_row["total"] = total_row_total

		if has_value:
			provisional_profit_loss.update({
				"account_name": "'" + _("Provisional Profit / Loss (Credit)") + "'",
				"account": "'" + _("Provisional Profit / Loss (Credit)") + "'",
				"warn_if_negative": True,
				"currency": currency
			})

	return provisional_profit_loss, total_row

def check_opening_balance(asset, liability, equity):
	# Check if previous year balance sheet closed
	opening_balance = 0
	float_precision = cint(frappe.db.get_default("float_precision")) or 2
	if asset:
		opening_balance = flt(asset[0].get("opening_balance", 0), float_precision)
	if liability:
		opening_balance -= flt(liability[0].get("opening_balance", 0), float_precision)
	if equity:
		opening_balance -= flt(equity[0].get("opening_balance", 0), float_precision)

	opening_balance = flt(opening_balance, float_precision)
	if opening_balance:
		return _("Previous Financial Year is not closed"),opening_balance
	return None,None

def get_chart_data(filters, columns, asset, liability, equity):
	labels = [d.get("label") for d in columns[2:]]

	asset_data, liability_data, equity_data = [], [], []

	for p in columns[2:]:
		if asset:
			asset_data.append(asset[-2].get(p.get("fieldname")))
		if liability:
			liability_data.append(liability[-2].get(p.get("fieldname")))
		if equity:
			equity_data.append(equity[-2].get(p.get("fieldname")))

	datasets = []
	if asset_data:
		datasets.append({'name':'Assets', 'values': asset_data})
	if liability_data:
		datasets.append({'name':'Liabilities', 'values': liability_data})
	if equity_data:
		datasets.append({'name':'Equity', 'values': equity_data})

	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}

	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	return chart


def get_period_list(from_fiscal_year, to_fiscal_year, periodicity, accumulated_values=False,
	company=None, reset_period_on_fy_change=True):
	"""Get a list of dict {"from_date": from_date, "to_date": to_date, "key": key, "label": label}
		Periodicity can be (Yearly, Quarterly, Monthly)"""

	# fiscal_year = get_fiscal_year_data(from_fiscal_year, to_fiscal_year)
	# validate_fiscal_year(fiscal_year, from_fiscal_year, to_fiscal_year)

	# start with first day, so as to avoid year to_dates like 2-April if ever they occur]
	# year_start_date = from_fiscal_year.date()
	fmt = "%Y-%m-%d"
	year_start_date = datetime.strptime(from_fiscal_year, fmt).date()
	year_end_date = datetime.strptime(to_fiscal_year, fmt).date()
	# year_end_date = to_fiscal_year.date()

	months_to_add = {
		"Yearly": 12,
		"Half-Yearly": 6,
		"Quarterly": 3,
		"Monthly": 1
	}[periodicity]

	period_list = []

	start_date = year_start_date
	months = get_months(year_start_date, year_end_date)

	for i in range(months // months_to_add):
		period = frappe._dict({
			"from_date": start_date
		})

		to_date = add_months(start_date, months_to_add)
		start_date = to_date

		if to_date == get_first_day(to_date):
			# if to_date is the first day, get the last day of previous month
			to_date = add_days(to_date, -1)

		if to_date <= year_end_date:
			# the normal case
			period.to_date = to_date
		else:
			# if a fiscal year ends before a 12 month period
			period.to_date = year_end_date

		period.to_date_fiscal_year = get_fiscal_year(period.to_date, company=company)[0]
		period.from_date_fiscal_year_start_date = get_fiscal_year(period.from_date, company=company)[1]

		period_list.append(period)

		if period.to_date == year_end_date:
			break

	# common processing
	for opts in period_list:
		key = opts["to_date"].strftime("%b_%Y").lower()
		if periodicity == "Monthly" and not accumulated_values:
			label = formatdate(opts["to_date"], "MMM YYYY")
		else:
			if not accumulated_values:
				label = get_label(periodicity, opts["from_date"], opts["to_date"])
			else:
				if reset_period_on_fy_change:
					label = get_label(periodicity, opts.from_date_fiscal_year_start_date, opts["to_date"])
				else:
					label = get_label(periodicity, period_list[0].from_date, opts["to_date"])

		opts.update({
			"key": key.replace(" ", "_").replace("-", "_"),
			"label": label,
			"year_start_date": year_start_date,
			"year_end_date": year_end_date
		})

	return period_list


def get_fiscal_year_data(from_fiscal_year, to_fiscal_year):
	fiscal_year = frappe.db.sql("""select min(year_start_date) as year_start_date,
		max(year_end_date) as year_end_date from `tabFiscal Year` where
		name between %(from_fiscal_year)s and %(to_fiscal_year)s""",
		{'from_fiscal_year': from_fiscal_year, 'to_fiscal_year': to_fiscal_year}, as_dict=1)

	return fiscal_year[0] if fiscal_year else {}


def validate_fiscal_year(fiscal_year, from_fiscal_year, to_fiscal_year):
	if not fiscal_year.get('year_start_date') and not fiscal_year.get('year_end_date'):
		frappe.throw(_("End Year cannot be before Start Year"))


def get_months(start_date, end_date):
	diff = (12 * end_date.year + end_date.month) - (12 * start_date.year + start_date.month)
	return diff + 1


def get_label(periodicity, from_date, to_date):
	if periodicity == "Yearly":
		if formatdate(from_date, "YYYY") == formatdate(to_date, "YYYY"):
			label = formatdate(from_date, "YYYY")
		else:
			label = formatdate(from_date, "YYYY") + "-" + formatdate(to_date, "YYYY")
	else:
		label = formatdate(from_date, "MMM YY") + "-" + formatdate(to_date, "MMM YY")

	return label


def get_data(
		company, root_type, balance_must_be, period_list, filters=None,
		accumulated_values=1, only_current_fiscal_year=True, ignore_closing_entries=False,
		ignore_accumulated_values_for_fy=False):

	accounts = get_accounts(company, root_type)
	if not accounts:
		return None

	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

	company_currency = get_appropriate_currency(company, filters)

	gl_entries_by_account = {}
	for root in frappe.db.sql("""select lft, rgt from tabAccount
			where root_type=%s and ifnull(parent_account, '') = ''""", root_type, as_dict=1):

		set_gl_entries_by_account(
			company,
			period_list[0]["year_start_date"] if only_current_fiscal_year else None,
			period_list[-1]["to_date"],
			root.lft, root.rgt, filters,
			gl_entries_by_account, ignore_closing_entries=ignore_closing_entries
		)

	calculate_values(
		accounts_by_name, gl_entries_by_account, period_list, accumulated_values, ignore_accumulated_values_for_fy)
	accumulate_values_into_parents(accounts, accounts_by_name, period_list, accumulated_values)
	out = prepare_data(accounts, balance_must_be, period_list, company_currency)
	out = filter_out_zero_value_rows(out, parent_children_map)

	if out:
		add_total_row(out, root_type, balance_must_be, period_list, company_currency)

	return out


def get_appropriate_currency(company, filters=None):
	if filters and filters.get("presentation_currency"):
		return filters["presentation_currency"]
	else:
		return frappe.db.get_value("Company", company, "default_currency")


def calculate_values(
		accounts_by_name, gl_entries_by_account, period_list, accumulated_values, ignore_accumulated_values_for_fy):
	for entries in gl_entries_by_account.values():
		for entry in entries:
			d = accounts_by_name.get(entry.account)
			if not d:
				frappe.msgprint(
					_("Could not retrieve information for {0}.".format(entry.account)), title="Error",
					raise_exception=1
				)
			for period in period_list:
				# check if posting date is within the period

				if entry.posting_date <= period.to_date:
					if (accumulated_values or entry.posting_date >= period.from_date) and \
						(not ignore_accumulated_values_for_fy or
							entry.fiscal_year == period.to_date_fiscal_year):
						d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)

			if entry.posting_date < period_list[0].year_start_date:
				d["opening_balance"] = d.get("opening_balance", 0.0) + flt(entry.debit) - flt(entry.credit)


def accumulate_values_into_parents(accounts, accounts_by_name, period_list, accumulated_values):
	"""accumulate children's values in parent accounts"""
	for d in reversed(accounts):
		if d.parent_account:
			for period in period_list:
				accounts_by_name[d.parent_account][period.key] = \
					accounts_by_name[d.parent_account].get(period.key, 0.0) + d.get(period.key, 0.0)

			accounts_by_name[d.parent_account]["opening_balance"] = \
				accounts_by_name[d.parent_account].get("opening_balance", 0.0) + d.get("opening_balance", 0.0)


def prepare_data(accounts, balance_must_be, period_list, company_currency):
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")

	for d in accounts:
		# add to output
		has_value = False
		total = 0
		row = frappe._dict({
			"account_name": _(d.account_name),
			"account": _(d.name),
			"parent_account": _(d.parent_account),
			"year_start_date": year_start_date,
			"year_end_date": year_end_date,
			"currency": company_currency,
			"opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be == "Debit" else -1)
		})
		for period in period_list:
			if d.get(period.key) and balance_must_be == "Credit":
				# change sign based on Debit or Credit, since calculation is done using (debit - credit)
				d[period.key] *= -1

			row[period.key] = flt(d.get(period.key, 0.0), 3)

			if abs(row[period.key]) >= 0.005:
				# ignore zero values
				has_value = True
				total += flt(row[period.key])

		row["has_value"] = has_value
		row["total"] = total
		data.append(row)

	return data


def filter_out_zero_value_rows(data, parent_children_map, show_zero_values=False):
	data_with_value = []
	for d in data:
		if show_zero_values or d.get("has_value"):
			data_with_value.append(d)
		else:
			# show group with zero balance, if there are balances against child
			children = [child.name for child in parent_children_map.get(d.get("account")) or []]
			if children:
				for row in data:
					if row.get("account") in children and row.get("has_value"):
						data_with_value.append(d)
						break

	return data_with_value


def add_total_row(out, root_type, balance_must_be, period_list, company_currency):
	total_row = {
		"account_name": "'" + _("Total {0} ({1})").format(_(root_type), _(balance_must_be)) + "'",
		"account": "'" + _("Total {0} ({1})").format(_(root_type), _(balance_must_be)) + "'",
		"currency": company_currency
	}

	for row in out:
		if not row.get("parent_account"):
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)
				row[period.key] = 0.0

			total_row.setdefault("total", 0.0)
			total_row["total"] += flt(row["total"])
			row["total"] = ""

	if "total" in total_row:
		out.append(total_row)

		# blank row after Total
		out.append({})


def get_accounts(company, root_type):
	return frappe.db.sql(
		"""select name, parent_account, lft, rgt, root_type, report_type, account_name from `tabAccount`
		where company=%s and root_type=%s order by lft""", (company, root_type), as_dict=True)


def filter_accounts(accounts, depth=10):
	parent_children_map = {}
	accounts_by_name = {}
	for d in accounts:
		accounts_by_name[d.name] = d
		parent_children_map.setdefault(d.parent_account or None, []).append(d)

	filtered_accounts = []

	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			sort_accounts(children, is_root=True if parent==None else False)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)

	add_to_list(None, 0)

	return filtered_accounts, accounts_by_name, parent_children_map


def sort_accounts(accounts, is_root=False, key="name"):
	"""Sort root types as Asset, Liability, Equity, Income, Expense"""

	def compare_accounts(a, b):
		if is_root:
			if a.report_type != b.report_type and a.report_type == "Balance Sheet":
				return -1
			if a.root_type != b.root_type and a.root_type == "Asset":
				return -1
			if a.root_type == "Liability" and b.root_type == "Equity":
				return -1
			if a.root_type == "Income" and b.root_type == "Expense":
				return -1
		else:
			if re.split('\W+', a[key])[0].isdigit():
				# if chart of accounts is numbered, then sort by number
				return cmp(a[key], b[key])
		return 1

	accounts.sort(key = functools.cmp_to_key(compare_accounts))

def set_gl_entries_by_account(
		company, from_date, to_date, root_lft, root_rgt, filters, gl_entries_by_account, ignore_closing_entries=False):
	"""Returns a dict like { "account": [gl entries], ... }"""

	additional_conditions = get_additional_conditions(from_date, ignore_closing_entries, filters)

	gl_entries = frappe.db.sql("""select posting_date, account, debit, credit, is_opening, fiscal_year, debit_in_account_currency, credit_in_account_currency, account_currency from `tabGL Entry`
		where company=%(company)s
		{additional_conditions}
		and posting_date <= %(to_date)s
		and account in (select name from `tabAccount`
			where lft >= %(lft)s and rgt <= %(rgt)s)
		order by account, posting_date""".format(additional_conditions=additional_conditions),
		{
			"company": company,
			"from_date": from_date,
			"to_date": to_date,
			"lft": root_lft,
			"rgt": root_rgt
		},
		as_dict=True)

	if filters and filters.get('presentation_currency'):
		convert_to_presentation_currency(gl_entries, get_currency(filters))

	for entry in gl_entries:
		gl_entries_by_account.setdefault(entry.account, []).append(entry)

	return gl_entries_by_account


def get_additional_conditions(from_date, ignore_closing_entries, filters):
	additional_conditions = []

	if ignore_closing_entries:
		additional_conditions.append("ifnull(voucher_type, '')!='Period Closing Voucher'")

	if from_date:
		additional_conditions.append("posting_date >= %(from_date)s")

	if filters:
		if filters.get("project"):
			additional_conditions.append("project = '%s'" % (frappe.db.escape(filters.get("project"))))
		if filters.get("cost_center"):
			additional_conditions.append(get_cost_center_cond(filters.get("cost_center")))

	return " and {}".format(" and ".join(additional_conditions)) if additional_conditions else ""


def get_cost_center_cond(cost_center):
	lft, rgt = frappe.db.get_value("Cost Center", cost_center, ["lft", "rgt"])
	return """ cost_center in (select name from `tabCost Center` where lft >=%s and rgt <=%s)""" % (lft, rgt)


def get_columns(periodicity, period_list, accumulated_values=1, company=None):
	columns = [{
		"fieldname": "account",
		"label": _("Account"),
		"fieldtype": "Link",
		"options": "Account",
		"width": 300
	}]
	if company:
		columns.append({
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		})
	for period in period_list:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"options": "currency",
			"width": 150
		})
	if periodicity!="Yearly":
		if not accumulated_values:
			columns.append({
				"fieldname": "total",
				"label": _("Total"),
				"fieldtype": "Currency",
				"width": 150
			})

	return columns
