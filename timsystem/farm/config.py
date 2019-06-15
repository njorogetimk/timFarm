class Base():
    SECRET_KEY = '12343'


class Dev(Base):
    DEBUG = True


class Production(Base):
    DEBUG = False
