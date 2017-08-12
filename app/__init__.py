from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.static_folder = 'static'
app.config.from_object('config.FlaskConfig')

db = SQLAlchemy(app)

from app.views import mod as main_module
app.register_blueprint(main_module)
