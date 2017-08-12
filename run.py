import sys
from os.path import dirname

from app import app
from config import FLASK_APP_PORT, FLASK_APP_HOST

sys.path.append(dirname(__file__))

app.run(host=FLASK_APP_HOST, port=FLASK_APP_PORT)
