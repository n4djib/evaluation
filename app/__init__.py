from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
# from flask_admin import Admin, BaseView, expose
# from flask_admin.contrib.sqla import ModelView
from flask_breadcrumbs import Breadcrumbs
# from flask_rbac import RBAC
from flask_principal import Principal





app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
principals = Principal(app)

Breadcrumbs(app=app)


# admin = Admin(app, template_mode='bootstrap3')




from app import routes, routesAdmin, routesSession, routesGrade, routesTree,\
	routesBasicTables, routesConfig, routesCalculation, models, errors

