from flask_wtf import FlaskForm
from models import User, session
from wtforms.validators import ValidationError
from wtforms import PasswordField, SubmitField, EmailField, validators


class RequestResetForm(FlaskForm):
    email = EmailField('Email', [validators.DataRequired()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = session.query(User).filter(User.email == email.data).first()
        if user is None:
            raise ValidationError('There is no user with this email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', [validators.DataRequired()])
    confirm_password = PasswordField('Confirm password', [validators.DataRequired()])
    submit = SubmitField('Reset Password')