from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import StudentFormCreate, StudentFormUpdate, RegistrationForm, LoginForm
from app.models import Student, User, Branch, Session
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
# from flask_breadcrumbs import register_breadcrumb


@app.route('/')
@app.route('/index/')
# @register_breadcrumb(app, '.', 'Home')
def index():
    return render_template('index.html', title='Welcome Page')

# @app.route('/grid/')
# def grid():
#     return render_template('grid.html', title='Welcome Page')

@app.route('/student/')
@app.route('/student/index/')
def student_index():
    students = Student.query.all()
    return render_template('student/index.html', title='Students List', students=students)

@app.route('/student/create/', methods=['GET', 'POST'])
def students_create():
    form = StudentFormCreate()
    if form.validate_on_submit():
        student = Student(username=form.username.data,
            last_name=form.last_name.data, first_name=form.first_name.data,
            email=form.email.data, birth_date=form.birth_date.data)
        db.session.add(student)
        db.session.commit()
        flash('Student Created and Saved Successfully.')
        return redirect(url_for('student_index'))
    elif request.method == 'GET':
        ################
        ################
        ################
        form.username.data = form.get_username('SF', '2017')
        ################
        ################
        ################
    return render_template('student/create.html', title='Student Create', form=form)

@app.route('/student/create-many/', methods=['GET', 'POST'])
def students_create_many():
    forms = []
    for x in range(0, 1):
        forms = StudentFormCreate()

    # if form.validate_on_submit():
    #     student = Student(username=form.username.data,
    #         last_name=form.last_name.data, first_name=form.first_name.data,
    #         email=form.email.data, birth_date=form.birth_date.data)
    #     db.session.add(student)
    #     db.session.commit()
    #     flash('Student Created and Saved Successfully.')
    #     return redirect(url_for('student_index'))
    # elif request.method == 'GET':
    #     form.username.data = form.get_username('ISP', '2018')

    return render_template('student/create-many.html', title='Student Create Many', forms=forms)

@app.route('/student/edit/<id>/', methods=['GET', 'POST'])
def student_edit(id):
    # student = Student.query.filter_by(id=id).first()
    student = Student.find(id)

    form = StudentFormUpdate(student.id)
    if form.validate_on_submit():
        student.username = form.username.data
        student.last_name = form.last_name.data
        student.first_name = form.first_name.data
        student.email = form.email.data
        student.birth_date = form.birth_date.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('student_index'))
    elif request.method == 'GET':
        form.username.data = student.username
        form.last_name.data = student.last_name
        form.first_name.data = student.first_name
        form.email.data = student.email
        form.birth_date.data = student.birth_date
    return render_template('student/edit.html', title='Student Update', form=form)

@app.route('/student/view/<id>/', methods=['GET', 'POST'])
def student_view(id):
    return '<h2>Student : '+id+'</h2>'


@app.route('/branch/', methods=['GET', 'POST'])
def branch_idnex():
    branches = Branch.query.all()
    return render_template('branch.html', title='Branches', branches=branches)



##############################################

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



# put html in groups
