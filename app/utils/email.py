from flask_mail import Message
from flask import render_template, current_app
from threading import Thread
from app import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipient, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject, recipients=[recipient])
    msg.html = render_template(template + '.html', **kwargs)
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_token()
    send_email(
        'Reset Your Password',
        user.email,
        'email/reset_password',
        user=user,
        token=token
    )
