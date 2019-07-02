from flask import Blueprint, render_template, redirect, url_for
from flask import flash
from flask_mail import Message
from timsystem.farm.models import Farm
from timsystem.farm.email import send_email
from timsystem.farm.token import gen_confirm_token
from timsystem import db, mail


administor = Blueprint('administor', __name__)


@administor.route('/farmAdministor')
def administrator():
    farms = Farm.query.filter_by(confirmed=False).all()
    return render_template('admin_home.html', farms=farms)


@administor.route('/activateFarm/<farm_name>')
def farm_activate(farm_name):
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    # Send activation link
    token = gen_confirm_token(farm_name, farm.farm_email)
    confirm_url = url_for(
        'farm.confirm_farm_email', token=token, _external=True
    )
    html = render_template('activate.html', confirm_url=confirm_url)
    subject = 'Confirm Your Email'
    send_email(farm.farm_email, subject, html)

    farm.pending = True
    db.session.add(farm)
    db.session.commit()
    return redirect(url_for('administor.administrator'))


@administor.route('/rejectFarm/<farm_name>')
def farm_reject(farm_name):
    # Send rejection email
    farm = Farm.query.filter_by(farm_name=farm_name).first()
    db.session.delete(farm)
    db.session.commit()
    flash('Farm %s registration requests rejected' % farm_name, 'danger')
    return redirect(url_for('administor.administrator'))


@administor.route('/emails')
def comm():
    ml = ['timdevtesting@gmail.com']
    msg = Message('Testing', recipients=ml)
    msg.body = 'Testing flask mail'
    mail.send(msg)
    return redirect(url_for('administor.administrator'))
