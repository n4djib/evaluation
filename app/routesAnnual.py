from app import app, db
from flask import render_template, request, redirect, url_for, flash
from app.models import AnnualSession, StudentSession, AnnualGrade, Student, Session
from sqlalchemy import or_

from flask_breadcrumbs import register_breadcrumb




def get_student_annual_list(annual_session, annual_dict):
    session_1 = annual_dict['S1']
    session_2 = annual_dict['S2']
    
    student_sessions = StudentSession.query\
        .filter(StudentSession.session_id.in_([session_1, session_2]))\
        .all()
    students = [student_session.student.username for student_session in student_sessions]

    # remove duplicates & sort by username
    students = sorted(list(set(students)))

    # add student_id
    student_ids = []
    for username in students:
        student = Student.query.filter_by(username=username).first()
        student_ids.append(student.id)

    return student_ids

# call this after creating a new session and 
# and creating a new 
def init_annual_grade(annual_session_id):
    annual_session = AnnualSession.query.get(annual_session_id)
    annual_dict = annual_session.get_annual_dict()

    student_ids = get_student_annual_list(annual_session, annual_dict)
    # then fill annual grade if the record does not exist
    for student_id in student_ids:
        annual_grade = AnnualGrade.query\
            .filter_by(annual_session_id=annual_session_id, student_id=student_id)\
            .first()
        if annual_grade == None:
            annual_grade = AnnualGrade( annual_session_id=annual_session_id, student_id=student_id )
            db.session.add(annual_grade)
    db.session.commit()

    # NOTE:
    # delete users in Table Who are not supposed to be in annual
    students_annual = AnnualGrade.query.filter_by(annual_session_id=annual_session_id).all()
    students_annual_list = [s_a.student_id for s_a in students_annual]
    for student_id in students_annual_list:
        if student_id not in student_ids:
            annual_grade = AnnualGrade.query\
                .filter_by(annual_session_id=annual_session_id, student_id=student_id)\
                .first()
            db.session.delete(annual_grade)
    db.session.commit()

    return 'init_annual_grade'

def calculate_annual(annual_session_id):
    annual_session = AnnualSession.query.get(annual_session_id)
    annual_dict = annual_session.get_annual_dict()
    annual_grades = AnnualGrade.query.filter_by(annual_session_id=annual_session_id).all()

    for an in annual_grades:
        sess_1 = StudentSession.query.filter_by(
            session_id=annual_dict['S1'], student_id=an.student_id).first()
        ratt_1 = StudentSession.query.filter_by(
            session_id=annual_dict['R1'], student_id=an.student_id).first()
        sess_2 = StudentSession.query.filter_by(
            session_id=annual_dict['S2'], student_id=an.student_id).first()
        ratt_2 = StudentSession.query.filter_by(
            session_id=annual_dict['R2'], student_id=an.student_id).first()

        if sess_1 != None:
            an.s1 = sess_1.average
            an.c1 = sess_1.credit
        else:
            an.s1 = None
            an.c1 = None

        if sess_2 != None:
            an.s2 = sess_2.average
            an.c2 = sess_2.credit
        else:
            an.s2 = None
            an.c2 = None

        if ratt_1 != None:
            an.rs1 = ratt_1.average
            an.rc1 = ratt_1.credit
        else:
            an.rs1 = None
            an.rc1 = None

        if ratt_2 != None:
            an.rs2 = ratt_2.average
            an.rc2 = ratt_2.credit
        else:
            an.rs2 = None
            an.rc2 = None


        ############### average before Rattrapage
        # if sess_1 != None and sess_2 != None:
        if sess_1.average != None and sess_2.average != None:
            an.average = (sess_1.average + sess_2.average)/2
            an.credit  = sess_1.credit + sess_2.credit
        else:
            an.average = None
            an.credit  = None

        ############### average after Rattrapage
        if an.average != None and (an.rc1 != None or an.rc2 != None):
            S1 = an.s1
            C1 = an.c1
            S2 = an.s2
            C2 = an.c2
            if an.rs1 != None:
                S1 = an.rs1
                C1 = an.rc1
            if an.rs2 != None:
                S2 = an.rs2
                C2 = an.rc2
            an.average_r = (S1 + S2)/2
            an.credit_r  = C1 + C2
        else:   
            an.average_r = None
            an.credit_r  = None

    db.session.commit()
    return 'calculate_annual'

