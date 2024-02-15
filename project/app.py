from flask import url_for, redirect, render_template, flash, request
from flask_login import LoginManager, login_user, login_required
from controllers import add_object_to_database, get_all_cars
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from mail import send_reset_email, send_verify_email, verification_code
from forms import RequestResetForm, ResetPasswordForm
from models import User, Car, Image, session
from create_app import app
from create_admin import admin_email

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = 'supersecretkey'

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        model_name = request.form.get('model-name')
        colors = request.form.get('colors')
        price = request.form.get('price')
        desc = request.form.get('description')

        car = Car(model=model_name, price=price, description=desc, colors=colors)
        err = add_object_to_database(car)
        if err:
            flash('Error occurred while adding the car to the database')

        pic = request.files.get('pic')

        if pic:
            filename = secure_filename(pic.filename)
            mimetype = pic.mimetype

            image = Image(img=pic.read(), mimetype=mimetype, name=filename)
            add_object_to_database(image)
        else:
            flash('No pic uploaded')

        return redirect(url_for('admin'))

    return render_template('admin.html')


@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(user_id)


@app.route('/main')
@login_required
def main():
    cars = get_all_cars()
    return render_template('main.html', cars=cars)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        user = session.query(User).filter_by(email=email).first()

        if user:
            flash('This user already exists.')
            return redirect(url_for('signup'))

        password = request.form.get('password1')
        confirmed_password = request.form.get('password2')

        if not password == confirmed_password:
            flash('Passwords do not match(')
            return redirect(url_for('signup'))

        finished_password = generate_password_hash(password)

        user = User(name, email, finished_password)

        err = add_object_to_database(user)
        if not err:
            send_verify_email(user)
            return redirect('verification')

    return render_template('signup.html')


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

        if email == admin_email:
            login_user(user)
            return redirect(url_for('admin'))

        login_user(user)
        return redirect(url_for('main'))

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


@app.route('/verification', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        entered_code = request.form.get('code')
        if entered_code == verification_code:
            flash('Success!')
            return redirect('login')

    return render_template("verification.html")