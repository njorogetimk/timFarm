from flask import Blueprint, render_template, redirect, url_for, request
from flask import flash, g
from flask_login import current_user
from wtforms import Form, StringField, TextAreaField, validators
from wtforms.fields.html5 import EmailField
from timsystem.farm.models import Farm, Users, House, Crop, Day
from timsystem.farm.models import Activities, Harvest, Condition
from timsystem.farm.email import send_email
from timsystem.farm.token import gen_confirm_token
from timsystem.farm.userviews import StartDay
from timsystem.farm import daycheck as dayGiver
from timsystem import db
from functools import wraps


admin = Blueprint('admin', __name__)

"""
Administrator routes
"""


@admin.before_request
def get_current_user():
    g.user = current_user


# Check if administrator in
def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_active and current_user.level == 'Admin':
            return f(*args, **kwargs)
        else:
            flash('Unauthorized!!!', 'danger')
            return redirect(url_for('farm.signin'))
    return wrap


class HouseName(Form):
    house_name = StringField('Name of the new house', [
        validators.DataRequired(),
        validators.length(min=3, max=10)
    ])
# Dashboard
@admin.route('/<farm_name>/admin-dashboard')
@is_admin
def farm_admin(farm_name):
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signin'))
    form = HouseName(request.form)
    # Get the houses belonging to the farm
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    # You should be able to determine which are active and dormant
    houses = farm.house.all()
    return render_template('admin/admin_dashboard.html', form=form, houses=houses)

# Display the house
@admin.route('/<farm_name>/<house_name>/house')
@is_admin
def disp_house(farm_name, house_name):
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('admin.farm_admin', farm_name=farm_name))
    # Query the number of crops present
    # The crops should have an active or archived status
    crops = house.crop.all()
    active_crop = house.crop.filter_by(status=True).first()

    # Change the house status
    freeze = request.args.get('freeze')
    activate = request.args.get('activate')
    if freeze:
        # Freeze the house
        house.status = False
        db.session.commit()
        flash('The house is now frozen', 'success')
        return redirect(url_for(
            'admin.disp_house', farm_name=farm_name, house_name=house_name
        ))
    if activate:
        # Activate the house
        house.status = True
        db.session.commit()
        flash('The house has been activated', 'success')
        return redirect(url_for(
            'admin.disp_house', farm_name=farm_name, house_name=house_name
        ))

    return render_template(
        'display/disp_house.html', crops=crops, active_crop=active_crop,
        house=house
    )


# Add a house
@admin.route('/<farm_name>/add/house', methods=['POST', 'GET'])
@is_admin
def add_house(farm_name):
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
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
        return redirect(url_for('admin.farm_admin', farm_name=farm_name))
    return redirect(url_for('admin.farm_admin', farm_name=farm_name))


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
@admin.route('/<farm_name>/<house_name>/add/crop', methods=['GET', 'POST'])
@is_admin
def add_crop(farm_name, house_name):
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    form = CropForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('admin.farm_admin', farm_name=farm_name))

    # Get the current crop in the house
    current_crop_no = house.currentCrop
    current_crop = house.crop.filter_by(crop_no=current_crop_no).first()
    date = dayGiver.ConvDate(current_crop.end_date)
    min_date = date.result()  # For date picker min date

    if request.method == 'POST' and form.validate():
        # Get the data and update it
        crop_name = form.crop_name.data
        crop_no = form.crop_no.data
        start_date = form.start_date.data

        crop = house.crop.filter_by(crop_no=crop_no).first()
        if not crop:
            # Get started on the new crop
            crop = Crop(farm_name, house_name, crop_name, crop_no, start_date)
            day_no = '1'
            day = Day(farm_name, house_name, crop_no, day_no, start_date)
            db.session.add(crop)
            db.session.add(day)
            db.session.commit()
            flash('New crop %s created' % crop_no, 'success')
            return redirect(url_for(
                'admin.disp_house', farm_name=farm_name, house_name=house_name
            ))
        else:
            flash('The crop number %s is present' % crop_no, 'danger')
            return redirect(url_for(
                'admin.disp_house', farm_name=farm_name, house_name=house_name
            ))
    return render_template('admin/add_crop.html', form=form, min_date=min_date)


class EndCrop(Form):
    summary = TextAreaField("The crop summarizing comments", [
        validators.DataRequired(),
        validators.length(min=5, max=600)
    ])
    date = StringField("Pick the ending date", [
        validators.DataRequired()
    ])