def create_data_annual_session(annual_session_id):
    annual_session = AnnualSession.query.get(annual_session_id)
    annual_dict = annual_session.get_annual_dict()
    student_ids = get_student_annual_list(annual_session, annual_dict)
    annual_grades = AnnualGrade.query.filter_by(annual_session_id=annual_session_id).all()

    # array_data = ['#', 'name', 'S1', 'R1', 'S2', 'R2', 'average', 'credit', 'b']
    array_data = []
    for index, an in enumerate(annual_grades):
        student = an.student
        name = student.username+' - '+student.last_name+' '+student.first_name

        observation = '<span class="label label-warning">Rattrapage</span>'
        if an.credit != None:
            if an.credit is not None and an.credit >= 60:
                observation = '<span class="label label-success">Admis</span>'
        if an.credit_r != None:
            if an.credit_r < 60:
                observation = '<span class="label label-danger">Admis avec dettes</span>'
            if an.credit_r >= 60:
                observation = '<span class="label label-info">Admis Apres Ratt.</span>'

        cross_s1 = ''
        cross_s2 = ''
        cross_average = ''
        if an.rs1 != None:
            cross_s1 = 'line-through'
        if an.rs2 != None:
            cross_s2 = 'line-through'
        if an.rs1 != None or an.rs2 != None:
            cross_average = 'line-through'

        array_data.append([
            '<td class="center">' + str(index+1) + '</td>', 
            '<td>' + name.replace(' ', ' ') + '</td>', 

            '<td class="right '+cross_s1+'">'  + str(an.s1) + '</td>', 
            '<td class="center '+cross_s1+'">' + str(an.c1) + '</td>', 
            '<td class="right">'  + str(an.rs1) + '</td>', 
            '<td class="center">' + str(an.rc1) + '</td>',

            '<td class="right '+cross_s2+'">'  + str(an.s2) + '</td>', 
            '<td class="center '+cross_s2+'">' + str(an.c2) + '</td>', 
            '<td class="right">'  + str(an.rs2) + '</td>', 
            '<td class="center">' + str(an.rc2) + '</td>', 

            '<td class="right '+cross_average+'">'  + str(an.average) + '</td>', 
            '<td class="center '+cross_average+'">' + str(an.credit) + '</td>', 
            '<td class="right">'  + str(an.average_r) + '</td>', 
            '<td class="center">' + str(an.credit_r) + '</td>', 

            '<td class="right">'  + str(an.saving_average) + '</td>', 
            '<td class="center">' + str(an.saving_credit) + '</td>',
            '<td>' + observation  + '</td>'
        ])

    return array_data


@app.route('/annual-session/<annual_session_id>/create-rattrapage/', methods=['GET', 'POST'])
def create_rattrapage_annual(annual_session_id=0):
    students = request.form.getlist('students[]')

    for student_id in students:
        annual_grade = AnnualGrade.query\
            .filter_by(annual_session_id=annual_session_id, student_id=student_id)\
            .first()

        annual_dict = annual_grade.annual_session.get_annual_dict()

        student_session_1 = StudentSession.query\
            .filter_by(session_id=annual_dict['S1'], student_id=annual_grade.student_id)\
            .filter(StudentSession.credit<30)\
            .first()
        student_session_2 = StudentSession.query\
            .filter_by(session_id=annual_dict['S2'], student_id=annual_grade.student_id)\
            .filter(StudentSession.credit<30)\
            .first()

        if student_session_1 != None:
            create_rattrapage_semester(student_session_1.session_id, True)
        if student_session_2 != None:
            create_rattrapage_semester(student_session_2.session_id, True)

    return redirect(url_for('annual_session', annual_session_id=annual_session_id))


@app.route('/annual-session/<annual_session_id>/refrech', methods=['GET', 'POST'])
def annual_session_refrech(annual_session_id=0):
    init_annual_grade(annual_session_id)
    calculate_annual(annual_session_id)
    return redirect(url_for('annual_session', annual_session_id=annual_session_id))


def annual_session_dlc(*args, **kwargs):
    annual_session_id = request.view_args['annual_session_id']
    annual_session = AnnualSession.query.get(annual_session_id)
    return [{'text': '' + annual_session.name, 
        'url': url_for('annual_session', annual_session_id=annual_session_id) }]

