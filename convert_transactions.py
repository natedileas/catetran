""" Copyright 2019, Nathan Dileas
"""
import re
import json

import pandas as pd


USA_STATES = pd.read_csv('./data/state_abbrevs.csv')
USA_STATES.index = USA_STATES.State
USA_STATE_COUNTRY = '|'.join((code + ' USA' for code in USA_STATES.Postal_Code.to_list()))

USA_CITIES = json.load(open('./data/us-cities-towns-wiki.json', 'r'))
USA_CITY_STATE = '|'.join((
	'{} {}'.format(city.upper(), USA_STATES.Postal_Code[USA_STATES.State == state].values[0]).strip() 
	for state in USA_CITIES for city in USA_CITIES[state]))

STRIP_RE = [
	re.compile(r'^(POS MAC|POS EXA|SQU?( \*SQ)?)'),   # processor?
	re.compile(r'\+?[\d\-]{10,14}'),   # phone number
	re.compile(r'({})$'.format(USA_CITY_STATE)),    # City State
	# r'',    # City State Country
	re.compile(r'({})$'.format(USA_STATE_COUNTRY)),    # State Country
	re.compile(r' ({})$'.format('|'.join(USA_STATES.Postal_Code.to_list()))),   # Just the state # FIXME: this doesn't work beacuse it will replace 
]   

# STMT2VENDOR = [
# 	re.compile(r'(.*) (?:)'),
# 	re.compile(r'(?:POS MAC|POS EXA) ((?:.+)+) (?:ROCHESTER NY|AMHERST NY)'),
# 	re.compile(r'(.*) (?:ROCHESTER )(?:[A-Z]{2} ?)(?: USA)?'),
# 	re.compile(r'(.*) (?:[A-Z]{2} USA)'),
# ]

# TODO split this out to a csv or something
VENDOR2CAT = {
	'THE HOME DEPOT': 'Home Improvement',
	'TARGET': 'Shopping',
	'SPECTRUM': 'Bills/Internet',
	'ROCH GAS & ELEC': 'Bills',
	'WEGMANS': 'Food/Groceries',
	'SOL BURRITO': 'Food/Restaurants',
	'THE KING AND I': 'Food/Restaurants',
	'NAAN-TASTIC': 'Food/Restaurants',
	'WONG\'S KITCHEN': 'Food/Restaurants',
	'WONG\'S': 'Food/Restaurants',
	'GRUBHUB': 'Food/Fast Food',
	'DOORDASH': 'Food/Fast Food',
	'BURGER KING': 'Food/Fast Food',
	'BALSAM BAG': 'Food/Fast Food',
	'WENDY\'S': 'Food/Fast Food',
	'ITT SPACE SYSTE': 'Food/Fast Food',
	'SERVOMATION': 'Food/Fast Food',
	'DUNKIN': 'Food/Coffee Shops',
	'TIM HORTONS': 'Food/Coffee Shops',
	'COZY': 'Rent',
	'AMTRAK': 'Travel',
	'HOTELS': 'Travel',
	'GEICO': 'Transport/Car Insurance',
	'UBER': 'Transport/Taxi',
	'SUNOCO': 'Transport/Gas',
	'SPEEDWAY': 'Transport/Gas',
	'EXXONMOBIL': 'Transport/Gas',
	'DIRECT DEPOSIT': 'Paycheck',
	'STITCH FIX': 'Clothes',
	'NINTENDO': 'Entertainment',
}


def convert_statements(invalue):
	val = invalue.strip().upper()

	for rule in STRIP_RE:
		val = re.sub(rule, '', val)

	return val


def convert_vendors(vendor):
	for _vendor, _category in VENDOR2CAT.items():
		if _vendor in vendor:
			return _category

	return None


def apply_categorizations(df):
	df['Vendor'] = df.Description.map(convert_statements)
	df['Categories'] = df.Vendor.map(convert_vendors)

	return df


if __name__ == '__main__':
	import sys
	import pandas as pd

	assert len(sys.argv) >= 3

	dfs = None
	for filepath in sys.argv[1:-1]:
		df = pd.read_csv(filepath, sep=',', header=1, index_col=False)
		df = apply_categorizations(df)
		dfs = df if dfs is None else pd.concat([dfs, df])

	dfs.to_csv(sys.argv[-1])

	# print most common uncategorized vendors
	print('Top 15 Uncategorized Vendors:')
	print(dfs[dfs.Categories.isnull()].Vendor.value_counts()[:15])
	print()
	print('Top 15 Unmodified Transactions:')
	print(dfs[dfs.Description == dfs.Vendor].Vendor.value_counts()[:15])