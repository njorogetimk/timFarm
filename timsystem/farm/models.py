from timsystem import db
from passlib.hash import pbkdf2_sha256 as phash
from datetime import datetime as dt


global sep
sep = '%$'


class Administrator(db.Model):
    """
    Njoroges Farm Administrator
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    top_level = db.Column(db.Boolean)

    def __init__(self, username, password, top_level=True):
        self.username = username
        self.password = phash.hash(password)
        self.top_level = top_level

    def authenticate(self, passw):
        """
        Authenticate Administrator
        """
        verified = phash.verify(passw, self.password)
        return verified

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


class Farm(db.Model):
    """
    farm_name: Name of the farm
    farm_email: The email of the farm
    """
    id = db.Column(db.Integer, primary_key=True)
    farm_name = db.Column(db.String, unique=True)
    farm_email = db.Column(db.String)
    confirmed = db.Column(db.Boolean)
    pending = db.Column(db.Boolean)

    def __init__(self, farm_name, farm_email, confirmed=False, pending=False):
        self.farm_name = farm_name
        self.farm_email = farm_email
        self.confirmed = confirmed
        self.pending = pending

    def confirm(self):
        self.confirmed = True

    def __repr__(self):
        return '<Farm {}>'.format(self.farm_name)


class Level(db.Model):
    """
    There are levels of the users.
    """
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String, unique=True)

    def __init__(self, level):
        self.level = level

    def __repr__(self):
        return '<Level %s>' % self.level


class Users(db.Model):
    """
    name: Name of the user, Timothy Kinoro
    username: The name identifying the user in the system, njorogetimk
    username_serial: Distinguish users of a given farm
    email: Email of the user
    password: User's password
    level: Admin or not
    farm_name: Farm associated with the user
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    username = db.Column(db.String)
    username_serial = db.Column(db.String, unique=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    confirmed = db.Column(db.Boolean)
    Level = db.relationship(
        'Level', backref=db.backref('users', lazy='dynamic')
    )
    level = db.Column(db.String, db.ForeignKey('level.level'))
    farm = db.relationship('Farm', backref=db.backref('users', lazy='dynamic'))
    farm_name = db.Column(db.String, db.ForeignKey('farm.farm_name'))

    def __init__(
        self, name, username, email, password, farm_name, level,
        confirmed=False
    ):
        self.name = name
        self.username = username
        self.username_serial = username+sep+farm_name
        self.email = email
        self.password = phash.hash(password)
        self.confirmed = confirmed
        self.Level = Level.query.filter_by(level=level).first()
        self.farm = Farm.query.filter_by(farm_name=farm_name).first()

    def confirm(self):
        self.confirmed = True

    def authenticate(self, passw):
        """
        Authenticate a user
        """
        verified = phash.verify(passw, self.password)
        return verified

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def __repr__(self):
        return '<User {}>'.format(self.username)


class House(db.Model):
    """
    house_name: Name of the house
    house_name_serial: unique name identifying the house
    profile_path: path to the house profile picture
    status: Boolean value whether active(True), or dormant
    farm_name: Associated farm
    """
    id = db.Column(db.Integer, primary_key=True)
    house_name = db.Column(db.String)
    house_name_serial = db.Column(db.String, unique=True)
    profile_path = db.Column(db.String, nullable=True)
    status = db.Column(db.Boolean)
    farm = db.relationship('Farm', backref=db.backref('house', lazy='dynamic'))
    farm_name = db.Column(db.String, db.ForeignKey('farm.farm_name'))
    currentCrop = db.Column(db.String, nullable=True)

    def __init__(self, farm_name, house_name):
        self.house_name = house_name
        self.house_name_serial = house_name+sep+farm_name
        self.farm = Farm.query.filter_by(farm_name=farm_name).first()
        self.status = False

    def __repr__(self):
        return '<House {}, Farm {} >'.format(self.house_name, self.farm_name)


class Crop(db.Model):
    """
    crop_name: name of the crop, e.g Button
    crop_no: Number of the crop
    crop_no_serial: unique number identifying the crop
    start_date: String, identifying the start date
    status: Boolean, True(Active), False(Archived)
    house_name: Associated house
    """
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String)
    crop_no = db.Column(db.String)
    crop_no_serial = db.Column(db.String, unique=True)
    start_date = db.Column(db.String)
    current_date = db.Column(db.String)
    end_date = db.Column(db.String, nullable=True)
    status = db.Column(db.Boolean)
    summary = db.Column(db.String)
    house = db.relationship('House', backref=db.backref(
        'crop', lazy='dynamic'
    ))
    house_name_serial = db.Column(
        db.String, db.ForeignKey('house.house_name_serial')
    )
    house_name = db.Column(db.String)

    def __init__(self, farm_name, house_name, crop_name, crop_no, start_date):
        self.crop_name = crop_name
        self.crop_no = crop_no
        self.start_date = start_date
        self.current_date = start_date
        self.status = True
        self.house_name_serial = house_name+sep+farm_name
        self.crop_no_serial = crop_no+sep+self.house_name_serial
        self.house = House.query.filter_by(
            house_name_serial=self.house_name_serial
        ).first()
        self.house.status = True
        self.house.currentCrop = self.crop_no
        self.house_name = house_name

    def summarize(self, date, summary):
        self.current_date = date
        self.end_date = date
        self.status = False
        self.summary = summary

    def __repr__(self):
        return '<Crop {}, House {}>'.format(self.crop_no, self.house_name_serial)


