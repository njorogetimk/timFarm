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


class Dev(Base):
    DEBUG = True
    protocol = 'postgresql://postgres:'
    password = 'Kinsman.'
    host = '@localhost'
    dbase = '/timfarm'
    SQLALCHEMY_DATABASE_URI = protocol+password+host+dbase

    MAIL_USERNAME = 'timdevtesting@gmail.com'
    MAIL_PASSWORD = 'enterinto'
    MAIL_DEFAULT_SENDER = ('timsystem', MAIL_USERNAME)


class Production(Base):
    DEBUG = False
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']
    # WTF_CRFS_SECRET_KEY = SECRET_KEY

    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = ('timsystem', MAIL_USERNAME)
