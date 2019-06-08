from app import app, db
from flask_admin import Admin, BaseView, expose
from flask_admin.form import rules
from flask_admin.contrib.sqla import ModelView
from app.models import User, Student, Phone, School, Branch, Promo, \
	StudentSession, Session, Grade, Semester, Unit, Module, Percentage, Type
from flask import url_for 
# , request, current_app
from datetime import datetime



admin = Admin(app, template_mode='bootstrap3')

# admin.add_view(ModelView(Student, db.session))
# admin.add_view(ModelView(Phone, db.session))
# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(School, db.session))
# admin.add_view(ModelView(Branch, db.session))
# admin.add_view(ModelView(Promo, db.session))
# admin.add_view(ModelView(StudentSession, db.session))
# admin.add_view(ModelView(Session, db.session))
# admin.add_view(ModelView(Grade, db.session))
# admin.add_view(ModelView(Type, db.session))


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
	<div>
		<a id="btn-{action}" href="************" class="btn {btn}" >
		{label}
		</a>

		<!-- -->

		{js}
	</div>
	</br>
	"""
	return button


class S(ModelView):
	can_create = False
	form_excluded_columns = ['next_semester', 'units', 'sessions', 'branch']
	# form_edit_rules = ("name")
	def __init__(self, model, session, **kwargs):
		new_label = '<img src="/static/img/new_yellow.ico"> Add a New Unit' 
		new_button = make_button(model, 'create', 'semester', new_label)
		self.form_edit_rules = (
		    "name", 
		    "display_name", 
		    rules.HTML( new_button  ),
		)
		super(S, self).__init__(model, session, **kwargs)

class U(ModelView):
	can_create = False
	form_excluded_columns = ['modules', 'grade_units', 'semester']
	form_edit_rules = ("name")
	def __init__(self, model, session, **kwargs):
		new_label = '<img src="/static/img/new_yellow.ico"> Add a New Module' 
		new_button = make_button(model, 'create', 'unit', new_label)
		del_button = make_button(model, 'delete', 'unit', 'Delete this Unit', btn='btn-danger')
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

class M(ModelView):
	can_create = False
	form_excluded_columns = ['percentages', 'grades', 'unit', 'module_sessions']
	form_edit_rules = ("name")
	def __init__(self, model, session, **kwargs):
		new_label = '<img src="/static/img/new_yellow.ico"> Add a New Percentage' 
		new_button = make_button(model, 'create', 'module', new_label)
		del_button = make_button(model, 'delete', 'module', 'Delete this Module', btn='btn-danger')
		self.form_edit_rules = (
		    "code", 
		    "name", 
		    "display_name", 
		    "coefficient", 
		    "credit", 
		    "time", 
		    "order", 
		    rules.HTML( new_button  ),
		    rules.HTML( del_button ),
		)
		super(M, self).__init__(model, session, **kwargs)

class P(ModelView):
	can_create = False
	form_excluded_columns = ['module', 'name']
	# column_editable_list = ['name', 'percentage', 'type']
	column_filters = ['module', 'name']
	# def get_save_return_url(self, model, is_created):
	# 	# Parameters
	# 	#   • model – Saved object
	# 	#   • is_created – Whether new object was created or existing one was updated
	# 	precentage = model
	# 	semester = precentage.module.unit.semester
	# 	semester.latest_update = datetime.utcnow()
	# 	db.session.commit()
	# 	return url_for('conf_semester', semester_id=semester.id)
	form_edit_rules = ("name")
	def __init__(self, model, session, **kwargs): 
		del_button = make_button(model, 'delete', 'percentage', 'Delete this Percentage', btn='btn-danger')
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


admin.add_view( S(Semester, db.session) )
admin.add_view( U(Unit, db.session, url='/admin/unit') )
admin.add_view( M(Module, db.session) )
admin.add_view( P(Percentage, db.session) )

