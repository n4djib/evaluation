from app import app, db
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from app.models import User, Student, Phone, School, Branch, Promo, \
	StudentSession, Session, Grade, Semester, Unit, Module, Percentage, Type
from flask import url_for
from datetime import datetime


admin = Admin(app, template_mode='bootstrap3')

# admin.add_view(ModelView(Student, db.session))
admin.add_view(ModelView(Phone, db.session))
admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(School, db.session))
# admin.add_view(ModelView(Branch, db.session))
# admin.add_view(ModelView(Promo, db.session))
# admin.add_view(ModelView(StudentSession, db.session))
admin.add_view(ModelView(Session, db.session))
# admin.add_view(ModelView(Grade, db.session))
admin.add_view(ModelView(Type, db.session))

class S(ModelView):
	form_excluded_columns = ['next_semester', 'units', 'sessions', 'branch', '', '', '']
	def get_save_return_url(self, model, is_created):
		semester = model
		semester.latest_update = datetime.utcnow()
		db.session.commit()
		return url_for('conf', semester_id=semester.id)
class U(ModelView):
	form_excluded_columns = ['modules', 'grade_units', 'semester']
	def get_save_return_url(self, model, is_created):
		unit = model
		semester = unit.semester
		semester.latest_update = datetime.utcnow()
		db.session.commit()
		return url_for('conf', semester_id=semester.id)
class M(ModelView):
	form_excluded_columns = ['percentages', 'grades', 'unit', 'module_sessions']
	def get_save_return_url(self, model, is_created):
		module = model
		semester = module.unit.semester
		semester.latest_update = datetime.utcnow()
		db.session.commit()
		return url_for('conf', semester_id=semester.id)
class P(ModelView):
	form_excluded_columns = ['module', 'name']
	# column_editable_list = ['name', 'percentage', 'type']
	column_filters = ['module', 'name']
	def get_save_return_url(self, model, is_created):
		# Parameters
		#   • model – Saved object
		#   • is_created – Whether new object was created or existing one was updated
		precentage = model
		semester = precentage.module.unit.semester
		semester.latest_update = datetime.utcnow()
		db.session.commit()
		return url_for('conf', semester_id=semester.id)

admin.add_view( S(Semester, db.session) )
admin.add_view( U(Unit, db.session) )
admin.add_view( M(Module, db.session) )
admin.add_view( P(Percentage, db.session) )