class Day(db.Model):
    """
    day_serial: unique day number in the crop calender
    date: date of the day
    crop_no: crop number of associated crop
    status: True (Current day. Not all data is updated)
    actv: Activities tracker (True if updated)
    condt: Condition tracker (True if updated)
    harv: Harvest tracker (True if updated)
    """
    id = db.Column(db.Integer, primary_key=True)
    day_serial = db.Column(db.String, unique=True)
    day_no = db.Column(db.Integer)
    date = db.Column(db.String)
    status = db.Column(db.Boolean)
    crop = db.relationship('Crop', backref=db.backref('day', lazy='dynamic'))
    crop_no_serial = db.Column(db.String, db.ForeignKey('crop.crop_no_serial'))
    counter = db.Column(db.Integer)
    actv = db.Column(db.Boolean, default=False)
    condt = db.Column(db.Boolean, default=False)
    harv = db.Column(db.Boolean, default=False)

    def __init__(self, farm_name, house_name, crop_no, day_no, date):
        self.date = date
        self.crop_no_serial = crop_no+sep+house_name+sep+farm_name
        self.day_serial = day_no+sep+self.crop_no_serial
        self.day_no = int(day_no)
        self.status = True
        self.crop = Crop.query.filter_by(
            crop_no_serial=self.crop_no_serial
        ).first()
        self.counter = 0
        self.crop.current_date = date

    def day_check(self):
        if self.actv == True and self.condt == True and self.harv == True:
            self.status = False

    def actv_tracker(self):
        self.actv = True

    def condt_tracker(self):
        self.condt = True

    def harv_tracker(self):
        self.harv = True

    def __repr__(self):
        return '<Day: {}, CropNo: {}>'.format(self.day_no, self.crop_no_serial)


