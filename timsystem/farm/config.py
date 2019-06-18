class Base():
    SECRET_KEY = '12343'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Dev(Base):
    DEBUG = True
    protocol = 'postgresql://postgres:'
    password = 'Kinsman.'
    host = '@localhost'
    dbase = '/timfarm'
    SQLALCHEMY_DATABASE_URI = protocol+password+host+dbase


class Production(Base):
    DEBUG = False
