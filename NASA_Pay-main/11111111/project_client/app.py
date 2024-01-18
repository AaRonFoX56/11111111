from flask import render_template, request, flash, redirect, url_for
from controllers import add_object_to_database, get_user_by_id, change_subscribied_state_to_true
from models import User, UserMessage, session, Base, engine
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
import requests
from create_app import app
from mail import send_reset_email, send_verify_email, verification_code
from forms import RequestResetForm, ResetPasswordForm
import stripe
import json

app.config['JSON_SORT_KEYS'] = False

NASA_API_KEY = 'a3HzNmfXWJP7JHzBVutwPSnaTetSrIpYg6Qh2CI9'

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51OSS1hJxBjL7O6KfNLbRdlUwvko24qZ9jTNSZ2qlxvmvTCISEgHxuip5tGBiFZGAPueM3c259gtEHwNz8iD8bxUd00xDejn5fd'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51OSS1hJxBjL7O6KfETdhhcF6fkZ4Nl6OpA3AZq8xqkwYPZktwdKr1dtrZA5FXkdlLxVBbqvHxCwmoHPPRj72UrZH00TfsPyvIX'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


@app.route('/mars', methods=['GET', 'POST'])
@login_required
def mars():
    if request.method == 'POST':
        sol = request.form['sol']
        camera = request.form['camera']
        url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol={sol}&camera={camera}&api_key={NASA_API_KEY}'
        response = requests.get(url)
        data = response.json()
        photos = data.get('photos', [])

        return render_template('mars_result.html', photos=photos)

    return render_template('mars.html')


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

        user = User(name, email, finished_password, False)

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


@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('login'))


@app.route('/index')
@login_required
def index():
    '''
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1GtKWtIdX0gthvYPm4fJgrOr',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    '''
    return render_template(
        'index.html',
        #checkout_session_id=session['id'],
        #checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
    )

@app.route('/stripe_pay')
@login_required
def stripe_pay():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1OXTYGJxBjL7O6KfUSJ6aUfM',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    change_subscribied_state_to_true(current_user.id)
    return {
        'checkout_session_id': session['id'],
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


@app.route('/stripe_webhook', methods=['POST'])
def stripe_webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'YOUR_ENDPOINT_SECRET'
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items['data'][0]['description'])

    return {}


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/profile')
@login_required
def profile():
    user = get_user_by_id(current_user.id)
    print(user)
    username = user.name
    user_email = user.email
    state = user.subscribied_state
    return render_template('profile.html', username=username, user_email=user_email, state=state)


if __name__ == "__main__":
    app.secret_key = 'your_secret_key'
    Base.metadata.create_all(engine)
    app.run(debug=True)
