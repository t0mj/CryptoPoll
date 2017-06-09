#!/usr/bin/env python3.6
"""
A utility to update current prices of cryptocurrencies I currently hold.
"""
from decimal import Decimal
import yaml

from CryptoCoinChartsApi import API
from sheets import get_sheet, update_cells


SHEETS = yaml.safe_load(open('config.yml'))
THE_SHEET = SHEETS['Active']

print('Grabbing spreadsheet...\n')
wallets = get_sheet(THE_SHEET['id'], THE_SHEET['range'], as_dict=True)

pairs_to_update = {}

for idx, wallet in enumerate(wallets):
    if not wallet.get('Currency') or wallet.get('Status') == 'SOLD':
        continue
    pairs_to_update[wallet['Currency'].lower()] = {'index': idx, 'curr_rate': wallet['Current Rate']}

# Create a dict of all the currencies and the current rate
# grab all trading pairs that are not sold
# update any that have changed
# Always add LTC/USD and BTC/USD to keep the references updated
pairs = ','.join(pairs_to_update.keys()) + ',LTC/USD,BTC/USD'
api = API()
print('Getting updated currency values...\n')
result = api.tradingpairs(pairs)
data_to_update = []

for currency in result:
    # TODO: Clean this up to only update if a change is needed
    if currency.id == 'ltc/usd':
        data_to_update.append({'range': 'K2', 'values': [[currency.price]]})
        print(f'Updating {currency.id} to {currency.price}')
        continue
    if currency.id == 'btc/usd':
        data_to_update.append({'range': 'L2', 'values': [[currency.price]]})
        print(f'Updating {currency.id} to {currency.price}')
        continue
    record_to_update = pairs_to_update.get(currency.id)
    # TODO: Allow empty cells to not break decimal
    if Decimal(record_to_update['curr_rate']) != Decimal(currency.price):
        # Add 2 for header and 0 index
        print(f'Updating {currency.id} to {currency.price}')
        data_to_update.append({'range': 'D' + str(record_to_update['index'] + 2), 'values': [[currency.price]]})

result = update_cells(THE_SHEET['id'], data_to_update)
print(f"\n{result['totalUpdatedCells']} cells updated.")

# TODO: Add ability to text when ROI is a certain level
