from app import app, db
from flask import render_template, redirect, url_for, flash, request, jsonify
from app.models import Student, AnnualSession, User, Notification
from app.forms import LoginForm, RegistrationForm
# from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from flask_breadcrumbs import register_breadcrumb
from flask_principal import Identity, AnonymousIdentity, identity_changed
from app.permissions_and_roles import *





# # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # #

# _insecure_views = ['login', 'register']
_insecure_views = []

@app.before_request
def before_request():
    if not current_user.is_authenticated:
        if request.endpoint not in _insecure_views:
            return redirect(url_for('login'))


def login_not_required(fn):
    '''decorator to disable user authentication'''
    endpoint = fn.__name__
    _insecure_views.append(endpoint)
    return fn


# # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # 


@app.route('/')
@app.route('/index/')
# @admin_permission.require()
# @login_required
@register_breadcrumb(app, '.', 'Home')
def index():
    return render_template('index.html', title='Welcome Page')



# @app.route('/')
# @app.route('/form-builder/')
# # @admin_permission.require()
# # @login_required
# # @register_breadcrumb(app, '.', 'Home')
# def form_builder():
#     return render_template('test-form-builder.html', title='test-form-builder')


from app.models import School, Branch, Semester, Module, Promo, Session, ModuleSession

# @app.route('/select-list/')
# @app.route('/select-list/sc/<sc_id>/bra/<bra_id>/pr/<pr_id>/sem/<sem_id>')
@app.route('/select-list/')
@app.route('/select-list/school/<school_id>')
@app.route('/select-list/branch/<branch_id>')
@app.route('/select-list/promo/<promo_id>')
@app.route('/select-list/session/<session_id>')
def select_list_calendar(school_id=0, branch_id=0, promo_id=0, session_id=0):
    school = branch = promo = session = None

    # from semester conclude annual and bring both semesters
    if session_id != 0:
        session = Session.query.get_or_404(session_id)
        promo_id = session.promo_id
    if promo_id != 0:
        promo = Promo.query.get_or_404(promo_id)
        branch_id = promo.branch_id
    if branch_id != 0:
        branch = Branch.query.get_or_404(branch_id)
        school_id = branch.school_id
    if school_id != 0:
        school = School.query.get_or_404(school_id)

    return render_template('select-list-module-calendar.html',
        school=school, branch=branch, promo=promo, session=session)


def make_html_options(_list, name):
    html_options = '<option value="">Select '+name+'</option>'
    for l in _list:
        html_options += '<option value="'+str(l.id)+'">'+str(l.name)+'</option>'
    return html_options

@app.route('/select-options-schools', methods=['GET'])
def get_schools():
    schools = School.query.all()
    return make_html_options(schools, 'School')

@app.route('/select-options-branches-by-school/<school_id>', methods=['GET'])
def get_branches_by_school(school_id):
    school = School.query.get_or_404(school_id)
    return make_html_options(school.branches, 'Branch')

@app.route('/select-options-promos-by-branch/<branch_id>', methods=['GET'])
def get_promos_by_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    return make_html_options(branch.promos, 'Promo')

@app.route('/select-options-session-by-promo/<promo_id>', methods=['GET'])
def get_semesters_by_promo(promo_id):
    sessions = Session.query.filter_by(promo_id=promo_id)\
        .join(Semester).order_by(Semester.display_name, Session.timestamp).all()

    html_options = '<option value="">Select Semester</option>'
    for session in sessions:
        id = str(session.id)
        display_name = str(session.semester.display_name)
        historic = ' (historic)' if session.is_historic else ''
        if session.is_historic == True:
            continue
        html_options += '<option value="'+id+'">'+display_name+historic+'</option>'
    return html_options

@app.route('/select-options-module-by-session/<session_id>', methods=['GET'])
def get_modules_by_session(session_id):
    session = Session.query.get_or_404(session_id)
    # modules = Module.query.join(ModuleSession)\
    #     .filter_by(session_id=session_id).order_by(Module.code).all()

    units = session.semester.units
    modules = []
    for unit in units:
        for mod in unit.modules:
            modules.append(mod)

    html_options = '<option value="">Select Module</option>'
    for module in modules:
        html_options += '<option value="'+str(module.id)+'">'+module.code+' - '+module.name+'</option>'
    return html_options

#######################################
#######################################


@app.route('/slow-redirect/', methods=['GET', 'POST'])
def slow_redirect():
    url = request.args.get('url', default='', type=str)
    message = request.args.get('message', default='', type=str)
    gif = request.args.get('gif', default='Preloader_8_2', type=str)
    if message != None and message != '':
        flash(message)

    return render_template('slow-redirect.html', title='Redirect Page', 
        url=url, message=message, gif=gif)


#######################################

@app.route('/notifications', methods=['GET'])
@login_not_required
def notifications():
    notifications = Notification.query.all()

    msg = []
    for notification in notifications:
        # remove this later and add the correct url when inserting
        make_delete_url(notification)

        msg.append({
            'id': notification.id, 
            'title': notification.title, 
            'notification': notification.notification,
            'delete_url': notification.delete_url
        })

    return jsonify(msg)

@app.route('/notifications-remove/<int:id>/', methods=['GET', 'DELETE'])
def remove_notification(id):
    print('')
    print('remove_notification')
    notification = Notification.query.get(id)
    db.session.delete(notification)
    print('deleted '+ str(id))
    print('')
    db.session.commit()
    return 'removed'

def make_delete_url(notification):
    notification.delete_url = url_for('remove_notification', id=notification.id)
    db.session.commit()
    return notification.delete_url

#######################################
#######################################
#######################################
#######################################


@app.route('/login/', methods=['GET', 'POST'])
@login_not_required
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        # Tell Flask-Principal the identity changed
        # identity_changed.send(app, identity=Identity(user.id))

        return redirect(url_for('index'))
    return render_template('user/login.html', title='Sign In', form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register/', methods=['GET', 'POST'])
# @login_not_required
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('user/register.html', title='Register', form=form)



#######################################
#             


