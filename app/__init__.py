from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_breadcrumbs import Breadcrumbs
# from flask_rbac import RBAC
from flask_principal import Principal

from flask import url_for



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
principals = Principal(app)

Breadcrumbs(app=app)


admin = Admin(app, template_mode='bootstrap3')

from app.models import User, Student, Phone, School, Branch, Promo, \
	StudentSession, Session, Grade, Semester, Unit, Module, Percentage, Type




# admin.add_view(ModelView(Student, db.session))
admin.add_view(ModelView(Phone, db.session))
admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(School, db.session))
# admin.add_view(ModelView(Branch, db.session))
# admin.add_view(ModelView(Promo, db.session))
# admin.add_view(ModelView(StudentSession, db.session))
admin.add_view(ModelView(Session, db.session))
# admin.add_view(ModelView(Grade, db.session))



class S(ModelView):
	form_excluded_columns = ['next_semester', 'units', 'sessions', 'branch']
	def get_save_return_url(self, model, is_created):
		semester = model
		semester_id = semester.id
		return url_for('conf', semester_id=semester_id)
class U(ModelView):
	form_excluded_columns = ['modules', 'grade_units', 'semester']
	def get_save_return_url(self, model, is_created):
		unit = model
		semester_id = unit.semester.id
		return url_for('conf', semester_id=semester_id)
class M(ModelView):
	form_excluded_columns = ['percentages', 'grades', 'unit']
	def get_save_return_url(self, model, is_created):
		module = model
		semester_id = module.unit.semester.id
		return url_for('conf', semester_id=semester_id)
class P(ModelView):
	form_excluded_columns = ['module', 'name']
	# column_editable_list = ['name', 'percentage', 'type']
	column_filters = ['module', 'name']
	def get_save_return_url(self, model, is_created):
		# Parameters
		#   • model – Saved object
		#   • is_created – Whether new object was created or existing one was updated
		precentage = model
		semester_id = precentage.module.unit.semester.id
		return url_for('conf', semester_id=semester_id)

admin.add_view(S(Semester, db.session))
admin.add_view(U(Unit, db.session))
admin.add_view(M(Module, db.session))
admin.add_view(P(Percentage, db.session))

admin.add_view(ModelView(Type, db.session))

from app import routes, routesSession, routesGrade, routesTree, routesAnnual,\
	routesBasicTables, routesConfig, routesCalculation, models, errors

