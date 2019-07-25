import os


class Base():
    Kkey = 'c9b06027439ee6061004a982b41a714965cad7534a7b40f7'
    SECRET_KEY = os.environ['SECRET_KEY'] or Kkey
    WTF_CSRF_SECRET_KEY = SECRET_KEY

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = ('timsystem', MAIL_USERNAME)


class Dev(Base):
    DEBUG = True
    protocol = 'postgresql://postgres:'
    password = 'Kinsman.'
    host = '@localhost'
    dbase = '/timfarm'
    SQLALCHEMY_DATABASE_URI = protocol+password+host+dbase


class Testing():
    SECRET_KEY = '12'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Production(Base):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
