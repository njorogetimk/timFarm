from flask_mail import Message
from threading import Thread
from timsystem import mail, app


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template):
    msg = Message(
        subject, recipients=[to], html=template
    )
    thrd = Thread(target=send_async_email, args=[app, msg])
    thrd.start()
    return thrd