class Harvest(db.Model):
    """
    punnets: Number of harvested punnets
    record_time: time the record was updated in the system
    chronicler: the user who updated the record
    day_no: the day of the harvest
    updated: Whether an update has been recorded
    """
    id = db.Column(db.Integer, primary_key=True)
    punnets = db.Column(db.String)
    record_time = db.Column(db.String)
    updated = db.Column(db.Boolean)
    day = db.relationship('Day', backref=db.backref(
        'harvest', lazy='dynamic'
    ))
    day_serial = db.Column(db.String, db.ForeignKey('day.day_serial'))
    user = db.relationship('Users', backref=db.backref(
        'harvest', lazy='dynamic'
    ))
    username_serial = db.Column(
        db.String, db.ForeignKey('users.username_serial')
    )
    chronicler = db.Column(db.String)

    def __init__(
        self, farm_name, house_name, crop_no, day_no, punnets, chronicler,
        updated=True
    ):
        self.punnets = punnets
        self.updated = updated
        self.day_serial = day_no+sep+crop_no+sep+house_name+sep+farm_name
        self.username_serial = chronicler+sep+farm_name
        self.day = Day.query.filter_by(day_serial=self.day_serial).first()
        self.user = Users.query.filter_by(
            username_serial=self.username_serial
        ).first()
        time = dt.now()
        self.record_time = time.ctime()
        self.day.harv_tracker()
        self.day.day_check()
        self.chronicler = chronicler

    def __repr__(self):
        return '<Harvest, {} Day {}>'.format(self.punnets, self.day_serial)


class Condition(db.Model):
    """
    temperature: in degrees celcius
    humidity: relative humidity
    record_time: time the record was updated in the system
    chronicler: the user who updated the record
    day_no: the day of the harvest
    updated: Whether an update has been recorded
    time: the time the record was taken
    """
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.String)
    humidity = db.Column(db.String)
    time = db.Column(db.String)
    record_time = db.Column(db.String)
    updated = db.Column(db.Boolean)
    day = db.relationship('Day', backref=db.backref(
        'condition', lazy='dynamic'
    ))
    day_serial = db.Column(db.String, db.ForeignKey('day.day_serial'))
    user = db.relationship('Users', backref=db.backref(
        'condition', lazy='dynamic'
    ))
    username_serial = db.Column(
        db.String, db.ForeignKey('users.username_serial')
    )
    chronicler = db.Column(db.String)

    def __init__(
        self, farm_name, house_name, crop_no, day_no, temperature, humidity,
        time, chronicler, updated=True
    ):
        self.temperature = temperature
        self.humidity = humidity
        self.time = time
        self.updated = updated
        self.day_serial = day_no+sep+crop_no+sep+house_name+sep+farm_name
        self.username_serial = chronicler+sep+farm_name
        self.day = Day.query.filter_by(day_serial=self.day_serial).first()
        self.user = Users.query.filter_by(
            username_serial=self.username_serial
        ).first()
        time = dt.now()
        self.record_time = time.ctime()
        self.day.condt_tracker()
        self.day.day_check()
        self.chronicler = chronicler

    def __repr__(self):
        return '<Condition: {}>'.format(self.day_serial)


class Activities(db.Model):
    """
    description: Short description of the day's activities
    record_time: time the record was updated in the system
    chronicler: the user who updated the record
    updated: Whether an update has been recorded
    day_no: the day of the harvest
    """
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=True)
    record_time = db.Column(db.String)
    updated = db.Column(db.Boolean)
    day = db.relationship('Day', backref=db.backref(
        'activities', lazy='dynamic'
    ))
    day_serial = db.Column(db.String, db.ForeignKey('day.day_serial'))
    user = db.relationship('Users', backref=db.backref(
        'activities', lazy='dynamic'
    ))
    username_serial = db.Column(
        db.String, db.ForeignKey('users.username_serial')
    )
    chronicler = db.Column(db.String)

    def __init__(
        self, farm_name, house_name, crop_no, day_no, description, chronicler,
        updated=True
    ):
        self.description = description
        self.updated = updated
        self.day_serial = day_no+sep+crop_no+sep+house_name+sep+farm_name
        self.username_serial = chronicler+sep+farm_name
        self.day = Day.query.filter_by(day_serial=self.day_serial).first()
        self.user = Users.query.filter_by(
            username_serial=self.username_serial
        ).first()
        time = dt.now()
        self.record_time = time.ctime()
        self.day.actv_tracker()
        self.day.day_check()
        self.chronicler = chronicler

    def __repr__(self):
        return '<Activities {}>'.format(self.day_serial)
