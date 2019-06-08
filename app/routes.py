from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.models import Student, AnnualSession, User
# from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from flask_breadcrumbs import register_breadcrumb
from flask_principal import Identity, AnonymousIdentity, identity_changed
from app.permissions_and_roles import *








@app.route('/code-change-case/')
def run_code_case():
    students = Student.query.all()
    for student in students:
        student.last_name = student.last_name.upper().strip()
        student.first_name = student.first_name.capitalize().strip()
    db.session.commit()
    return 'excuted code-change-case'


@app.route('/code-fill-annual/')
def run_code_annual():
    annual_sessions = AnnualSession.query.all()
    for annual_session in annual_sessions:
        if annual_session.annual_id == None:
            annual_session.annual_id = annual_session.sessions[0].semester.annual.annual
    db.session.commit()
    return 'excuted code-fill-annual-id'





@app.route('/calendar/')
def calendar():
    return render_template('calendar.html', title='Welcome Page')


@app.route('/student/promos/<id>/')
def student_promos(id):
    student = Student.query.get_or_404(id)
    promos = student.get_promos()
    return str(promos)




# # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # # 
# # # # # # # # # # # # # # # # # # # # #  



@app.route('/')
@app.route('/index/')
# @admin_permission.require()
@register_breadcrumb(app, '.', 'Home')
def index():
    return render_template('index.html', title='Welcome Page')


@app.route('/slow-redirect/', methods=['GET', 'POST'])
def slow_redirect():
    url = request.args.get('url', default='**', type=str)
    message = request.args.get('message', default='', type=str)
    gif = request.args.get('gif', default='Preloader_8_2', type=str)
    if message != None and message != '':
        flash(message)

    return render_template('slow-redirect.html', title='Redirect Page', url=url, message=message, gif=gif)


#######################################



@app.route('/login/', methods=['GET', 'POST'])
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
        identity_changed.send(app, identity=Identity(user.id))

        return redirect(url_for('index'))
    return render_template('user/login.html', title='Sign In', form=form)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register/', methods=['GET', 'POST'])
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


