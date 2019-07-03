from flask import Blueprint, render_template, redirect, url_for
from flask import flash, g, request
from flask_login import current_user, login_user
from wtforms import Form, StringField, validators, PasswordField
from flask_mail import Message
from timsystem.farm.models import Farm
from timsystem.farm.email import send_email
from timsystem.farm.token import gen_confirm_token
from timsystem.farm.models import Administrator
from timsystem import db, mail
from functools import wraps


administor = Blueprint('administor', __name__)


class AdminForm(Form):
    username = StringField('Username', [
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])


@administor.before_request
def get_current_user():
    g.user = current_user


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_active and current_user.top_level:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized !!!', 'danger')
            return redirect(url_for('farm.home'))
    return wrap


@administor.route('/silence', methods=['POST', 'GET'])
def silence():
    form = AdminForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data

        admin = Administrator.query.filter_by(username=username).first()
        if not admin:
            flash('Invalid Login Parameters', 'danger')
            return render_template('silence.html', form=form)
        auth = admin.authenticate(password)
        if not auth:
            flash('Invalid Login Parameters', 'danger')
            return render_template('silence.html', form=form)

        login_user(admin)
        flash('Successful Login', 'success')
        return redirect(url_for('administor.administrator'))
    return render_template('silence.html', form=form)


@administor.route('/farmAdministor')
@is_admin
def administrator():
    farms = Farm.query.filter_by(confirmed=False).all()
    return render_template('admin_home.html', farms=farms)


@administor.route('/activateFarm/<farm_name>')
@is_admin
def farm_activate(farm_name):
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    # Send activation link
    token = gen_confirm_token(farm_name, farm.farm_email)
    confirm_url = url_for(
        'farm.confirm_farm_token', token=token, _external=True
    )
    html = render_template(
        'activate.html', confirm_url=confirm_url, admin=True
    )
    subject = 'Confirm Your Email'
    send_email(farm.farm_email, subject, html)

    farm.pending = True
    db.session.add(farm)
    db.session.commit()
    return redirect(url_for('administor.administrator'))


@administor.route('/rejectFarm/<farm_name>')
@is_admin
def farm_reject(farm_name):
    # Send rejection email
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    db.session.delete(farm)
    db.session.commit()
    flash('Farm %s registration requests rejected' % farm_name, 'danger')
    return redirect(url_for('administor.administrator'))


@administor.route('/emails')
@is_admin
def comm():
    ml = ['timdevtesting@gmail.com']
    msg = Message('Testing', recipients=ml)
    msg.body = 'Testing flask mail'
    mail.send(msg)
    return redirect(url_for('administor.administrator'))
