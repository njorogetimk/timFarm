from flask import Blueprint, render_template, redirect, url_for, request
from flask import session, flash
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from wtforms import IntegerField
from wtforms.fields.html5 import EmailField
from timsystem.farm.models import Farm, Users, House, Crop
from timsystem.farm.models import Day, Activities, Harvest, Condition
from timsystem import db, app
from timsystem.farm import daycheck as dayGiver


farm = Blueprint('farm', __name__)


@farm.route('/')
@farm.route('/home')
def home():
    return render_template('home.html')


"""
Initial setup of the farm, routes
"""


class RegisterFarm(Form):
    farm_name = StringField('Name of the Farm', [
        validators.DataRequired(),
        validators.length(min=3, max=30)
    ])
    farm_email = EmailField('Email', [
        validators.DataRequired(),
        validators.Email()
    ])


@farm.route('/register-farm', methods=['POST', 'GET'])
def registerFarm():
    form = RegisterFarm(request.form)
    if request.method == 'POST' and form.validate():
        # Store the data
        farm_name = form.farm_name.data
        farm_email = form.farm_email.data

        # Check if farm_name exists
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        if not farm:
            # The farm does not exist
            newFarm = Farm(farm_name, farm_email)
            db.session.add(newFarm)
            db.session.commit()
            flash('New farm %s created' % (farm_name), 'success')
            return redirect(url_for('farm.registerAdmin', farm_name=farm_name))
        else:
            flash('The farm name %s taken' % farm_name, 'danger')
            # return redirect(url_for('farm.registerFarm'))
    return render_template('register_farm.html', form=form)


class RegisterAdmin(Form):
    admin_name = StringField('Name', [
        validators.DataRequired(),
        validators.length(min=2, max=50)
    ])
    username = StringField('Username', [
        validators.DataRequired(),
        validators.length(min=3, max=20)
    ])
    admin_email = EmailField('Email', [
        validators.DataRequired(),
        validators.Email()
    ])
    # phone_no = IntegerField('Phone Number', [
    #     validators.DataRequired()
    # ])
    password = PasswordField('Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


@farm.route('/register-admin/<farm_name>', methods=['POST', 'GET'])
def registerAdmin(farm_name):
    form = RegisterAdmin(request.form)
    if request.method == 'POST' and form.validate():
        admin_name = form.admin_name.data
        username = form.username.data
        admin_email = form.admin_email.data
        # phone_no = form.phone_no.data
        password = form.password.data

        # Check if farm_name exists
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        if not farm:
            flash('The farm %s is not found' % farm_name, 'danger')
            return render_template('register_admin.html', form=form)

        # Check admin
        user = farm.users.filter_by(username=username).first()
        if not user:
            # Register admin
            newAdmin = Users(
                admin_name, username, admin_email, password, farm_name, 'Admin'
                )
            db.session.add(newAdmin)
            db.session.commit()
            flash('Administrator Registered!', 'success')
            return redirect(url_for('farm.signin'))
        elif user.level == 'Admin':
            flash('The admin is already registered', 'success')
            return redirect(url_for('farm.signin'))
    return render_template('register_admin.html', form=form)


@farm.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        farm_name = request.form.get('farm_name')
        username = request.form.get('username')
        password = request.form.get('password')

        farm = Farm.query.filter_by(farm_name=farm_name).first()

        if not farm:
            flash('The farm %s is not registered' % farm_name, 'danger')
            return render_template('signin.html')

        user = farm.users.filter_by(username=username).first()
        if not user:
            flash('The username %s is not registered in the farm %s' % (
                username, farm_name), 'danger')
            return render_template('signin.html')

        auth = user.authenticate(password)

        if not auth:
            flash('Wrong password', 'danger')
            return render_template('signin.html')
        else:
            session['farm_name'] = farm_name
            session['username'] = username
            if user.level == 'Admin':
                return redirect(url_for('farm.admin', farm_name=farm_name))
            else:
                return redirect(url_for(
                    'farm.user_dashboard', farm_name=farm_name))
    return render_template('signin.html')


"""
Administrator routes
"""


class HouseName(Form):
    house_name = StringField('Name of the new house', [
        validators.DataRequired(),
        validators.length(min=3, max=10)
    ])
# Dashboard
@farm.route('/<farm_name>/admin-dashboard')
def admin(farm_name):
    form = HouseName(request.form)
    # Get the houses belonging to the farm
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    # You should be able to determine which are active and dormant
    houses = farm.house.all()
    return render_template('admin_dashboard.html', form=form, houses=houses)

# Display the house
@farm.route('/<farm_name>/<house_name>/house')
def disp_house(farm_name, house_name):
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('farm.admin', farm_name=farm_name))
    # Query the number of crops present
    # The crops should have an active or archived status
    crops = house.crop.all()
    active_crop = house.crop.filter_by(status=True).first()
    return render_template('disp_house.html', crops=crops, active_crop=active_crop, house_name=house_name)


