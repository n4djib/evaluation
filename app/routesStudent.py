from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import StudentFormCreate, StudentFormUpdate, StudentFormUpdateCostum, RegistrationForm, LoginForm
from app.models import Student, StudentSession, AnnualSession, User, Branch, Session, Wilaya, School, Module
from flask_breadcrumbs import register_breadcrumb
from datetime import datetime







#######################################
#####                             #####
#####           Student           #####
#####                             #####
#######################################


# @app.route('/student/')
# @register_breadcrumb(app, '.basic.student', 'Students')
# def student_index():
#     students = Student.query.all()
#     return render_template('student/index.html', title='Students List', students=students)


@app.route('/student/')
@register_breadcrumb(app, '.basic.student', 'Students')
def student_index():
    all_students = Student.query.all()

    renegades = []
    for student in all_students:
        student.empty = False
        sessions = student.get_sessions_ordered()
        if len(sessions) == 0:
            student.empty = True
            renegades.append(student)

    students = renegades
    for student in all_students:
        if student not in renegades:
            students.append(student)

    return render_template('student/index.html', title='Students List', students=renegades)
    # return render_template('student/index.html', title='Students List', students=students)



SEPARATOR = '-'

@app.route('/student/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.student.create', 'Create')
def students_create():
    form = StudentFormCreate()

    if request.method == 'POST':
        birth_date_request = request.form.get('birth_date_str')
        if birth_date_request != None and birth_date_request != '':
            birth_date_string = str(birth_date_request)
            form.birth_date.data = datetime.strptime(birth_date_string, '%Y-%m-%d')
    
    if form.validate_on_submit():
        student = Student(
            username=form.username.data,
            last_name=form.last_name.data, 
            first_name=form.first_name.data,
            last_name_arab=form.last_name_arab.data,
            first_name_arab=form.first_name_arab.data,
            email=form.email.data,
            birth_date=form.birth_date.data,
            birth_place=form.birth_place.data,
            address=form.address.data,
            branch_id=form.branch_id.data,
            wilaya_id=form.wilaya_id.data,
            sex=form.sex.data,
            residency=form.residency.data)
        if student.email == '':
            student.email = None 

        db.session.add(student)
        db.session.commit()
        flash('Student Created and Saved Successfully.')
        # return redirect(url_for('student_index'))
        return redirect(url_for('student_view', id=student.id))
    elif request.method == 'GET':
        # form.username.data = form.get_username('SF', str(datetime.datetime.now().year))
        form.username.data = Student.get_username('**', str(get_current_year()), SEPARATOR)
    return render_template('student/create.html', title='Student Create', form=form)

def get_current_year():
    this_year = datetime.now().year
    if datetime.now().month < 8:
        this_year = this_year - 1
    return this_year

@app.route('/student/get-username/', methods=['POST'])
def student_get_username():
    branch_id = request.json
    branch = Branch.query.filter_by(id=branch_id).first()
    branch_name = Student.get_username(branch.name, str(get_current_year()), SEPARATOR)
    return str(branch_name)

@app.route('/student/update/<id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.student.update', 'Update')
def student_update(id):
    student = Student.query.get_or_404(id)
    form = StudentFormUpdate(student.id)

    ### this disallow username change
    if student.allow_username_change() != True:
        form = StudentFormUpdateCostum(student.id)
        form.username.data = student.username

    # to convert birth_date
    if request.method == 'POST':
        birth_date_request = request.form.get('birth_date_str')
        if birth_date_request != None and birth_date_request != '':
            birth_date_string = str(birth_date_request)
            form.birth_date.data = datetime.strptime(birth_date_string, '%Y-%m-%d')

    if form.validate_on_submit():
        student.username = form.username.data
        student.last_name = form.last_name.data
        student.first_name = form.first_name.data
        student.last_name_arab = form.last_name_arab.data
        student.first_name_arab = form.first_name_arab.data
        if len(form.email.data) > 0:
            student.email = form.email.data
        student.birth_date = form.birth_date.data
        student.birth_place = form.birth_place.data
        student.address = form.address.data
        student.branch_id = form.branch_id.data
        student.wilaya_id = form.wilaya_id.data
        student.sex = form.sex.data
        student.residency = form.residency.data
        db.session.commit()
        flash('Your changes have been saved.')
        # return redirect(url_for('student_index'))
        return redirect(url_for('student_view', id=student.id))
    elif request.method == 'GET':
        form.username.data = student.username
        form.last_name.data = student.last_name
        form.first_name.data = student.first_name
        form.last_name_arab.data = student.last_name_arab
        form.first_name_arab.data = student.first_name_arab
        form.email.data = student.email
        form.birth_date.data = student.birth_date
        form.birth_place.data = student.birth_place
        form.address.data = student.address
        form.branch_id.data = student.branch_id
        form.wilaya_id.data = student.wilaya_id
        form.sex.data = student.sex
        form.residency.data = student.residency
    return render_template('student/update.html', title='Student Update', form=form)