@app.route('/annual-session/<annual_session_id>/', methods=['GET', 'POST'])
# @register_breadcrumb(app, '.tree.annual', 'Annual Session')
@register_breadcrumb(app, '.annual_tree.annual', '***', dynamic_list_constructor=annual_session_dlc)
def annual_session(annual_session_id=0):
    annual_session = AnnualSession.query.filter_by(id=annual_session_id).first_or_404()
    array_data = create_data_annual_session(annual_session_id)
    return render_template('session/annual-session.html', 
        title='Annual Session', annual_session=annual_session, array_data=array_data)


def renegade_annual_session(annual_session_id):
    # if it doesn't have any sessions
    annual_session = AnnualSession.query.get(annual_session_id)
    sessions = annual_session.sessions
    count = 0
    for session in sessions:
        count += 1

    if count == 0:
        annual_grades = AnnualGrade.query.filter_by(annual_session_id=annual_session_id).all()
        for annual_grade in annual_grades:
            db.session.delete(annual_grade)
        db.session.delete(annual_session)
        db.session.commit()

    return count

@app.route('/annual-session/<annual_session_id>/delete/', methods=['GET', 'POST'])
def delete_annual_session(annual_session_id):
    # if it doesn't have any sessions
    count = renegade_annual_session(annual_session_id)

    annual_session = AnnualSession.query.get(annual_session_id)
    promo = annual_session.promo
    school_id = promo.branch.school_id
    branch_id = promo.branch_id

    # in case it is not deleted in renegade_annual_session
    if count != 0 and annual_session != None:
        annual_grades = AnnualGrade.query.filter_by(annual_session_id=annual_session_id).all()
        for annual_grade in annual_grades:
            db.session.delete(annual_grade)
        db.session.delete(annual_session)
        db.session.commit()
    flash('annual session (' + str(annual_session_id) + ') is deleted')

    return redirect(url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo.id))
    
@app.route('/annual-session/<session_id>/create_annual_session/', methods=['GET', 'POST'])
def create_annual_session(session_id):
    annual_session_id = None
    promo_id = None
    session = Session.query.get(session_id)
    chain = session.get_annual_chain()
    for ch in chain:
        session = Session.query.get(ch)
        if session.annual_session_id != None:
            annual_session_id = session.annual_session_id
            promo_id = session.promo_id
            break

    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id

    # check the existance of the record
    annual_session = AnnualSession.query.filter_by(id=annual_session_id).first()
    if annual_session_id != None and annual_session == None:
        raise Exception('the Annual Session:' + str(annual_session_id) + ' does not exist')

    if annual_session == None:
        name = "Annual " + str(session.semester.annual)
        annual_session = AnnualSession(name=name, promo_id=promo_id)
        db.session.add(annual_session)
        db.session.commit()
        annual_session_id = annual_session.id

    init_annual_session_id(session.id, annual_session_id)


    # return redirect(url_for('annual_session', annual_session_id=annual_session_id))
    return redirect(url_for('annual_session_refrech', annual_session_id=annual_session_id))


# if annual_session_id=None -> take from other session in the same Annual
# else -> init with the new one
def init_annual_session_id(session_id, annual_session_id=None):
    # session = Session.query.get(session_id)
    # chain = session.get_annual_chain()
    chain = Session.query.get(session_id).get_annual_chain()
    if annual_session_id == None:
        for ch in chain:
            session = Session.query.get(ch)
            if session.annual_session_id != None:
                annual_session_id = session.annual_session_id
                break
    # init all in annual chain
    if annual_session_id != None:
        for ch in chain:
            session = Session.query.get(ch)
            session.annual_session_id = annual_session_id
        db.session.commit()


@app.route('/annual-session/<annual_session_id>/rattrapage/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.annual_tree.annual.rattrapage', 'Annual Rattrapage')
def students_rattrapage_annual(annual_session_id=0):
    students = AnnualGrade.query\
        .filter_by(annual_session_id=annual_session_id)\
        .filter(or_(AnnualGrade.credit<60, AnnualGrade.credit == None))\
        .join(Student).order_by(Student.username)\
        .all()
    return render_template('session/students-rattrapage-annual.html', 
        title='students-rattrapage-annual', 
        students=students, 
        annual_session_id=annual_session_id)

