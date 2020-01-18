import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'eval.db')
    # username = 'root'
    # password = '123'
    # SQLALCHEMY_DATABASE_URI = 'mysql://' + username + ':' + password + '@127.0.0.1/eval'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # WKHTMLTOPDF_PATH = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
    # RBAC_USE_WHITE = True

	# CELERY_BROKER_URL = 'redis:////localhost:6379//0'
	# CELERY_RESULT_BACKEND = 'redis:////localhost:6379//0'