@app.route('/student/view/<id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.student.view', 'View')
def student_view(id):
    student = Student.query.get_or_404(id)
    return render_template('student/view.html', title='Student View', student=student)

@app.route('/student/delete/<id>/', methods=['GET', 'POST'])
def student_delete(id):
    student = Student.query.get_or_404(id)
    if len(student.student_sessions) > 0:
        flash("you can't delete this Student because it is in Relation with other Records", 'alert-danger')
        flash("you have to break the relation with the Sessions first")
        return redirect(url_for('student_view', id=student.id))
    db.session.delete(student)
    db.session.commit()
    flash('Student: ' + student.username + ' - ' \
        + student.last_name + ' ' + student.last_name + ' is deleted', 'alert-success')
    return redirect(url_for('student_index'))


#######################################
#
#  move these methods to Models
#
#######################################


# 
# 
# 
# turn this into static in model
# 
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
@register_breadcrumb(app, '.basic.student.create_many', 'Create Many')
def students_create_many():
    data = []
    i = 0
    while i < 10:
        # data.append(['', '', '', '', '', ''])
        data.append([None, None, None, None, None, None])
        i += 1

    return render_template('student/create-many.html', 
        title='Student Create Many', 
        data=data, 
        wilayas_name_list=get_wilayas_list(), 
        username_list=get_username_list(),
        branch_list=get_branches_list(),
        branches=Branch.query.all())

@app.route('/student/create-many/save/', methods = ['POST'])
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
                # birth_date=, 
                birth_place=data[4])

            if data[3] != None and data[3] != '':
                student.birth_date = datetime.datetime.strptime(data[3], "%d/%m/%Y")

            student.branch_id = data[6]


            wilaya = Wilaya.query.filter_by(name=data[5]).first()
            if wilaya != None:
                student.wilaya_id = wilaya.id
            else:
                student.wilaya_id = None

            ###############

            try:
                db.session.add(student)
                # db.session.commit()
                _return_print += student.username + '-' + student.last_name + '-' + \
                    student.first_name + '-' + 'str(data[3])' + '-' + \
                    str(student.birth_place) + '-' + str(student.email) + '-' + \
                    str(student.branch_id) + '-' + str(student.wilaya_id) 
                _return_print += '\n'
            except:
                _return_print += 'error\n'

    # end for

    db.session.commit()

    flash('Many Students has been Saved...')
    return _return_print
    return 'data saved'



#######################################
#            update_many              #

