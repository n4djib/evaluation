from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import StudentFormCreate, StudentFormUpdate, RegistrationForm, LoginForm
from app.models import Student, User, Branch, Session, Wilaya
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
import datetime
# from flask_breadcrumbs import register_breadcrumb

from app.permissions_and_roles import *



@app.route('/')
@app.route('/index/')
# @admin_permission.require()
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


SEPARATOR = '-'

@app.route('/student/create/', methods=['GET', 'POST'])
def students_create():
    form = StudentFormCreate()
    if form.validate_on_submit():
        student = Student(
            username=form.username.data,
            last_name=form.last_name.data, 
            first_name=form.first_name.data,
            email=form.email.data, 
            birth_date=form.birth_date.data,
            branch_id=form.branch_id.data,
            wilaya_id=form.wilaya_id.data)
        db.session.add(student)
        db.session.commit()
        flash('Student Created and Saved Successfully.')
        return redirect(url_for('student_index'))
    elif request.method == 'GET':
        # form.username.data = form.get_username('SF', str(datetime.datetime.now().year))
        form.username.data = Student.get_username('**', str(datetime.datetime.now().year), SEPARATOR)
    return render_template('student/create.html', title='Student Create', form=form)


@app.route('/student/get-username/', methods=['POST'])
def student_get_username():
    branch_id = request.json
    branch = Branch.query.filter_by(id=branch_id).first()
    branch_name = Student.get_username(branch.name, str(datetime.datetime.now().year), SEPARATOR)
    return str(branch_name)


##################################
#
#  move these methods to Models
#
##################################
def get_wilayas_list():
    wilayas = Wilaya.query.all()
    wilayas_name_list = ['']
    for wilaya in wilayas:
        wilayas_name_list.append(wilaya.name)
    return wilayas_name_list

def get_username_list():
    students = Student.query.all()
    username_list = []
    for student in students:
        username_list.append(student.username)
    return username_list

def get_branches_list():
    branches = Branch.query.all()
    branch_list = []
    for branch in branches:
        branch_list.append(branch.name)
    return branch_list

@app.route('/student/create-many/', methods=['GET', 'POST'])
def students_create_many():
    data = []
    i = 0
    while i < 3 :
        data.append(['', '', '', '', '', '', ''])
        i += 1

    return render_template('student/create-many.html', 
        title='Student Create Many', 
        data=data, 
        wilayas_name_list=get_wilayas_list(), 
        username_list=get_username_list(),
        branch_list=get_branches_list(),
        branches=Branch.query.all())

@app.route('/create-many-student/save/', methods = ['POST'])
def create_many_student_save():
    data_arr = request.json

    _return_print = ''

    for i, data in enumerate(data_arr, start=0):
        username_list = get_username_list()
        if data[0] != '' and data[0] not in username_list:
            student = Student(
                username=data[0].lstrip().rstrip(),
                last_name=data[1].lstrip().rstrip(), 
                first_name=data[2].lstrip().rstrip(), 
                # birth_date=data[3], 
                birth_place=data[4])

            # student.email = student.last_name+'_'+student.first_name+'@gmail.com'
            # student.birth_date = datetime.datetime.strptime(data[3], "%d/%m/%Y").strftime("%Y-%m-%d")
            try:
                student.birth_date = datetime.datetime.strptime(data[3], "%d/%m/%Y")
            except ValueError:
                student.birth_date = None

            # get branch
            # FIX: it will get the first branch
            # index = data[0].index('-')
            # if index >= 0:
            #     name = data[0][:index]
            #     branch = Branch.query.filter_by(name=name).first()
            #     student.branch_id = branch.id
            student.branch_id = data[6]

            # get wilaya
            wilaya = Wilaya.query.filter_by(name=data[5]).first()
            if wilaya != None:
                student.wilaya_id = wilaya.id

            try:
                db.session.add(student)
                db.session.commit()

                _return_print += student.username + '-' + student.last_name + '-' + \
                    student.first_name + '-' + str(data[3]) + '-' + \
                    str(student.birth_place) + '-' + str(student.email) + '-' + \
                    str(student.branch_id) + '-' + str(student.wilaya_id) 
                _return_print += '\n'
            except:
                _return_print += 'error\n'

    # return false;

    flash('Many Students has been Saved...')
    return _return_print
    return 'data saved'

@app.route('/student/edit/<id>/', methods=['GET', 'POST'])
def student_edit(id):
    student = Student.query.filter_by(id=id).first()
    # student = Student.find(id)
    form = StudentFormUpdate(student.id)
    if form.validate_on_submit():
        student.username = form.username.data
        student.last_name = form.last_name.data
        student.first_name = form.first_name.data
        student.email = form.email.data
        student.birth_date = form.birth_date.data
        student.branch_id = form.branch_id.data
        student.wilaya_id = form.wilaya_id.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('student_index'))
    elif request.method == 'GET':
        form.username.data = student.username
        form.last_name.data = student.last_name
        form.first_name.data = student.first_name
        form.email.data = student.email
        form.birth_date.data = student.birth_date
        form.branch_id.data = student.branch_id
        form.wilaya_id.data = student.wilaya_id

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




