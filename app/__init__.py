from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

# from flask_breadcrumbs import Breadcrumbs
# from flask_rbac import RBAC

from flask_principal import Principal

# load the extension



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
# Breadcrumbs(app=app)

principals = Principal(app)




# rbac = RBAC(app)
# app.config['RBAC_USE_WHITE'] = True
# @rbac.set_user_loader
# def get_current_user():
#     return login.current_user._get_current_object()


admin = Admin(app, template_mode='bootstrap3')

from app.models import User, Student, Phone, School, Branch, Promo, \
	StudentSession, Session, Grade, Semester, Unit, Module, Percentage, Type

# admin.add_view(ModelView(Student, db.session))
# admin.add_view(ModelView(Phone, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(School, db.session))
admin.add_view(ModelView(Branch, db.session))
admin.add_view(ModelView(Promo, db.session))
admin.add_view(ModelView(StudentSession, db.session))
admin.add_view(ModelView(Session, db.session))
admin.add_view(ModelView(Grade, db.session))
admin.add_view(ModelView(Semester, db.session))
admin.add_view(ModelView(Unit, db.session))
admin.add_view(ModelView(Module, db.session))
admin.add_view(ModelView(Percentage, db.session))
admin.add_view(ModelView(Type, db.session))

from app import routes, routesConf, routesGrade, routesCalculation, routesTree, models, errors

