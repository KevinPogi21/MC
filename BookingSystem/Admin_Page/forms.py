# BookingSystem/Admin_Page/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from BookingSystem.models import User  # Ensure User model is imported correctly


# Define custom validators
def UppercaseValidator(form, field):
    """Validates that the field contains at least one uppercase letter."""
    if not any(char.isupper() for char in field.data):
        raise ValidationError('Password must contain at least one uppercase letter.')

def LowercaseValidator(form, field):
    """Validates that the field contains at least one lowercase letter."""
    if not any(char.islower() for char in field.data):
        raise ValidationError('Password must contain at least one lowercase letter.')

def DigitalValidator(form, field):
    """Validates that the field contains at least one digit."""
    if not any(char.isdigit() for char in field.data):
        raise ValidationError('Password must contain at least one digit.')

def SpecialCharacterValidator(form, field):
    """Validates that the field contains at least one special character."""
    if not any(char in "!@#$%^&*()_+-=[]{}|;':,.<>?/" for char in field.data):
        raise ValidationError('Password must contain at least one special character.')



# Define the form
class UserTourOperatorForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=6, max=300)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long.'),
        UppercaseValidator,
        LowercaseValidator,
        DigitalValidator,
        SpecialCharacterValidator
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    municipal = StringField('Municipal', validators=[DataRequired()])
    submit = SubmitField('Create Account')

    def validate_email(self, email):
        tour_operator = User.query.filter_by(email=email.data).first()
        if tour_operator:
            raise ValidationError('That email is already in use. Please choose a different one.')