# Add a house
@farm.route('/<farm_name>/add/house', methods=['POST', 'GET'])
def add_house(farm_name):
    form = HouseName(request.form)
    if request.method == 'POST' and form.validate():
        house_name = form.house_name.data
        # save the data
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        if not farm:
            flash('Please register your farm %s' % farm_name, 'danger')
            return redirect(url_for('farm.registerFarm'))
        house = farm.house.filter_by(house_name=house_name).first()
        if not house:
            house = House(farm_name, house_name)
            db.session.add(house)
            db.session.commit()
            flash('House %s created' % house_name, 'success')
        else:
            flash('House %s is present' % house_name, 'success')
        return redirect(url_for('farm.admin', farm_name=farm_name))
    return redirect(url_for('farm.admin', farm_name=farm_name))


# Display a crop
@farm.route('/<farm_name>/<house_name>/crop/<crop_no>')
def disp_crop(farm_name, house_name, crop_no):
    # Query the crop number
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('farm.admin', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('The crop number is not found', 'danger')
        return redirect(url_for('farm.disp_house', house_name=house_name, farm_name=farm_name))

    days = crop.day.order_by('day_no').all()
    daysdata = {}

    for day in days:
        harv = day.harvest.all()
        condt = day.condition.all()
        actv = day.activities.all()
        if harv:
            harv = harv[0]
        if condt:
            condt = condt[0]
        if actv:
            actv = actv[0]
        daysdata[day.day_serial] = {
            "condition": condt, "harvest": harv, "activities": actv
        }

    day_status = crop.day.filter_by(status=True).first()

    return render_template('disp_crop.html', crop=crop, days=days, daysdata=daysdata, day_status=day_status)


class CropForm(Form):
    crop_name = StringField('The name of the crop', [
        validators.DataRequired(),
        validators.length(min=3, max=10)
    ])
    crop_no = StringField('The Crop Number', [
        validators.DataRequired(),
        validators.length(min=1, max=10)
    ])
    start_date = StringField('Select the start date', [
        validators.DataRequired()
    ])


# Add a crop
@farm.route('/<farm_name>/<house_name>/add/crop', methods=['GET', 'POST'])
def add_crop(farm_name, house_name):
    form = CropForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('farm.admin', farm_name=farm_name))

    if request.method == 'POST' and form.validate():
        # Get the data and update it
        crop_name = form.crop_name.data
        crop_no = form.crop_no.data
        start_date = form.start_date.data

        crop = house.crop.filter_by(crop_no=crop_no).first()
        if not crop:
            # Get started on the new crop
            crop = Crop(house_name, crop_name, crop_no, start_date)
            day_serial = '1-'+crop_no
            day = Day(crop_no, day_serial, start_date)
            db.session.add(crop)
            db.session.add(day)
            db.session.commit()
            flash('New crop %s created' % crop_no, 'success')
            return redirect(url_for('farm.disp_house', farm_name=farm_name, house_name=house_name))
        else:
            flash('The crop number %s is present' % crop_no, 'danger')
            return redirect(url_for('farm.disp_house', farm_name=farm_name, house_name=house_name))
    return render_template('add_crop.html', form=form)


@farm.route('/<farm_name>/<house_name>/<crop_no>/add/day', methods=['POST'])
def add_day(farm_name, house_name, crop_no):
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('farm.admin', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('The crop %s is not present in this house' % crop_no, 'danger')
        return redirect(url_for('farm.disp_house', farm_name=farm_name, house_name=house_name))
    date = request.form.get('date')
    daycheck = dayGiver.Dates(crop.start_date, date)
    day_serial = str(daycheck.day_no())+'-'+crop.crop_no
    get_day = crop.day.filter_by(day_serial=day_serial).first()
    if not get_day:
        day = Day(crop_no, day_serial, date)
        db.session.add(day)
        db.session.commit()
        flash('New day %s created' % day_serial, 'success')
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, house_name=house_name, crop_no=crop_no))
    else:
        flash('The day %s is present. Update its record' % day_serial, 'success')
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, house_name=house_name, crop_no=crop_no))


class ActvForm(Form):
    description = TextAreaField("Fill in the day's activities", [
        validators.DataRequired(),
        validators.length(min=5, max=100)
    ])


class CondtForm(Form):
    temperature = IntegerField('Temperature in Celcius', [
        validators.DataRequired()
    ])
    humidity = IntegerField('Relative Humidity', [
        validators.DataRequired()
    ])
    time = StringField('Select the time the records were taken', [
        validators.DataRequired()
    ])


