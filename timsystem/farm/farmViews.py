from flask import Blueprint, render_template, redirect, url_for, request
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
        app.logger.info(level)

        if level == 'admin':
            return redirect(url_for('farm.admin'))
        else:
            return redirect(url_for('farm.user_dashboard'))
    return render_template('signin.html')


"""
Administrator routes
"""
# Dashboard
@farm.route('/admin-dashboard')
def admin():
    return render_template('admin_dashboard.html')

# Display the house
@farm.route('/house/<house_name>')
def disp_house(house_name):
    return render_template('disp_house.html')

# Add a house
@farm.route('/add/house', methods=['POST', 'GET'])
def add_house():
    return render_template('add_house.html')

# Display a crop
@farm.route('/crop/<house_name>/<crop_no>')
def disp_crop(house_name, crop_no):
    return render_template('disp_crop.html')

# Add a crop
@farm.route('/add/crop/<house_name>', methods=['GET', 'POST'])
def add_crop(house_name):
    return render_template('add_crop.html')


# View Users
@farm.route('/view-users')
def disp_users():
    return render_template('disp_users.html')


# Register User
@farm.route('/register-user', methods=['POST', 'GET'])
def reg_user():
    return render_template('register_user.html')


# Delete User
@farm.route('/delete-user/<username>')
def del_users(username):
    return redirect(url_for('farm.disp_users'))


# Messaging
@farm.route('/message')
def message():
    return render_template('messaging.html')


"""
User Routes
"""
# Dashboard
@farm.route('/user-dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')

# Update records
@farm.route('/record', methods=['POST', 'GET'])
def record():
    return render_template('record.html')


# Sign out route
@farm.route('/signout')
def signout():
    return redirect(url_for('farm.home'))
