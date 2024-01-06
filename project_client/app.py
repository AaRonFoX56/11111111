from flask import render_template, request, flash, redirect, url_for, abort
from controllers import add_object_to_database
from models import User, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user
import requests
from datetime import datetime, timedelta
from flask_paginate import Pagination, get_page_parameter
from create_app import app
from mail import send_reset_email, send_verify_email, verification_code
from forms import RequestResetForm, ResetPasswordForm

app.config['JSON_SORT_KEYS'] = False

COINGECKO_API_BASE = 'https://api.coingecko.com/api/v3'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


def get_historical_data_paginated(crypto_name, page=1, per_page=10):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 2)

        url = f'{COINGECKO_API_BASE}/coins/{crypto_name}/market_chart'
        params = {'vs_currency': 'usd', 'from': int(start_date.timestamp()), 'to': int(end_date.timestamp()), 'interval': 'daily'}
        response = requests.get(url, params=params)

        response.raise_for_status()

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = session.query(User).filter_by(email=email).first()

        if not user:
            flash('User not found')
            return redirect(url_for('login'))

        is_password_correct = check_password_hash(user.password, password)

        if not is_password_correct:
            flash('Incorrect password')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if request.method == "POST":
        user = session.query(User).filter(User.email == form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect('login')
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    form = ResetPasswordForm()
    if request.method == "POST":
        finished_password = generate_password_hash(form.password.data)
        user.password = finished_password
        session.commit()
        flash('Your password has been updated!')
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        user = session.query(User).filter_by(email=email).first()

        if user:
            flash('This user already exists.')
            return redirect(url_for('signup'))

        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not password1 == password2:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        finished_password = generate_password_hash(password1)

        user = User(name, email, finished_password)

        err = add_object_to_database(user)

        if not err:
            send_verify_email(user)
            return redirect('verification')

    return render_template('signup.html')


@app.route('/verification', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_code = request.form.get('code')
        if entered_code == verification_code:
            flash('Success!')
            return redirect('login')

    return render_template("verification.html")



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

        response.raise_for_status()

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


if __name__ == "__main__":
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
