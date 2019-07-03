from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from timsystem.farm.config import Production


app = Flask(__name__)
app.config.from_object(Production)
db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

mail = Mail(app)

from timsystem.farm.farmViews import farm
from timsystem.farm.userviews import user
from timsystem.farm.adminviews import admin
from timsystem.farm.administrator import administor
app.register_blueprint(farm)
app.register_blueprint(user)
app.register_blueprint(admin)
app.register_blueprint(administor)

db.create_all()

from timsystem.farm.models import Level, Users, Administrator


@login_manager.user_loader
def load_user(id):
    user = Users.query.filter_by(username=id).first()
    if user:
        return user
    admin = Administrator.query.filter_by(username=id).first()
    return admin


if not Level.query.all():
    admin = Level('Admin')
    user = Level('User')
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()
