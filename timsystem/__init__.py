from flask import Flask
from timsystem.farm.config import Dev


app = Flask(__name__)
app.config.from_object(Dev)

from timsystem.farm.farmViews import farm
app.register_blueprint(farm)
