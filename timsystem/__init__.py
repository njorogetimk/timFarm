from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from timsystem.farm.config import Dev


app = Flask(__name__)
app.config.from_object(Dev)
db = SQLAlchemy(app)

from timsystem.farm.farmViews import farm
app.register_blueprint(farm)


db.create_all()
