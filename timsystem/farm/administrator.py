from flask import Blueprint, render_template, redirect, url_for
from flask import flash
from timsystem.farm.models import Farm
from timsystem import db


administor = Blueprint('administor', __name__)


# @administor.route('/admin-farm')
# def admin():
#     return render_template('admin_sign.html')


@administor.route('/farmAdministor')
def administrator():
    farms = Farm.query.filter_by(confirmed=False).all()
    return render_template('admin_home.html', farms=farms)


# @administor.route('/requests')
# def requests():
#     farms = Farm.query.filter_by(confirmed=False).all()
#     return render_template('reg_request.html', farms=farms)


@administor.route('/activateFarm/<farm_name>')
def farm_activate(farm_name):
    # Send activation link
    farm = Farm.query.filter_by(farm_name=farm_name).first()
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
    return 'communicate'
