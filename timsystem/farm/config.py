import os


class Base():
    SECRET_KEY = 'c9b06027439ee6061004a982b41a714965cad7534a7b40f7'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CRFS_SECRET_KEY = SECRET_KEY


class Dev(Base):
    DEBUG = True
    protocol = 'postgresql://postgres:'
    password = 'Kinsman.'
    host = '@localhost'
    dbase = '/timfarm'
    SQLALCHEMY_DATABASE_URI = protocol+password+host+dbase


class Production():
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    WTF_CRFS_SECRET_KEY = SECRET_KEY
