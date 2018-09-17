from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
# from flask_breadcrumbs import Breadcrumbs




app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
# Breadcrumbs(app=app)
login = LoginManager(app)
login.login_view = 'login'

admin = Admin(app, template_mode='bootstrap3')

from app.models import User, Student, Phone, School, Branch, StudentSession, \
	Session, Grade, Semester, Unit, Module, Percentage, Type

# admin.add_view(ModelView(Student, db.session))
# admin.add_view(ModelView(Phone, db.session))
admin.add_view(ModelView(User,     db.session))
admin.add_view(ModelView(School,   db.session))
admin.add_view(ModelView(Branch,   db.session))
admin.add_view(ModelView(StudentSession, db.session))
admin.add_view(ModelView(Session,  db.session))
admin.add_view(ModelView(Grade,  db.session))
admin.add_view(ModelView(Semester, db.session))
admin.add_view(ModelView(Unit,    db.session))
admin.add_view(ModelView(Module,   db.session))
admin.add_view(ModelView(Percentage, db.session))
admin.add_view(ModelView(Type,     db.session))

from app import routes, routesConf, routesGrade, routesCalculation, models, errors