@admin.route(
    '/<farm_name>/<house_name>/<crop_no>/archive', methods=['GET', 'POST']
)
@is_admin
def archive_crop(farm_name, house_name, crop_no):
    form = EndCrop(request.form)
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('admin.farm_admin', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('The crop %s is not present in this house' % crop_no, 'danger')
        return redirect(url_for(
            'admin.disp_house', farm_name=farm_name, house_name=house_name
        ))

    date = dayGiver.ConvDate(crop.current_date)
    min_date = date.result()  # For date picker min date

    if request.method == 'POST' and form.validate():
        # End the crop
        summary = form.summary.data
        date = form.date.data

        crop.summarize(date, summary)
        db.session.commit()
        return redirect(url_for(
            'admin.disp_house', farm_name=current_user.farm_name,
            house_name=crop.house_name
        ))
    return render_template(
        'admin/archive_crop.html', crop=crop, form=form, min_date=min_date
    )


@admin.route('/<farm_name>/<house_name>/<crop_no>/add/day', methods=['POST'])
@is_admin
def add_day(farm_name, house_name, crop_no):
    form = StartDay(request.form)
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('admin.farm_admin', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('The crop %s is not present in this house' % crop_no, 'danger')
        return redirect(url_for(
            'admin.disp_house', farm_name=farm_name, house_name=house_name
        ))
    date = form.date.data
    daycheck = dayGiver.Dates(crop.start_date, date)
    day_no = str(daycheck.day_no())
    get_day = crop.day.filter_by(day_no=day_no).first()
    if not get_day:
        day = Day(farm_name, house_name, crop_no, day_no, date)
        db.session.add(day)
        db.session.commit()
        flash('Day %s of crop %s started' % (day_no, crop.crop_no), 'success')
        return redirect(url_for(
            'user.disp_crop', farm_name=farm_name, house_name=house_name,
            crop_no=crop_no
        ))
    else:
        flash('The day %s is present. Update its record' % day_no, 'success')
        return redirect(url_for(
            'user.disp_crop', farm_name=farm_name, house_name=house_name,
            crop_no=crop_no, form=form
        ))


# End a day
@admin.route('/<farm_name>/<house_name>/<crop_no>/end/day/<day_no>')
@is_admin
def end_day(farm_name, house_name, crop_no, day_no):
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    house = farm.house.filter_by(house_name=house_name).first()
    if not house:
        flash('The house %s is not registered' % house_name, 'danger')
        return redirect(url_for('admin.farm_admin', farm_name=farm_name))
    crop = house.crop.filter_by(crop_no=crop_no).first()
    if not crop:
        flash('The crop %s is not present in this house' % crop_no, 'danger')
        return redirect(url_for(
            'admin.disp_house', farm_name=farm_name, house_name=house_name
        ))
    day = crop.day.filter_by(day_no=day_no).first()
    if not day:
        flash('The day %s is not present in this crop' % day_no, 'danger')
        return redirect(url_for(
            'user.disp_crop', farm_name=farm_name, house_name=house_name,
            crop_no=crop_no
        ))

    # End the day
    actv = day.activities.filter_by(updated=True).first()
    harv = day.harvest.filter_by(updated=True).first()
    condt = day.condition.filter_by(updated=True).first()

    if not actv:
        # Update null fields
        description = 'There were no activities'
        null_actv = Activities(
            farm_name, house_name, crop_no, day_no, description, current_user.username
        )
        db.session.add(null_actv)
        db.session.commit()

    if not harv:
        # Update null fields
        punnets = '0'
        null_harv = Harvest(
            farm_name, house_name, crop_no, day_no, punnets, current_user.username
        )
        db.session.add(null_harv)
        db.session.commit()

    if not condt:
        # Update null fields
        temperature = '0'
        humidity = '0'
        time = '00:00'
        null_condt = Condition(
            farm_name, house_name, crop_no, day_no, temperature, humidity,
            time, current_user.username
        )
        db.session.add(null_condt)
        db.session.commit()
    flash('Day %s ended' % day_no, 'success')
    return redirect(url_for(
        'user.disp_crop', farm_name=farm_name, house_name=house_name,
        crop_no=crop_no
    ))


# View Users
@admin.route('/<farm_name>/view-users')
@is_admin
def disp_users(farm_name):
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    users = farm.users.order_by('username').all()
    return render_template('display/disp_users.html', users=users)


class UserForm(Form):
    user_name = StringField('Name', [
        validators.DataRequired(),
        validators.length(min=2, max=50)
    ])
    username = StringField('Username', [
        validators.DataRequired(),
        validators.length(min=3, max=20)
    ])
    user_email = EmailField('Email', [
        validators.DataRequired(),
        validators.Email()
    ])


# Register User
@admin.route('/<farm_name>/register-user', methods=['POST', 'GET'])
@is_admin
def reg_user(farm_name):
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    form = UserForm(request.form)
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))

    if request.method == 'POST':
        user_name = form.user_name.data
        username = form.username.data
        user_email = form.user_email.data
        user = farm.users.filter_by(username=username).first()
        if not user:
            # pd = os.urandom(3)
            # password = pd.hex()
            password = '123'
            user = Users(
                user_name, username, user_email, password, farm_name, 'User'
            )
            db.session.add(user)
            db.session.commit()

            token = gen_confirm_token(farm_name, username)
            confirm_url = url_for(
                'farm.confirm_user_token', token=token, _external=True
            )
            html = render_template(
                'emails/acc_activate.html', confirm_url=confirm_url, admin=False,
                user=user, password=password
            )
            subject = 'Activate Your Account'
            send_email(user_email, subject, html)

            flash('New user %s created' % user_name, 'success')
            return redirect(url_for('admin.disp_users', farm_name=farm_name))
        else:
            flash('The username %s is already picked' % username, 'danger')
    return render_template('register/register_user.html', form=form)


# Delete User
@admin.route('/<farm_name>/delete-user/<username>')
@is_admin
def del_users(farm_name, username):
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    if not farm:
        flash('Please register your farm %s' % farm_name, 'danger')
        return redirect(url_for('farm.registerFarm'))
    user = farm.users.filter_by(username=username).first()
    if not user:
        flash('The user %s does not exist' % username, 'danger')
        return redirect(url_for('admin.disp_users', farm_name=farm_name))
    db.session.delete(user)
    db.session.commit()
    flash('The user %s has been successfully deleted' % user.name, 'success')
    return redirect(url_for('admin.disp_users', farm_name=farm_name))


# Messaging
@admin.route('/<farm_name>/message')
@is_admin
def message(farm_name):
    if farm_name != current_user.farm_name:
        flash('Unauthorized!!', 'danger')
        return redirect(url_for('farm.signout'))
    return render_template('messaging.html')
