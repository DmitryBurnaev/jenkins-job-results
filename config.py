from os.path import dirname, abspath, join as path_join
BASE_DIR = dirname(abspath(__file__))

# FLASK configuration (name must be eq. FLASK_<CONFIG_NAME>)
FLASK_APP_HOST = '0.0.0.0'
FLASK_APP_PORT = 5000
FLASK_DB_NAME = 'data.db'
FLASK_DEBUG = False
FLASK_DEVELOPMENT = True
FLASK_CSRF_ENABLED = True
FLASK_SECRET_KEY = 'YOUR_RANDOM_SECRET_KEY'
FLASK_SQLALCHEMY_TRACK_MODIFICATIONS = False

#  Other application config

JENKINS_AUTH = ('***', '***')
JENKINS_URL = 'http://jenkins2.ezd.lan'
STAGING_STAT_RESULTS_URL = \
    'http://jnode0.ezd.lan/jobs_statistic/81GSStaging.html'

JOB_RESULTS_URL = JENKINS_URL + '/job/{job_name}/lastBuild/testReport/'

RESOURCES_DIR = path_join(BASE_DIR, 'resources')

try:
    from config_local import *
except ImportError:
    pass

FLASK_SQLALCHEMY_DATABASE_URI = \
    'sqlite:///{}'.format(path_join(RESOURCES_DIR, FLASK_DB_NAME))


class FlaskConfig(object):
    DEBUG = FLASK_DEBUG
    CSRF_ENABLED = FLASK_CSRF_ENABLED
    SECRET_KEY = FLASK_SECRET_KEY
    SQLALCHEMY_DATABASE_URI = FLASK_SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = FLASK_SQLALCHEMY_TRACK_MODIFICATIONS


