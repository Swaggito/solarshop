from flask_wtf import FlaskForm
from flask_wtf.file import FileField, MultipleFileField
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL
from wtforms import SubmitField
from flask_login import current_user, login_required
from app.models import Brand, Category, Settings  # Changed from SiteSettings to Settings
from flask import flash, redirect, url_for, render_template
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Register as', choices=[
        ('buyer', 'Buyer/Customer'),
        ('user', 'Regular User')
    ], validators=[DataRequired()])

# app/forms.py

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    brand = SelectField('Brand', coerce=int)
    category = SelectField('Category', coerce=int)
    image1 = FileField('Product Image 1', validators=[DataRequired()])
    image2 = FileField('Product Image 2')
    image3 = FileField('Product Image 3')
    image4 = FileField('Product Image 4')

class BrandForm(FlaskForm):
    name = StringField('Brand Name', validators=[DataRequired()])
    submit = SubmitField('Add Brand')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    image = FileField('Category Image', validators=[DataRequired()])
    submit = SubmitField('Add Category')

class SettingsForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    contact_email = StringField('Contact Email', validators=[DataRequired(), Email()])

class GeneralSettingsForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    site_url = StringField('Site URL', validators=[DataRequired(), URL()])

class ContactSettingsForm(FlaskForm):
    contact_email = StringField('Contact Email', validators=[DataRequired(), Email()])
    sales_email = StringField('Sales Email', validators=[DataRequired(), Email()])
    support_email = StringField('Support Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])

class SMTPSettingsForm(FlaskForm):
    smtp_server = StringField('SMTP Server', validators=[DataRequired()])
    smtp_port = IntegerField('SMTP Port', validators=[DataRequired()])
    smtp_username = StringField('SMTP Username', validators=[DataRequired()])
    smtp_password = PasswordField('SMTP Password', validators=[DataRequired()])
    smtp_use_tls = BooleanField('Use TLS')

class AddressSettingsForm(FlaskForm):
    address_line1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line2 = StringField('Address Line 2')
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State/Province', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password')
    confirm = PasswordField('Confirm Password', validators=[EqualTo('password')])
    is_admin = BooleanField('Administrator')
    admin_access_level = SelectField('Admin Level', choices=[(0, 'User'), (1, 'Admin'), (2, 'Super Admin')], coerce=int)

class CheckoutForm(FlaskForm):
    # Contact Information
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    
    # Shipping Information
    shipping_address = TextAreaField('Shipping Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State/Province', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    
    # Payment Information
    payment_method = SelectField('Payment Method', choices=[
        ('credit_card', 'Credit Card'),
        ('mtn mobile money', 'Mtn mobile money'),
        ('bank_transfer', 'Bank Transfer'),
        ('orange mobile money', 'Orange mobile money'), 
        ('crypto', 'Cryptocurrency'),


            ], validators=[DataRequired()])
    
    # Credit Card Details (shown only if credit card is selected)
    card_number = StringField('Card Number')
    cardholder_name = StringField('Cardholder Name')
    expiry_date = StringField('Expiry Date')
    cvv = StringField('CVV')
    
    # Additional Notes
    order_notes = TextAreaField('Order Notes')

class UserSettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    newsletter = BooleanField('Subscribe to Newsletter')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')