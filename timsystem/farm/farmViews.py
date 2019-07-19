from flask import Blueprint, render_template, redirect, url_for, request
from flask import flash, g
from flask_login import current_user, login_user, logout_user
from wtforms import Form, StringField, PasswordField, validators
from wtforms.fields.html5 import EmailField
from timsystem.farm.models import Farm, Users
from timsystem.farm.token import confirm_token
from timsystem.farm.email import send_email
from timsystem import db
# import os


farm = Blueprint('farm', __name__)


@farm.before_request
def get_current_user():
    g.user = current_user


@farm.route('/')
@farm.route('/home')
def home():
    return render_template('home/home.html')


"""
Initial setup of the farm, routes
"""


class RegisterFarm(Form):
    farm_name = StringField('Name of the Farm', [
        validators.DataRequired(),
        validators.length(min=3, max=30),
        validators.Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores. Avoid Spaces')
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

            html = render_template(
                'emails/thanks.html', farm=farm
            )
            subject = 'Farm Registration'
            send_email(farm_email, subject, html)

            flash(
                'Registration request of %s has been recieved. Check your mail for the activation link'
                % (farm_name), 'success'
            )
            return redirect(url_for('farm.home'))
        else:
            flash(
                'The farm name %s taken. Please pick another one' % farm_name,
                'danger'
            )
            # return redirect(url_for('farm.registerFarm'))
    return render_template('register/register_farm.html', form=form)


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


@farm.route('/confirm/farm/<token>')
def confirm_farm_token(token):
    try:
        farm_name, farm_email = confirm_token(token)
    except Exception:
        flash('Invalid or expired confirmation link', 'danger')
        return redirect(url_for('farm.home'))

    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if farm.confirmed:
        flash('Account already confirmed', 'success')
    else:
        farm.confirmed = True
        db.session.add(farm)
        db.session.commit()
        flash('Account successfully confirmed', 'success')
    return redirect(url_for('farm.registerAdmin', farm_name=farm_name))


@farm.route('/confirm/user/<token>')
def confirm_user_token(token):
    try:
        farm_name, username = confirm_token(token)
    except Exception:
        flash('Invalid or expired confirmation link', 'danger')
        return redirect(url_for('farm.home'))

    farm = Farm.query.filter_by(farm_name=farm_name).first()
    user = farm.users.filter_by(username=username).first()
    if user.confirmed:
        flash('Account already confirmed', 'success')
    else:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        flash('Account successfully activated', 'success')
    return redirect(url_for('farm.signin'))


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
            return render_template('register/register_admin.html', form=form)

        # Check admin
        user = Users.query.filter_by(username=username).first()
        if not user:
            # Register admin
            farm = Farm.query.filter_by(farm_name=farm_name).first()
            admin_email = farm.farm_email
            newAdmin = Users(
                admin_name, username, admin_email, password, farm_name,
                'Admin', confirmed=True
                )
            db.session.add(newAdmin)
            db.session.commit()

            html = render_template(
                'emails/acc_confirmed.html', admin=newAdmin
            )
            subject = 'Administrator details'
            send_email(farm.farm_email, subject, html)

            flash(
                'Administrator Registered! Your details have been sent to your email',
                'success'
            )
            return redirect(url_for('farm.signin'))
        elif user.farm_name == farm_name and user.level == 'Admin':
            flash('The admin is already registered', 'success')
            return redirect(url_for('farm.signin'))
        else:
            flash('The username %s is already picked' % username, 'danger')
    return render_template('register/register_admin.html', form=form)


@farm.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        flash('You are already signed in', 'success')
        if current_user.level == 'Admin':
            return redirect(url_for(
                'admin.farm_admin', farm_name=current_user.farm_name
            ))
        else:
            return redirect(url_for(
                'user.user_dashboard', farm_name=current_user.farm_name))

    if request.method == 'POST':
        farm_name = request.form.get('farm_name')
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        farm = Farm.query.filter_by(farm_name=farm_name).first()

        if not farm:
            flash('The farm %s is not registered' % farm_name, 'danger')
            return render_template('home/signin.html')

        if not farm.confirmed:
            flash(
                'Your farm registration is due. Please check your email for the confirmation link',
                'danger'
            )
            return render_template('home/signin.html')

        user = farm.users.filter_by(username=username).first()

        if not user:
            flash('The username %s is not registered in the farm %s' % (
                username, farm_name), 'danger')
            return render_template('home/signin.html')

        if not user.confirmed:
            flash(
                'Your email verification is pending. Please check your email for the activation link',
                'danger'
            )
            return render_template('home/signin.html')

        auth = user.authenticate(password)

        if not auth:
            flash('Wrong password', 'danger')
            return render_template('home/signin.html')
        else:
            login_user(user, remember=remember)
            if user.level == 'Admin':
                return redirect(url_for(
                    'admin.farm_admin', farm_name=farm_name
                ))
            else:
                return redirect(url_for(
                    'user.user_dashboard', farm_name=farm_name))
    return render_template('home/signin.html')


# Sign out route
@farm.route('/signout')
def signout():
    logout_user()
    flash('Signed out', 'success')
    return redirect(url_for('farm.signin'))
