from flask import Blueprint, render_template, redirect, url_for, request
from flask import flash, session
from wtforms import Form, StringField, TextAreaField, validators
from wtforms import IntegerField
from timsystem.farm.models import Farm
from timsystem.farm.models import Activities, Harvest, Condition
from timsystem.farm import daycheck as dayGiver
from timsystem import db
from functools import wraps


user = Blueprint('user', __name__)

"""
User Routes
"""


# Check if signed in
def is_signedin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['signed_in']:
            return f(*args, **kwargs)
        else:
            flash('Please signin', 'danger')
            return redirect(url_for('farm.signin'))
    return wrap


# Dashboard
@user.route('/<farm_name>/user-dashboard')
@is_signedin
def user_dashboard(farm_name):
    if farm_name != session['farm_name']:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    houses = farm.house.filter_by(status='True').all()
    active_houses = {}
    for house in houses:
        crop = house.crop.filter_by(status='True').first()
        crop_no = crop.crop_no
        active_houses[house.house_name] = crop_no
    return render_template('user_dashboard.html', houses=active_houses)


# Display a crop
@user.route('/<farm_name>/<house_name>/crop/<crop_no>')
@is_signedin
def disp_crop(farm_name, house_name, crop_no):
    if farm_name != session['farm_name']:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    # Query the crop number
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Unregistered farm!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('Unregistered house!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('Unregistered crop!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))

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
    date = dayGiver.ConvDate(crop.start_date)
    min_date = date.result()
    return render_template(
        'disp_crop.html', crop=crop, days=days, daysdata=daysdata,
        day_status=day_status, min_date=min_date
    )


"""
Recording daily activities
"""


class ActvForm(Form):
    description = TextAreaField("Fill in the day's activities", [
        validators.DataRequired(),
        validators.length(min=5, max=600)
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
    punnets = IntegerField('Enter the number of punnets harvested', [
        validators.DataRequired()
    ])


@user.route(
    '/<farm_name>/<house_name>/<crop_no>/<day_serial>/record/activities',
    methods=['POST', 'GET']
)
@is_signedin
def record_activities(farm_name, house_name, crop_no, day_serial):
    if farm_name != session['farm_name']:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    form = ActvForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Unregistered farm!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('Unregistered house!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('Unregistered crop!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))

    day = crop.day.filter_by(day_serial=day_serial).first()
    if not day:
        flash('The day %s is not added' % day_serial, 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))

    if request.method == 'POST' and form.validate():
        description = form.description.data
        activities = Activities(
            day.day_serial, description, session['username']
        )
        db.session.add(activities)
        db.session.commit()
        flash('Day %s activities updated' % day.day_no, 'success')
        return redirect(url_for(
            'user.disp_crop', farm_name=farm_name, house_name=house_name,
            crop_no=crop_no
        ))
    return render_template(
        'record_activities.html', form=form, crop=crop, day=day
    )


@user.route(
    '/<farm_name>/<house_name>/<crop_no>/<day_serial>/record/condition',
    methods=['POST', 'GET']
)
@is_signedin
def record_condition(farm_name, house_name, crop_no, day_serial):
    if farm_name != session['farm_name']:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    form = CondtForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Unregistered farm!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('Unregistered house!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('Unregistered crop!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))

    day = crop.day.filter_by(day_serial=day_serial).first()
    if not day:
        flash('The day %s is not added' % day_serial, 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))

    if request.method == 'POST' and form.validate():
        temperature = form.temperature.data
        humidity = form.humidity.data
        time = form.time.data
        condition = Condition(
            day.day_serial, temperature, humidity, time, session['username']
        )
        db.session.add(condition)
        db.session.commit()
        flash('Day %s condition updated' % day.day_no, 'success')
        return redirect(url_for(
            'user.disp_crop', farm_name=farm_name, house_name=house_name,
            crop_no=crop_no
        ))
    return render_template(
        'record_condition.html', form=form, crop=crop, day=day
    )


@user.route(
    '/<farm_name>/<house_name>/<crop_no>/<day_serial>/record/harvest',
    methods=['POST', 'GET']
)
@is_signedin
def record_harvest(farm_name, house_name, crop_no, day_serial):
    if farm_name != session['farm_name']:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    form = HarvForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Unregistered farm!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('Unregistered house!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('Unregistered crop!', 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))

    day = crop.day.filter_by(day_serial=day_serial).first()
    if not day:
        flash('The day %s is not added' % day_serial, 'danger')
        return redirect(url_for('user.user_dashboard', farm_name=farm_name))

    if request.method == 'POST' and form.validate():
        punnets = form.punnets.data
        harvest = Harvest(day.day_serial, punnets, session['username'])
        db.session.add(harvest)
        db.session.commit()
        flash('Day %s harvest updated' % day.day_no, 'success')
        return redirect(url_for(
            'user.disp_crop', farm_name=farm_name, house_name=house_name,
            crop_no=crop_no
        ))
    return render_template(
        'record_harvest.html', form=form, crop=crop, day=day
    )
