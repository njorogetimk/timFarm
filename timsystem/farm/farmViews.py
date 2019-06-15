from flask import Blueprint, render_template, redirect, url_for, request
from flask import session
from wtforms import Form, StringField, PasswordField, IntegerField, validators
from wtforms.fields.html5 import EmailField
from timsystem import app


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

        # flash new farm created
        return redirect(url_for('farm.registerAdmin', farm_name=farm_name))
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
    phone_no = IntegerField('Phone Number', [
        validators.DataRequired()
    ])
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
        phone_no = form.phone_no.data
        password = form.password.data

        # Flash you are now registered
        return redirect(url_for('farm.signin'))
    return render_template('register_admin.html', form=form)


@farm.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        farm_name = request.form.get('farm_name')
        username = request.form.get('username')
        level = request.form.get('level')
        session['farm_name'] = farm_name

        if level == 'admin':
            return redirect(url_for('farm.admin', farm_name=farm_name))
        else:
            return redirect(url_for('farm.user_dashboard', farm_name=farm_name))
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
    # You should be able to determine which are active and dormant
    return render_template('admin_dashboard.html', form=form)

# Display the house
@farm.route('/<farm_name>/<house_name>/house')
def disp_house(farm_name, house_name):
    # Query the number of crops present
    # The crops should have an active or archived status
    return render_template('disp_house.html')

# Add a house
@farm.route('/<farm_name>/add/house', methods=['POST', 'GET'])
def add_house(farm_name):
    form = HouseName(request.form)
    if request.method == 'POST' and form.validate():
        house_name = form.house_name.data
        # save the data
        # Flash new house created
        return redirect(url_for('farm.admin', farm_name=farm_name))
    # Flash error
    return redirect(url_for('farm.admin', farm_name=farm_name))

# Display a crop
@farm.route('/<farm_name>/<house_name>/crop/<crop_no>')
def disp_crop(farm_name, house_name, crop_no):
    # Query the crop number
    
    return render_template('disp_crop.html')


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
    if request.method == 'POST' and form.validate():
        crop_name = form.crop_name.data
        crop_no = form.crop_no.data
        start_date = form.start_date.data
        # Get the data and update it
        # Get started on the new crop
        return redirect(url_for('farm.disp_crop', farm_name=farm_name, house_name=house_name, crop_no=crop_no))
    return render_template('add_crop.html', form=form)


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

# Update records
@farm.route('/<farm_name>/record', methods=['POST', 'GET'])
def record(farm_name):
    return render_template('record.html')


# Sign out route
@farm.route('/signout')
def signout():
    session.clear()
    # flash Signed out
    return redirect(url_for('farm.home'))
