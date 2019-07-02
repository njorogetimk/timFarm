from flask_mail import Message
from timsystem import mail


def send_email(to, subject, template):
    msg = Message(
        subject, recipients=[to], html=template
    )
    mail.send(msg)
