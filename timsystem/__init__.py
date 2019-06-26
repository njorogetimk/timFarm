from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from timsystem.farm.config import Dev


app = Flask(__name__)
app.config.from_object(Dev)
db = SQLAlchemy(app)

migrate = Migrate(app, db)
from timsystem.farm.farmViews import farm
app.register_blueprint(farm)


db.create_all()

from timsystem.farm.models import Level

if not Level.query.all():
    admin = Level('Admin')
    user = Level('User')
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()