class HarvForm(Form):
    punnets = IntegerField('Enter the number of punnets harvested',[
        validators.DataRequired()
    ])


@farm.route('/<farm_name>/<house_name>/<crop_no>/<day_serial>/record', methods=[
    'POST', 'GET'])
def record(farm_name, house_name, crop_no, day_serial):
    hvForm = HarvForm(request.form)
    cdnForm = CondtForm(request.form)
    actvForm = ActvForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('farm.admin', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('The crop %s is not present in this house' % crop_no, 'danger')
        return redirect(url_for('farm.disp_house', farm_name=farm_name, house_name=house_name))
    day = crop.day.filter_by(day_serial=day_serial).first()
    if not day:
        flash('The day %s is not added' % day_serial, 'danger')
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, crop_no=crop_no, house_name=house_name))

    return render_template('record.html', hvForm=hvForm, cdnForm=cdnForm, actvForm=actvForm, crop=crop, day=day)


@farm.route('/<farm_name>/<house_name>/<crop_no>/<day_serial>/record/activities', methods=['POST', 'GET'])
def record_activities(farm_name, house_name, crop_no, day_serial):
    form = ActvForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('farm.admin', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('The crop %s is not present in this house' % crop_no, 'danger')
        return redirect(url_for('farm.disp_house', farm_name=farm_name, house_name=house_name))
    day = crop.day.filter_by(day_serial=day_serial).first()
    if not day:
        flash('The day %s is not added' % day_serial, 'danger')
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, crop_no=crop_no, house_name=house_name))

    if request.method == 'POST' and form.validate():
        description = form.description.data
        activities = Activities(day.day_serial, description, session['username'])
        db.session.add(activities)
        db.session.commit()
        flash('Success', 'success')
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, house_name=house_name, crop_no=crop_no))
    return render_template('record_activities.html', form=form, crop=crop, day=day)

@farm.route('/<farm_name>/<house_name>/<crop_no>/<day_serial>/record/condition', methods=['POST', 'GET'])
def record_condition(farm_name, house_name, crop_no, day_serial):
    form = CondtForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('farm.admin', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('The crop %s is not present in this house' % crop_no, 'danger')
        return redirect(url_for('farm.disp_house', farm_name=farm_name, house_name=house_name))
    day = crop.day.filter_by(day_serial=day_serial).first()
    if not day:
        flash('The day %s is not added' % day_serial, 'danger')
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, crop_no=crop_no, house_name=house_name))

    if request.method == 'POST' and form.validate():
        temperature = form.temperature.data
        humidity = form.humidity.data
        time = form.time.data
        condition = Condition(day.day_serial, temperature, humidity, time, session['username'])
        db.session.add(condition)
        db.session.commit()
        flash('Success', 'success')
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, house_name=house_name, crop_no=crop_no))
    return render_template('record_condition.html', form=form, crop=crop, day=day)


@farm.route('/<farm_name>/<house_name>/<crop_no>/<day_serial>/record/harvest', methods=['POST', 'GET'])
def record_harvest(farm_name, house_name, crop_no, day_serial):
    form = HarvForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('farm.admin', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('The crop %s is not present in this house' % crop_no, 'danger')
        return redirect(url_for('farm.disp_house', farm_name=farm_name, house_name=house_name))
    day = crop.day.filter_by(day_serial=day_serial).first()
    if not day:
        flash('The day %s is not added' % day_serial, 'danger')
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, crop_no=crop_no, house_name=house_name))

    if request.method == 'POST' and form.validate():
        punnets = form.punnets.data
        harvest = Harvest(day.day_serial, punnets, session['username'])
        db.session.add(harvest)
        db.session.commit()
        flash('Success', 'success')
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, house_name=house_name, crop_no=crop_no))
    return render_template('record_harvest.html', form=form, crop=crop, day=day)


# View Users
@farm.route('/<farm_name>/view-users')
def disp_users(farm_name):
    return render_template('disp_users.html')


# Register User
@farm.route('/<farm_name>/register-user', methods=['POST', 'GET'])
def reg_user(farm_name):
    return render_template('register_user.html')


# Delete User
@farm.route('/<farm_name>/delete-user/<username>')
def del_users(farm_name, username):
    return redirect(url_for('farm.disp_users'))


# Messaging
@farm.route('/<farm_name>/message')
def message(farm_name):
    return render_template('messaging.html')


"""
User Routes
"""
# Dashboard
@farm.route('/<farm_name>/user-dashboard')
def user_dashboard(farm_name):
    return render_template('user_dashboard.html')


# Sign out route
@farm.route('/signout')
def signout():
    session.clear()
    # flash Signed out
    return redirect(url_for('farm.home'))
