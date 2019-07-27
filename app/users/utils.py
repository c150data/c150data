from app.db_models import User
from app import mail
from flask import url_for
from flask_mail import Message

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
        sender='lwtpoodles150@gmail.com', 
        recipients=[user.email])
    # Format of this is important or tabs will be shown in the email
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made. 
'''
    mail.send(msg)