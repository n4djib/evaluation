from flask import Flask, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
# from flask_admin import Admin, BaseView, expose
# from flask_admin.contrib.sqla import ModelView
from flask_breadcrumbs import Breadcrumbs
from celery import Celery
from redis import Redis
# from flask_rbac import RBAC

# from flask_principal import Principal
# from flask_caching import Cache


# def make_celery(app):
# 	celery = Celery(
# 		app.import_name,
#         broker=app.config['CELERY_BROKER_URL'],
#         backend=app.config['CELERY_RESULT_BACKEND']
#     )
# 	return celery



app = Flask(__name__)
app.config.from_object(Config)

# celery = Celery(
# 		app.import_name,
#         broker=app.config['CELERY_BROKER_URL'],
#         backend=app.config['CELERY_RESULT_BACKEND']
#     )

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
# principals = Principal(app)

Breadcrumbs(app=app)

# cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# cache.init_app(app)

# admin = Admin(app, template_mode='bootstrap3')


from app import routes, routesAdmin, routesSession, routesGrade, \
	routesTree, routesStudent, routesBasicTables, routesConfig, \
	routesCalculation, routesCalendar, models, errors

