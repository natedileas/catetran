import re


STMT2VENDOR = {
	re.compile(r'(.*) (?:[\d-]{10,13})'): None,
	re.compile(r'(?:POS MAC|POS EXA) ((?:.+)+) (?:ROCHESTER NY|AMHERST NY)'): None,
	re.compile(r'(.*) (?:ROCHESTER )(?:[A-Z]{2} USA)'): None,
	re.compile(r'(.*) (?:[A-Z]{2} USA)'): None,
}


VENDOR2CAT = {
	'THE HOME DEPOT': 'Home Improvement',
	'TARGET': 'Shopping',
	'SPECTRUM': 'Bills/Internet',
	'WEGMANS': 'Food/Groceries',
	'SOL BURRITO': 'Food/Restaurants',
	'GRUBHUB': 'Food/Fast Food',
	'DOORDASH': 'Food/Fast Food',
	'BALSAM BAG': 'Food/Fast Food',
	'COZY': 'Rent',
	'AMTRAK': 'Travel',
	'HOTELS': 'Travel',
	'GEICO': 'Transport/Car Insurance',
	'UBER': 'Transport/Taxi',
	'SUNOCO': 'Transport/Gas',
	'SPEEDWAY': 'Transport/Gas',
	'DIRECT DEPOSIT': 'Paycheck',
	'STITCH FIX': 'Clothes',
}


def convert_statements(invalue):
	for (rulein, ruleout) in STMT2VENDOR.items():
		if re.match(rulein, invalue):
			return ' '.join(re.match(rulein, invalue).groups())

	return invalue


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
		df = pd.read_csv(filepath, header=1)
		df = apply_categorizations(df)
		dfs = df if dfs is None else pd.merge(dfs, df)

	dfs.to_csv(sys.argv[-1])