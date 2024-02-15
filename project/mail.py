from flask import url_for
from flask_mail import Mail, Message
from create_app import app
import string, random

IMAP_PASSWORD = 'U3chxg9V60Tsuxvl'
app.config['MAIL_SERVER'] = "smtp.ukr.net"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'andriybalanda2008@ukr.net'
app.config['MAIL_PASSWORD'] = IMAP_PASSWORD
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
MAIL_EMAIL = 'andriybalanda2008@ukr.net'

mail = Mail(app)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=MAIL_EMAIL,
                  recipients=[user.email])
    msg.body = (f"To reset your password, visit the following link:"
                f"{url_for('reset_token', token=token, _external=True)}")
    mail.send(msg)
    print(1)


def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


verification_code = generate_code()


def send_verify_email(user):
    message = Message('Verification code',
                      sender=MAIL_EMAIL,
                      recipients=[user.email])
    message.body = f'Your verification code: {verification_code}'

    mail.send(message)