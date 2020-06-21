from app import app, db
from flask import render_template, redirect, url_for, flash, request, jsonify #, session, g
from app.models import Student, AnnualSession, User, Notification
from app.forms import LoginForm, RegistrationForm
# from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from flask_breadcrumbs import register_breadcrumb

# from flask_principal import Identity, AnonymousIdentity, identity_changed

# from app.prencipal import *
from app.permissions_and_rules import *





# # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # 




# @app.route('/run-code')
# def run():
#     users = User.query.all()



@app.route('/')
@app.route('/index/')
# @login_required
# @admin_permission.require(http_exception=403)
@register_breadcrumb(app, '.', 'Home')
def index():
    return render_template('index.html', title='Welcome Page')



# admin_manager_permission = admin_permission.union(manager_permission)

# @app.route('/aaa/')
# @login_required
# # @admin_permission.require(http_exception=403)
# # @manager_permission.require(http_exception=403)
# # @admin_manager_permission.require(http_exception=403)
# def aaa():
#     return "aaaaaaaaaaaa"
#     # with admin_permission.require(http_exception=403):
#     # print('')
#     # print(str(session))
#     # print('')
#     # return str(session['user_id'])


@app.route('/permission/')
@login_required
# @RolePermission('manager')
# @RolesAcceptedPermission(['admin', 'manager', 'grader'])
# @RolesRequiredPermission(['admin', 'manager', 'grader'])
def permission():
    session_id = 78
    permission = AttendancePermission(session_id)
    if not permission.check():
        return permission.deny()

    roles = '</br>'
    for role in current_user.roles:
        roles = roles + '</br> - '+role.name
    return "permission" + roles



# # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # #

# _insecure_views = ['login', 'register']
_insecure_views = []

@app.before_request
def before_request():
    if not current_user.is_authenticated:
        if request.endpoint not in _insecure_views:
            return redirect(url_for('login'))
    else:
        check_request_permission()


_admin_only_views = ['']

def check_request_permission():
    if request.endpoint in _admin_only_views:
        # with RolesRequiredPermission:
        permission = RolePermission("admin")
        if not permission.check():
            return permission.deny()
    



def login_not_required(fn):
    '''decorator to disable user authentication'''
    endpoint = fn.__name__
    _insecure_views.append(endpoint)
    return fn


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
#######################################

@app.route('/notifications', methods=['GET'])
@login_not_required
def notifications():
    notifications = Notification.query.all()

    msg = []
    for notification in notifications:
        # remove this later and add the correct url when inserting
        make_delete_notificaion_url(notification)

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

def make_delete_notificaion_url(notification):
    notification.delete_url = url_for('remove_notification', id=notification.id)
    db.session.commit()
    return notification.delete_url

#######################################
#######################################


@app.route('/login/', methods=['GET', 'POST'])
@login_not_required
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    print('1111111111111')
    if form.validate_on_submit():
        print('22222222222222')
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        
        # # Tell Flask-Principal the identity changed
        # identity_changed.send(app, identity=Identity(user.id))

        return redirect(request.args.get('next') or '/')
    return render_template('user/login.html', title='Sign In', form=form)

@app.route('/logout/')
@login_not_required
def logout():
    logout_user()
    
    # # Remove session keys set by Flask-Principal
    # for key in ('identity.name', 'identity.auth_type'):
    #     session.pop(key, None)

    # # Tell Flask-Principal the user is anonymous
    # identity_changed.send(app, identity=AnonymousIdentity())

    return redirect(request.args.get('next') or '/')

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


