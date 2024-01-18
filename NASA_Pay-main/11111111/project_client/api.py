from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

COINGECKO_API_BASE = 'https://api.coingecko.com/api/v3'

def get_historical_data_paginated(crypto_name, page=1, per_page=10):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 2)

        url = f'{COINGECKO_API_BASE}/coins/{crypto_name}/market_chart'
        params = {'vs_currency': 'usd', 'from': int(start_date.timestamp()), 'to': int(end_date.timestamp()), 'interval': 'daily'}
        response = requests.get(url, params=params)

        response.raise_for_status()  # Raise an error for bad responses

        data = response.json()
        prices = data.get('prices', [])

        total_items = len(prices)
        start = (page - 1) * per_page
        end = start + per_page

        paginated_data = prices[start:end]

        dates = [datetime.utcfromtimestamp(price[0] / 1000) for price in paginated_data]
        values = [price[1] for price in paginated_data]

        pagination = Pagination(page=page, per_page=per_page, total=total_items, css_framework='bootstrap4')

        return dates, values, pagination
    except requests.RequestException as e:
        print(f"Error fetching paginated historical data: {e}")
        return None, None, None

@app.route('/')
def index():
    try:
        crypto_name = request.args.get('crypto', default=None)
        page = request.args.get(get_page_parameter(), type=int, default=1)

        cryptocurrencies = ['bitcoin', 'ethereum', 'ripple', 'litecoin', 'cardano', 'polkadot', 'stellar', 'chainlink',
                            'dogecoin', 'binancecoin', 'usd-coin', 'uniswap', 'wrapped-bitcoin', 'bitcoin-cash',
                            'ethereum-classic', 'vechain', 'tezos', 'eos', 'aave', 'maker', 'cosmos', 'tron', 'neo', 'dash',
                            'monero', 'zcash', 'theta', 'filecoin', 'decred', 'nano']

        url = f'{COINGECKO_API_BASE}/simple/price'
        params = {'ids': ','.join(cryptocurrencies), 'vs_currencies': 'usd'}
        response = requests.get(url, params=params)

        response.raise_for_status() # Raise an error for bad responses

        data = response.json()

        prices = {}
        historical_data = None
        pagination = None

        if crypto_name and crypto_name in cryptocurrencies:
            prices[crypto_name] = data[crypto_name]['usd']
            historical_data, _, pagination = get_historical_data_paginated(crypto_name, page=page)

        return render_template('index.html', prices=prices, historical_data=historical_data, pagination=pagination)
    except requests.RequestException as e:
        return render_template('error.html', error_message=f"Error fetching data: {e}")


