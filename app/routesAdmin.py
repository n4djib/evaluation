from app import app, db
from flask import url_for
from flask_admin import Admin
from flask_admin.form import rules
from flask_admin.contrib.sqla import ModelView
from app.models import User, Student, Phone, School, Branch, Promo, \
	StudentSession, Session, Grade, Semester, Unit, Module, Percentage, Type
from datetime import datetime



admin = Admin(app, template_mode='bootstrap3')



def make_button(model, action, _type, label, btn='btn-success'):
	js = """
	  <script>
		function getURLParameter(name) {
		  return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [null, ''])[1].replace(/\+/g, '%20')) || null;
		}
		var id = getURLParameter('id');
		var elem = document.getElementById('btn-"""+action+"""');
		elem.setAttribute('href', '/"""+action+"""-node-for-config-tree/"""+_type+"""/id/'+id+'/');
	  </script>
	"""

	button = F"""
		<a id="btn-{action}" href="***" class="btn {btn} btn-xs"  style="float:right; margin:2px;">
		{label}
		</a>
		<!-- -->
		{js}
	"""
	return button

class S(ModelView):
	form_excluded_columns = ['units', 'sessions', 'branch']
	can_create = False
	can_delete = False
	def __init__(self, model, session, **kwargs):
		# new_label = '<img src="/static/img/new_yellow.ico"> Add a New Unit'
		new_label = '<img src="/static/img/New-16.png"> Add Unit' 
		new_button = make_button(model, 'create', 'semester', new_label)
		self.form_edit_rules = (
		    "name", 
		    "display_name", 
		    "semester", 
		    rules.HTML( new_button  ),
		)
		super(S, self).__init__(model, session, **kwargs)
	def get_save_return_url(self, model, is_created):
		semester = model
		semester.latest_update = datetime.utcnow()
		db.session.commit()
		return url_for('conf_semester', semester_id=semester.id)

class U(ModelView):
	form_excluded_columns = ['modules', 'grade_units', 'semester']
	can_create = False
	can_delete = False
	def __init__(self, model, session, **kwargs):
		# new_label = '<img src="/static/img/new_yellow.ico"> Add a New Module' 
		new_label = '<img src="/static/img/New-16.png"> Add Module' 
		new_button = make_button(model, 'create', 'unit', new_label)
		del_button = make_button(model, 'delete', 'unit', 'Delete Unit', btn='btn-danger')
		self.form_edit_rules = (
		    "name", 
		    "display_name", 
		    "unit_coefficient", 
		    "is_fondamental", 
		    "order", 
		    rules.HTML( new_button  ),
		    rules.HTML( del_button ),
		)
		super(U, self).__init__(model, session, **kwargs)
	def get_save_return_url(self, model, is_created):
		unit = model
		semester = unit.semester
		semester.latest_update = datetime.utcnow()
		db.session.commit()
		# return url_for('conf_semester', semester_id=semester.id)
		return url_for('conf_semester', semester_id=semester.id, type='unit', id=unit.id)

class M(ModelView):
	form_excluded_columns = ['percentages', 'grades', 'unit', 'module_sessions']
	# form_excluded_columns = ['grades', 'unit', 'module_sessions']
	can_create = False
	can_delete = False
	# inline_models = [Percentage]
	def __init__(self, model, session, **kwargs):
		# new_label = '<img src="/static/img/new_yellow.ico"> Add a New Percentage' 
		new_label = '<img src="/static/img/New-16.png"> Add Percentage' 
		new_button = make_button(model, 'create', 'module', new_label)
		del_button = make_button(model, 'delete', 'module', 'Delete Module', btn='btn-danger')
		self.form_edit_rules = (
		    "code", 
		    "name", 
		    "display_name", 
		    "coefficient", 
		    "credit", 
		    "time", 
		    "order", 
		    # "percentages",
		    rules.HTML( new_button  ),
		    rules.HTML( del_button ),
		)
		super(M, self).__init__(model, session, **kwargs)
	def get_save_return_url(self, model, is_created):
		module = model
		semester = module.unit.semester
		semester.latest_update = datetime.utcnow()
		db.session.commit()
		# return url_for('conf_semester', semester_id=semester.id)
		return url_for('conf_semester', semester_id=semester.id, type='module', id=module.id)

class P(ModelView):
	form_excluded_columns = ['module', 'name']
	# column_editable_list = ['name', 'percentage', 'type']
	column_filters = ['module', 'name']
	can_create = False
	can_delete = False
	def __init__(self, model, session, **kwargs): 
		del_button = make_button(model, 'delete', 'percentage', 'Delete Percentage', btn='btn-danger')
		self.form_edit_rules = (
		    # "name", 
		    "type", 
		    "percentage", 
		    "time", 
		    "rattrapable", 
		    "order", 
		    rules.HTML( del_button ),
		)
		super(P, self).__init__(model, session, **kwargs)
	def get_save_return_url(self, model, is_created):
		# Parameters
		#   • model – Saved object
		#   • is_created – Whether new object was created or existing one was updated
		precentage = model
		semester = precentage.module.unit.semester
		semester.latest_update = datetime.utcnow()
		db.session.commit()
		# return url_for('conf_semester', semester_id=semester.id)
		return url_for('conf_semester', semester_id=semester.id, type='precentage', id=precentage.id)

class T(ModelView):
	form_excluded_columns = ['percentages']
	can_create = False
	can_delete = False

admin.add_view( S(Semester, db.session) )
admin.add_view( U(Unit, db.session) )
admin.add_view( M(Module, db.session) )
admin.add_view( P(Percentage, db.session) )
admin.add_view( T(Type, db.session) )


# admin.add_view(ModelView(Student, db.session))
# admin.add_view(ModelView(Phone, db.session))
# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(School, db.session))
# admin.add_view(ModelView(Branch, db.session))
# admin.add_view(ModelView(Promo, db.session))
# admin.add_view(ModelView(StudentSession, db.session))
# admin.add_view(ModelView(Session, db.session))
# admin.add_view(ModelView(Grade, db.session))