@app.route('/session/<session_id>/update-many-student-username/t/<template>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/update-many-student-username/', methods=['GET', 'POST'])
def update_many_username_ordered(session_id, template=''):
    # check change is allowed
    session = Session.query.get_or_404(session_id)
    promo_has_closed = session.promo.has_closed_session()
    if promo_has_closed == True:
        flash("you can't Update the Usernames because ********")
        return redirect( url_for('students_update_many', session_id=session_id) )
        
    # get the Username Template
    if template == '':
        branch_name = session.promo.branch.name
        start_date = session.promo.start_date
        if start_date == None:
            start_date = datetime.now()
        template = branch_name+'-'+str(start_date.year)+'-'

    # get the students to change in the Session or Promo
    students = Student.query.join(StudentSession).filter_by(session_id=session_id).all()

    # change to somthing nutral
    for student in students:
        student.username = 'tmp-'+student.username
    db.session.commit()

    # order and rename 
    students = Student.query.join(StudentSession)\
        .filter_by(session_id=session_id)\
        .order_by(Student.last_name, Student.first_name).all()

    i = 1
    for student in students:
        # get username and check it doesn't exist
        while True:
            new_student = template + str(i)
            if i < 10:
                new_student = template + '0' + str(i)

            s = Student.query.filter_by(username=new_student).first()
            if s == None:
                student.username = new_student
                i += 1
                break
            else:
                flash('There is a Name Conflict - ' + new_student, 'alert-warning')
                i += 1

    db.session.commit()

    flash('Ordered and renamed', 'alert-success')
    return redirect(url_for('students_update_many', session_id=session_id))

@app.route('/session/<session_id>/update-many-student/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.update_many', 'Update Many')
def students_update_many(session_id):
    student_sessions = StudentSession.query.filter_by(session_id=session_id).all()

    data = []

    for student_session in student_sessions:
        student = student_session.student
        birth_date = None
        wilaya = None

        if student.birth_date != None:
            birth_date = student.birth_date.strftime("%d/%m/%Y")
        if student.wilaya != None:
            wilaya = str(student.wilaya.name)

        link = '<a href="'+url_for('student_view', id=student.id)+'" target="_blank">'
        link += student.last_name + ' - ' + student.first_name
        link += '</a>'

        data.append([
            student.id,
            student.username, 
            # student.last_name, 
            link, 
            student.first_name, 
            birth_date, 
            student.birth_place, 
            wilaya
        ])

    # disallow username change
    session = Session.query.get_or_404(session_id)
    promo_has_closed = session.promo.has_closed_session()

    return render_template('student/update-many.html', 
        title='Student Update Many', 
        data=data, 
        wilayas_name_list=get_wilayas_list(), 
        username_list=get_username_list(),
        branch_list=get_branches_list(),
        branches=Branch.query.all(),
        session_id=session_id,
        promo_has_closed=promo_has_closed
        )

@app.route('/student/update-many/save/', methods = ['POST'])
def update_many_student_save():
    data_arr = request.json

    for i, data in enumerate(data_arr, start=0):
        #
        #
        username_list = get_username_list()
        # if data[0] != '' and data[1] not in username_list:
        if data[0] != '':
            student = Student.query.get_or_404(data[0])

            # allow username change
            if student.allow_username_change() == True:
                student.username = data[1].lstrip().rstrip()

            # last_name = data[2].lstrip().rstrip()
            # first_name = data[6].lstrip().rstrip()
            student.birth_place = data[5]

            if data[4] != None and data[4] != '':
                student.birth_date = datetime.datetime.strptime(data[4], "%d/%m/%Y")

            wilaya = Wilaya.query.filter_by(name = data[6]).first()
            if wilaya != None:
                student.wilaya_id = wilaya.id
            else:
                student.wilaya_id = None

            db.session.commit()
    
    flash('Data has been Updated ...')
    return 'data updated'


@app.route('/session/<session_id>/update-many-name-case/case/<case>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/update-many-name-case/', methods=['GET', 'POST'])
def update_many_name_case(session_id, case=''):
    # check change is allowed
    session = Session.query.get_or_404(session_id)
    # promo_has_closed = session.promo.has_closed_session()
    # if promo_has_closed == True:
    #     flash("you can't Update the Names Because ****+++****")
    #     return redirect( url_for('students_update_many', session_id=session_id) )


    # get the students to change in the Session or Promo
    students = Student.query.join(StudentSession).filter_by(session_id=session_id).all()

    for student in students:
        student.last_name = student.last_name.upper()
        student.first_name = student.first_name.capitalize()

    db.session.commit()

    flash('Ordered and renamed', 'alert-success')
    return redirect(url_for('students_update_many', session_id=session_id))


