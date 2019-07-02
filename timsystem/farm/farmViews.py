from flask import Blueprint, render_template, redirect, url_for, request
from flask import session, flash, g
from flask_login import current_user, login_user, logout_user, login_required
from wtforms import Form, StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField
from timsystem.farm.models import Farm, Users
from timsystem import db
from timsystem import login_manager
# import os


farm = Blueprint('farm', __name__)


@login_manager.user_loader
def load_user(username):
    return Users.query.filter_by(username=username).first()


@farm.before_request
def get_current_user():
    g.user = current_user


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
            flash('Registration request of %s has been recieved. Check your email for the verification link' % (farm_name), 'success')
            return redirect(url_for('farm.home'))
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
        # phone_no = form.phone_no.data
        password = form.password.data

        # Check if farm_name exists
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        if not farm:
            flash('The farm %s is not found' % farm_name, 'danger')
            return render_template('register_admin.html', form=form)

        # Check admin
        user = Users.query.filter_by(username=username).first()
        if not user:
            # Register admin
            farm = Farm.query.filter_by(farm_name=farm_name).first()
            admin_email = farm.farm_email
            newAdmin = Users(
                admin_name, username, admin_email, password, farm_name, 'Admin'
                )
            db.session.add(newAdmin)
            db.session.commit()
            flash('Administrator Registered!', 'success')
            return redirect(url_for('farm.signin'))
        elif user.farm_name == farm_name and user.level == 'Admin':
            flash('The admin is already registered', 'success')
            return redirect(url_for('farm.signin'))
        else:
            flash('The username %s is already picked' % username, 'danger')
    return render_template('register_admin.html', form=form)


@farm.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        flash('You are already signed in', 'success')
    if request.method == 'POST':
        farm_name = request.form.get('farm_name')
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        farm = Farm.query.filter_by(farm_name=farm_name).first()

        if not farm:
            flash('The farm %s is not registered' % farm_name, 'danger')
            return render_template('signin.html')

        if not farm.confirmed:
            flash(
                'Your farm registration is due. Please check your email for the confirmation link',
                'danger'
            )
            return render_template('signin.html')

        user = farm.users.filter_by(username=username).first()

        if not user:
            flash('The username %s is not registered in the farm %s' % (
                username, farm_name), 'danger')
            return render_template('signin.html')

        if not user.confirmed:
            flash(
                'Your email verification is pending. Please check your email for activation',
                'danger'
            )
            return render_template('signin.html')

        auth = user.authenticate(password)

        if not auth:
            flash('Wrong password', 'danger')
            return render_template('signin.html')
        else:
            login_user(user, remember=remember)
            if user.level == 'Admin':
                return redirect(url_for(
                    'admin.farm_admin', farm_name=farm_name
                ))
            else:
                return redirect(url_for(
                    'user.user_dashboard', farm_name=farm_name))
    return render_template('signin.html')


# Sign out route
@farm.route('/signout')
def signout():
    logout_user()
    # flash Signed out
    return redirect(url_for('farm.signin'))
