from app import app, db
from flask import render_template, request, redirect, url_for, flash
from app.models import Promo, Session, StudentSession, Grade, GradeUnit, Unit, Semester,\
     School, Module, Student, Type, AnnualSession
from decimal import *
from ast import literal_eval
from sqlalchemy import or_

# from app.routesCalculation import config_to_dict, init_all
from app.routesCalculation import init_all, reinitialize_session
from flask_breadcrumbs import register_breadcrumb

from app.routesAnnual import init_annual_session_id



@app.route('/session/<session_id>/relation/', methods=['GET', 'POST'])
def show_relation(session_id=0):
    session = Session.query.filter_by(id=session_id).first()

    semesters = '*semesters*'
    sessions = '*sessions*'
    annual_semester = '*annual_semester*'
    annual_session = '*annual_session*'
    annual_dict = '*annual_dict*'
    previous_id = '*previous*'

    semesters = str(session.semester.get_chain())
    sessions = str(session.get_chain())
    annual_semester = str(session.semester.get_annual_chain())
    annual_session = str(session.get_annual_chain())
    annual_dict = str(session.get_annual_dict())
    previous = session.get_previous()
    if previous != None:
        previous_id = str(previous.id)

    return  'Semester ('+str(session.semester.id)+') chain: <br>' + semesters +\
        '<br><br>Session ('+str(session.id)+') chain: <br>' + sessions +\
        '<br><br><br>Annual ('+str(session.semester.annual )+') semester_id chain: <br>' + annual_semester +\
        '<br><br>Annual ('+str(session.semester.annual )+') session_id chain: <br>' + annual_session +\
        '<br><br>Annual ('+str(session.semester.annual )+') session_id dict: <br>' + annual_dict +\
        '<br><br>Previous of ('+str(session_id)+'): ' + previous_id

# ----------------------

def get_icon_progress_module(session_id, module_id):
    grades = Grade.query.filter_by(module_id=module_id)\
        .join(StudentSession).filter_by(session_id=session_id)\
        .all()
    return get_icon_progress(grades)

def get_icon_progress_student(session_id, student_id):
    grades = Grade.query.join(StudentSession)\
        .filter_by(session_id=session_id, student_id=student_id)\
        .all()
    return get_icon_progress(grades)

def extract_fields(formula):
    fields_list = []
    dictionary = eval(formula)
    for key in dictionary:
        fields_list += [key]

    return fields_list

def get_icon_progress(grades):
    cells_nbr = 0
    filled = 0
    errors = 0
    grades_is_empty = False

    for grade in grades:
        grades_is_empty = True
        fields_list = []
        if grade.formula != None:
            fields_list = extract_fields(grade.formula)
        for field in fields_list:
            if field in ['cour', 'td', 'tp', 't_pers', 'stage']:
                #if hasattr(a, 'property'):
                cells_nbr += 1
                val = getattr(grade, field)
                if val != None:
                    filled += 1
                    if val < 0 or val > 20:
                        errors += 1

    if grades_is_empty == False:
        return 'not_started2.png'
    if errors > 0:
        return 'refused.png'
    if cells_nbr == filled:
        return 'complite.png'
    if filled == 0:
        return 'not_started2.png'
    if cells_nbr!=filled and filled > 0  and  errors == 0:
        return 'in_progress.png'
    return ''


def is_config_changed(session):
    configuration= str(session.semester.config_dict())
    if configuration != session.configuration:
        return True
    return False

def get_config_changed_flash(session):
    if is_config_changed(session) and session.is_closed==False:
        init_url = url_for('reinitialize_session', session_id=session.id)
        url = url_for('slow_redirect', url=init_url, message='Initializing')
        btn = '<a href="'+url+'" class="btn btn-warning" role="button">(Re)initialize</a>'
        flash('Configuration has changed, you need to Reinitialized  '+btn, 'alert-warning')

def session_dlc(*args, **kwargs):
    session_id = request.view_args['session_id']
    session = Session.query.get(session_id)
    if session.is_rattrapage:
        return [{'text': 'Rattrapage ('+str(session.semester.get_nbr())+')', 
            'url': url_for('session', session_id=session_id) }]
    else:
        return [{'text': 'Semester ('+str(session.semester.get_nbr())+')', 
            'url': url_for('session', session_id=session_id) }]

@app.route('/session/<session_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session', '', dynamic_list_constructor=session_dlc)
def session(session_id=0):
    session = Session.query.filter_by(id=session_id).first_or_404()

    get_config_changed_flash(session)
    
    units = session.semester.units
    modules_list = []
    icons_module = []
    for unit in units:
        modules = unit.modules
        for module in modules:
            modules_list.append(module)
            icon = get_icon_progress_module(session_id, module.id)
            icons_module.append(icon)

    students_list = Student.query.join(StudentSession)\
        .filter_by(session_id=session_id).order_by(Student.username).all()
    icons_student = []
    for student in students_list:
        icon = get_icon_progress_student(session_id, student.id)
        icons_student.append(icon)

    session.name = make_session_name(session)

    return render_template('session/session.html', 
        title='Session', session=session,
        students=students_list, modules=modules_list,
        icons_module=icons_module, icons_student=icons_student)




def make_session_name(session):
    semester_nbr = session.semester.get_nbr()
    # name = session.promo.name
    name = session.promo.display_name

    if session.is_rattrapage is None or session.is_rattrapage is False:
        name += ' / Semester: ' + str(semester_nbr)
    else:
         name += ' / Rattrapage: ' + str(semester_nbr)
    return name

def update_student_session(students_from, students_to, session_id):
    session = Session.query.filter_by(id=session_id).first()

    dirty_add = False
    # all the students in this current Session
    students = Student.query.join(StudentSession).filter_by(session_id=session_id).all()
    for select in students_to:
        # check if  s  exists in  students
        s = Student.query.join(StudentSession).filter_by(student_id=select, session_id=session_id).first()
        if s not in students:
            student_session = StudentSession(student_id=select, session_id=session_id)
            db.session.add( student_session )
            dirty_add = True
    db.session.commit()

    message_add = 'No One added to Session: ' + str(session_id)
    if dirty_add == True:
        message_add = 'added Student(s) to Session: ' + str(session_id)


    dirty_remove = False
    # get new list of Student after adding
    students_session = StudentSession.query.filter_by(session_id=session_id)\
        .join(Student).order_by(Student.username).all()
    for student_session in students_session:
        if str(student_session.student_id) in students_from:
            grades = student_session.grades
            for grade in grades:
                db.session.delete(grade)
            grade_units = student_session.grade_units
            for grade_unit in grade_units:
                db.session.delete(grade_unit)
            db.session.delete(student_session)
            dirty_remove = True
    db.session.commit()

    message_remove = 'No One Removed from Session: ' + str(session_id)
    if dirty_remove == True:
        dirty_remove = 'Removed Student(s) from Session: ' + str(session_id)

    return message_add + '   -   ' + message_remove

def get_students_previous(session):
    students_previous = Student.query.order_by(Student.username).join(StudentSession)\
        .join(Session).filter_by(promo_id=session.promo_id).all()
    return students_previous

def get_students_candidates(session, _all):
    # I HAVE TO FIND ONLY THE ONES WITHOUT A SESSION
    # or just take ones from the Promo

    students_previous = get_students_previous(session)
    students_in_other_promos = Student.query.order_by(Student.username)\
        .join(StudentSession)\
        .join(Session).filter(Session.promo_id != session.promo_id).all()

    candidates_list = []
    for student in students_previous:
        candidates_list.append(student.id)
    for student in students_in_other_promos:
        candidates_list.append(student.id)

    if _all == '':
        return Student.query.filter_by(branch_id=session.semester.branch_id)\
            .filter(Student.id.notin_(candidates_list)).all()
    else:
        # return Student.query.filter(Student.id.notin_(candidates_list)).all()
        return Student.query.filter_by(branch_id=session.semester.branch_id).all()

# Note (security): can you change the id (post) and send it to another session ?????
@app.route('/session/<session_id>/add-student/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/add-student/<_all>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.student', 'Add Students')
def student_session(session_id=0, _all=''):
    students_from = request.form.getlist('from[]')
    students_to = request.form.getlist('to[]')

    if students_from != [] or students_to != []:
        msg = update_student_session(students_from, students_to, session_id)
        # re-initialize
        msg2 = init_all(session_id)
        flash(msg)
        # return redirect(url_for('student_session', session_id=session_id))
        return redirect(url_for('session', session_id=session_id))

    session = Session.query.get(session_id)

    students_previous = get_students_previous(session)
    students_candidates = get_students_candidates(session, _all)
    students_session = Student.query.order_by(Student.username)\
        .join(StudentSession).filter_by(session_id=session_id).all()

    return render_template('session/multiselect-add-students.html', 
        title='Session',
        students_previous=students_previous,
        students_candidates=students_candidates,
        students_session=students_session,
        session=session,
        _all=_all)

#

@app.route('/session/<session_id>/averages/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.average', 'Averages')
def semester_averages(session_id=0):
    # get modules list
    modules = []
    grades = Grade.query.join(StudentSession).filter_by(session_id=session_id).all()
    for grade in grades:
        _modules = (m[0] for m in modules)
        if grade.module_id not in _modules:
            module = []
            module.append(grade.module_id)
            module.append(grade.module.display_name)
            modules.append(module)

    data = []
    students_session = StudentSession.query.filter_by(session_id=session_id).all()
    for student_session in students_session:
        averages = []
        averages.append(student_session.student.username)
        averages.append(student_session.student.first_name.replace(' ', ' '))
        averages.append(student_session.student.last_name.replace(' ', ' '))
        for module in modules:
            grade = Grade.query.filter_by(student_session_id=student_session.id, module_id=module[0]).first()
            averages.append(grade.average)
        data.append(averages)

    return render_template('session/averages.html', title='Averages', 
        data=data, modules=modules, session_id=session_id)


#################


@app.route('/session/<session_id>/unlock-session/', methods=['GET', 'POST'])
def unlock_session(session_id):
    session = Session.query.filter_by(id=session_id).first_or_404()

    flash("Session (" + str(session.id) + ") unlocked.", 'alert-success')
    session.is_closed = False
    db.session.commit()

    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id
    return redirect(url_for('session', session_id=session.id))

@app.route('/session/<session_id>/lock-session/', methods=['GET', 'POST'])
def lock_session(session_id):
    session = Session.query.filter_by(id=session_id).first_or_404()

    # check that we calculated 
    student_sessions = session.student_sessions
    _not_complite = 0
    for ss in student_sessions:
        if ss.average == None:
            _not_complite += 1

    if _not_complite > 0:
        flash("you can't lock this Session because you didn't finish the Entries for " \
            + str(_not_complite) + " student(s).", 'alert-danger')
        return redirect(url_for('session', session_id=session.id))

    flash("Session (" + str(session.id) + ") locked.", 'alert-success')
    session.is_closed = True
    db.session.commit()

    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id
    return redirect(url_for('session', session_id=session.id))
    # return redirect(url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id))

# WARNING: i have to check before i delete
# check that the session is not closed
@app.route('/session/<session_id>/delete-session/', methods=['GET', 'POST'])
def delete_session(session_id):
    session = Session.query.filter_by(id=session_id).first_or_404()
    if session.is_closed == True:
        flash("you can't delete this session because it is locked")
        return redirect(url_for('session', session_id=session.id))

    sessions_chain = session.get_chain()

    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id

    # don't allow deletion if it is not the last one
    # and not ratt
    if session.get_next() is not None and not session.is_rattrapage:
        flash("you can't delete this Semester because it not the last one", 'alert-danger')
        return redirect(url_for('session', session_id=session.id))

    if session.is_closed is True:
        flash('Semester ('+str(session_id)+') was not deleted because it is Closed', 'alert-danger')
    else:
        # cleaning
        for ss in session.student_sessions:
            Grade.query.filter_by(student_session_id=ss.id).delete()
            GradeUnit.query.filter_by(student_session_id=ss.id).delete()
            db.session.delete(ss)
        db.session.delete(session)
        db.session.commit()
        flash('Semester ('+str(session_id)+') deleted')
        
    return redirect(url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id))



#######################################
#####                             #####
#####                             #####
#####             RATT            #####
#####                             #####
#####                             #####
#######################################

def create_rattrapage(session_id):
    session = Session.query.get(session_id)
    annual_dict = session.get_annual_dict()

    create_R1 = annual_dict['S1']==int(session_id) and annual_dict['R1']==-1
    create_R2 = annual_dict['S2']==int(session_id) and annual_dict['R2']==-1
    
    if create_R1 == True or create_R2 == True:
        new_session = Session(semester_id=session.semester_id, 
            promo_id=session.promo_id, is_rattrapage=True, 
            annual_session_id=session.annual_session_id)
        # set start_date and finish_date    
        # would it reference Semester before it is saved ???
        new_session.configuration = session.configuration
        db.session.add(new_session)
        db.session.commit()
        return new_session
    else:
        # if it Ratt exists
        if annual_dict['S1'] == session.id:
            return Session.query.get( annual_dict['R1'] )
        if annual_dict['S2'] == session.id:
            return Session.query.get( annual_dict['R2'] )

    # # if Rattrapage exist -> it is next
    return session

@app.route('/session/<session_id>/rattrapage/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.rattrapage', 'Rattrapage')
def students_rattrapage_semester(session_id=0):
    students = StudentSession.query\
        .filter_by(session_id=session_id)\
        .filter(or_(StudentSession.credit<30, StudentSession.credit == None))\
        .join(Student).order_by(Student.username)\
        .all()
    return render_template('session/students-rattrapage-semester.html', 
        title='students-rattrapage-semester', 
        students=students, 
        session_id=session_id)


def init_grades_rattrapage(session, rattrapage):
    # # travers students in Rattrapage and Init from Session
    students_session = StudentSession.query.filter_by(session_id=session.id).all()

    for student_sess in students_session:
        student_ratt = StudentSession.query\
            .filter_by(session_id=rattrapage.id, student_id=student_sess.student_id)\
            .first()
        # init_grades_modules(student_sess.id, student_ratt.id, student_ratt.student_id)
        init_grades_modules(student_sess.id, student_ratt.id)
    db.session.commit()

def init_grades_modules(student_session_id, student_rattrapage_id):
    grades = Grade.query.filter_by(student_session_id=student_session_id).all()
    for grade_sess in grades:
        grade_ratt = Grade.query.filter_by(
            student_session_id=student_rattrapage_id, 
            module_id=grade_sess.module_id
            ).first()

        # get "cour" according to 
        cour = None
        #if 

        # if grade_ratt does not exist -> create it
        # if grade_ratt exist -> update it
        if grade_ratt is None:
            grade_ratt = Grade(
                cour=cour,
                td=grade_sess.td,
                tp=grade_sess.tp,
                t_pers=grade_sess.t_pers,
                stage=grade_sess.stage,
                formula=grade_sess.formula,
                student_session_id=student_rattrapage_id,
                module_id=grade_sess.module_id
                )
            db.session.add(grade_ratt)
        else:
            grade_ratt.cour = cour
            grade_ratt.td = grade_sess.td
            grade_ratt.tp = grade_sess.tp
            grade_ratt.t_pers = grade_sess.t_pers
            grade_ratt.stage = grade_sess.stage
            grade_ratt.formula = grade_sess.formula
        #
    #

def transfer_grades(session_id, ratt_id, student_session_ratt_id, student_id):
    grades = Grade.query.join(StudentSession)\
        .filter_by(session_id=session_id, student_id=student_id)\
        .all()

    # ratt_modules = get_ratt_modules_list_semester(session_id, student_id)
    student_session = StudentSession.query.filter_by(session_id=session_id, student_id=student_id).first()
    ratt_modules = student_session.get_ratt_modules_list_semester()

    for grade in grades:
        grade_in_ratt = Grade.query.filter_by(
            student_session_id=student_session_ratt_id, 
            module_id=grade.module_id).first()

        cour = grade.cour
        is_rattrapage = None

        # if int(grade.module_id) in ratt_modules:
        if grade.module_id in ratt_modules:
            is_rattrapage = True
            cour = None

        # if it exists save Cour and delete record
        if grade_in_ratt is not None:
            # if int(grade.module_id) in ratt_modules:
            if grade.module_id in ratt_modules:
                cour = grade_in_ratt.cour
            db.session.delete(grade_in_ratt)

        new_grade = Grade(
            student_session_id=student_session_ratt_id,
            module_id=grade.module_id, 
            formula=grade.formula,
            cour=cour, 
            td=grade.td, 
            tp=grade.tp,
            t_pers=grade.t_pers, 
            stage=grade.stage, 
            average=grade.average, 
            credit=grade.credit,
            is_rattrapage=is_rattrapage)
        db.session.add(new_grade)

    return 1

def transfer_student_session(session_from, session_to, student_id):
    student_session = StudentSession.query\
        .filter_by(session_id=session_to, student_id=student_id)\
        .first()
    if student_session == None:
        student_session = StudentSession(session_id=session_to, student_id=student_id)
        db.session.add(student_session)
        db.session.commit()
    return student_session

@app.route('/session/<session_id>/create-rattrapage/', methods=['GET', 'POST'])
def create_rattrapage_semester(session_id=0, no_redirect=False):
    students = request.form.getlist('students[]')

    # create rattrapage
    session_rattrapage = create_rattrapage(session_id)
    ratt_id = session_rattrapage.id

    # transfair students
    for student_id in students:
        student_session_ratt = transfer_student_session(session_id, ratt_id, student_id)
        transfer_grades(session_id, ratt_id, student_session_ratt.id, student_id)
    
    db.session.commit()
    if no_redirect == True:
        return ''
    return redirect(url_for('session', session_id=session_rattrapage.id))



@app.route('/create-next-session/promo/<promo_id>/', methods=['GET', 'POST'])
def create_next_session(promo_id=0):
    promo = Promo.query.get(promo_id)
    next_semester = promo.get_next_semester()

    # return redirect( url_for('create_session', promo_id=promo.id, semester_id=next_semester.id) )

    url = url_for('create_session', promo_id=promo.id, semester_id=next_semester.id)
    return redirect( url_for('slow_redirect', url=url) )

    return ' *** create_next_session *** '


@app.route('/create-session/promo/<promo_id>/semester/<semester_id>/', methods=['GET', 'POST'])
def create_session(promo_id=0, semester_id=0):
    session = None

    sessions = Session.query.filter_by(
        promo_id=promo_id, semester_id=semester_id, is_rattrapage=False).all()
    if len(sessions) > 0:
        # check if the session of this simester exists
        session = Session.query\
            .filter_by(promo_id=promo_id, semester_id=semester_id, is_rattrapage=False)\
            .first()
        if session is not None:
            flash('Semester (' + str(session.semester.get_nbr()) + ') already exist', 'alert-warning')
    else:
        session = Session(promo_id=promo_id, semester_id=semester_id)
        db.session.add(session)
        db.session.commit()
        init_annual_session_id(session.id)
        flash('Semester (' + str(session.semester.get_nbr()) + ') created', 'alert-success')

    # transfair students
    previous_normal = session.get_previous_normal()
    if previous_normal != None:
        for student in previous_normal.student_sessions:
            transfer_student_session(previous_normal.id, session.id, student.student_id)
        init_all(session.id)

    # to fill configuration at creation
    update_session_configuraton(session)

    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id
    return redirect( url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id) )


def update_session_configuraton(session):
    configuration = str( session.semester.config_dict() )
    session.configuration = configuration
    
    # update Related Session (Ratt + Session)

    db.session.commit() 




#######################################
#####                             #####
#####                             #####
#####            Bultin           #####
#####                             #####
#####                             #####
#######################################

def get_header_bultin_semester():
    header = '<tr class="head">'
    header += '<th colspan=3>Unité d''Enseignement</th>'
    header += '<th colspan=4>Matière d''Enseignement</th>'
    header += '<th colspan=6>Résultats obtenus</th>'
    header += '</tr>'
    header += '<tr class="head">'
    header += '<th rowspan=2>Nature</th>'
    header += '<th rowspan=2>Crédit</br>requis</th>'
    header += '<th rowspan=2>Coeff</th>'

    header += '<th rowspan=2>Code</th>'
    header += '<th rowspan=2>Intitulé</th>'
    header += '<th rowspan=2>Crédit</br>requis</th>'
    header += '<th rowspan=2>Coeff</th>'

    header += '<th colspan=3>Matière</th> <th colspan=3>U.E</th>'
    header += '</tr>'
    header += '<tr class="head">'
    header += '<th>Moy</th> <th>Cr</th> <th>S</th>'
    header += '<th>Moy</th> <th>Cr</th> <th>S</th>'
    header += '</tr>'

    return header

def get_bultin_semester(student_session):
    student = student_session.student
    semester = student_session.session.semester
    sem = semester.semester

    annual_string = str(semester.annual)
    annual_string += '<sup>ére</sup>' if semester.annual == 1 else '<sup>ème</sup>'

    # header
    header = '<center><h2>Releve de Notes Semeste '+str(sem)+'</h2></center>'
    header += "Le directeur de <b>"+student.branch.school.name+",</b> atteste que l'étudiant(e)</br>"
    header += 'Nom: <b>'+student.last_name+'</b>     '
    header += 'Prenom: <b>'+student.first_name+'</b>    '
    header += 'Né(e) le: <b>'+str(student.birth_date)+'</b> à <b>'+student.birth_place+'</b></br>'
    header += 'Inscrit(e) en <b>' + str(annual_string) + ' année</b>   '
    header += 'Corps des: <b>'+student.branch.description+'</b></br>'
    header += 'Sous le matricule: <b>' + student.username + '</b>'
    header += "  a obtenu les résultats suivants durant l'année pédagogique: <b>*********</b>"
    header += '</br></br>'

    # footer
    footer = '</br>'
    footer += 'Moyenne Semestrielle: <b>'+str(student_session.average)+'</b>    '
    footer += 'Crédits cumulés dans le Semeste: <b>'+str(student_session.credit)+'</b></br>'
    footer += 'Décision de la commission de classement et '
    footer += 'd''orientation:  <b>******</b></br></br>'
    footer += 'Ouargla le:  ..................'

    # Table
    grade_units = student_session.grade_units
    table = '<table class="table table-bordered">'
    table += get_header_bultin_semester()

    for grade_unit in grade_units:
        modules_in_unit = [module.id for module in grade_unit.unit.modules]
        grades_in_unit = Grade.query\
            .filter_by(student_session_id=student_session.id)\
            .filter(Grade.module_id.in_(modules_in_unit)).all()

        grades_tr = ''
        rowspan = 0
        # EMPTY = '<font color="red"><b>X</b></font>'
        def EMPTY(text):
            return '<font color="red"><b>' + text + '</b></font>'

        for grade in grades_in_unit:
            module = grade.module
            if rowspan > 0:
                grades_tr += '<tr>'
            grades_tr += '<td>'+str(module.code).replace('None', EMPTY('???'))+'</td>'
            grades_tr += '<td class="intitule">'+module.display_name.replace(' ', ' ')+'</td>'
            grades_tr += '<td>'+str(module.credit)+'</td> <td>'+str(module.coefficient)+'</td>'
            grades_tr += '<td>'+str(grade.average).replace('None', EMPTY('X'))+'</td>'
            grades_tr += '<td>'+str(grade.credit).replace('None', EMPTY('X'))+'</td>'
            grades_tr += '<td>'+str(grade.get_ratt_bultin())+'</td>'
            if rowspan == 0:
                grades_tr += '<td rowspan=_rowspan_>'+str(grade_unit.average).replace('None', EMPTY('X'))+'</td>'
                grades_tr += '<td rowspan=_rowspan_>'+str(grade_unit.credit).replace('None', EMPTY('X'))+'</td>'
                grades_tr += '<td rowspan=_rowspan_>'+str(grade_unit.get_ratt_bultin())+'</td>'
            
            grades_tr += '</tr>'
            rowspan += 1

        unit = grade_unit.unit
        tr =  '<td rowspan='+str(rowspan)+'>'+unit.display_name+'</td>'
        tr += '<td rowspan='+str(rowspan)+'>'+str(unit.get_unit_cumul_credit())+'</td>'
        tr += '<td rowspan='+str(rowspan)+'>'+str(unit.unit_coefficient)+'</td>'
        tr += grades_tr.replace('_rowspan_', str(rowspan) )

        table += '<tr>' + tr + '</tr>'
    table += '</table>'

    return header + table + footer

@app.route('/session/<session_id>/student/<student_id>/bultin/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.classement.bultin', 'Bultin')
def bultin_semester(session_id, student_id):
    student_session = StudentSession.query\
        .filter_by(session_id=session_id, student_id=student_id).first()

    table = get_bultin_semester(student_session)

    return render_template('student/bultin-semester.html',
        title='Bultin', table=table, session_id=session_id, student_id=student_id)

@app.route('/session/<session_id>/student/<student_id>/bultin-print/', methods=['GET', 'POST'])
def bultin_semester_print(session_id, student_id):
    student_session = StudentSession.query\
        .filter_by(session_id=session_id, student_id=student_id).first()
    table = get_bultin_semester(student_session)
    return render_template('student/bultin-semester-print.html', 
            title='Bultin', table=table, session_id=session_id)

@app.route('/session/<session_id>/bultin-print-all/', methods=['GET', 'POST'])
def bultin_semester_print_all(session_id):
    student_sessions = StudentSession.query\
        .filter_by(session_id=session_id).all()

    tables = []
    for student_session in student_sessions:
        tables.append( get_bultin_semester(student_session) )

    return render_template('student/bultin-semester-print-all.html', 
            title='Bultin All', tables=tables, session_id=session_id)

# ----------------------
# ----------------------
# ----------------------




#######################################
#####                             #####
#####                             #####
#####                             #####
#####                             #####
#####                             #####
#######################################

def get_th_1(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th>Unit</th>'
    for unit in conf_dict['units']:
        display_name = unit["display_name"]
        coeff = unit["coeff"]
        unit_name = F'{display_name} ({coeff})'
        colspan = cols_per_module
        for module in unit['modules']:
            colspan += cols_per_module
        header += F'<th class="unit" colspan={colspan}><center>{unit_name}</center></th>'
    display_name = conf_dict["display_name"]
    return header + F'<th class="semester" rowspan=4 colspan={cols_per_module}><center>{display_name}</center></th>'

def get_th_2(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th>Module</th>'
    for unit in conf_dict['units']:
        for module in unit['modules']:
            display_name = module["display_name"]
            header += F'<th colspan={cols_per_module}><center>{display_name}</center></th>'
        name = 'Resultat de ' + unit["display_name"] 
        header += F'<th class="unit" rowspan=3 colspan={cols_per_module}><center>{name}</center></th>'
    return header

def get_th_3(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th>Required Credit</th>'
    for unit in conf_dict['units']:
        for module in unit['modules']:
            credit = module['credit']
            header += F'<th colspan={cols_per_module}><center>{credit}</center></th>'
    return header

def get_th_4(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th>Coefficient</th>'
    for unit in conf_dict['units']:
        for module in unit['modules']:
            coeff = module['coeff']
            header += F'<th colspan={cols_per_module}><center>{coeff}</center></th>'
    return header

def get_th_5(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th class="header5">N°</th><th class="header5">Matricule</th><th class="header5">Nom</th>'

    average = 'A'
    credit = 'C'
    session = 'S'

    th_module = F'<th class="header5"><center>{average}</center></th>'
    th_unit = F'<th class="unit"><center>{average}</center></th>'
    th_semester = F'<th class="semester"><center>{average}</center></th>'

    if cols_per_module >= 2:
        th_module += F'<th class="header5"><center>{credit}</center></th>'
        th_unit += F'<th class="unit"><center>{credit}</center></th>'
        th_semester += F'<th class="semester"><center>{credit}</center></th>'
    if cols_per_module == 3:
        th_module += F'<th class="header5"><center>{session}</center></th>'
        th_unit += F'<th class="unit"><center>{session}</center></th>'
        th_semester += F'<th class="semester"><center>{session}</center></th>'
    
    for unit in conf_dict['units']:
        for module in unit['modules']:
            header += th_module
        header += th_unit
    # semester
    header += th_semester
    return header

def get_thead(configuration, cols_per_module=2):
    th_1 = get_th_1(configuration, cols_per_module)
    th_2 = get_th_2(configuration, cols_per_module)
    th_3 = get_th_3(configuration, cols_per_module)
    th_4 = get_th_4(configuration, cols_per_module)
    th_5 = get_th_5(configuration, cols_per_module)

    return F'''
        <tr>     <th style='border: 0;' colspan=2 rowspan=4></th>     {th_1}     </tr>
        <tr>     {th_2}     </tr>
        <tr>     {th_3}     </tr>
        <tr>     {th_4}     </tr>
        <tr>     {th_5}     </tr>
    '''


def get_row_module(grade, cols_per_module):
    row = F'<td class="right td">{grade.average}</td>'
    if cols_per_module >= 2:
        row += F'<td class="center td">{grade.credit}</td>'
    if cols_per_module == 3:
        row += F'<td class="center td">**</td>'
    return row

def get_row_unit(grade_unit, cols_per_module):
    grades = grade_unit.student_session.grades
    row = ''
    for grade in grades:
        # get only the grades in unit
        if grade.module.unit_id == grade_unit.unit_id:
            row += get_row_module(grade, cols_per_module)

    row += F'<td class="unit right td">{grade_unit.average}</td>'
    if cols_per_module >= 2:
        row += F'<td class="unit center td">{grade_unit.credit}</td>'
    if cols_per_module == 3:
        row += F'<td class="unit center td">**</td>'
    return row

def get_row_semester(student_session, cols_per_module=2):
    grade_units = student_session.grade_units
    row = ''
    for grade_unit in grade_units:
        row += get_row_unit(grade_unit, cols_per_module)

    row += F'<td class="semester right td">{student_session.average}</td>'
    if cols_per_module >= 2:
        row += F'<td class="semester center td">{student_session.credit}</td>'
    if cols_per_module == 3:
        row += F'<td class="semester center td">{student_session.session_id}</td>'
    return row

def get_semester_result_data(session_id, cols_per_module=2):
    data_arr = []
    students_session = StudentSession.query.filter_by(session_id=session_id)\
        .join(Student).order_by(Student.username).all()

    for index, student_session in enumerate(students_session, start=1):
        student = student_session.student
        _std = '<td class="center td">' + str(index) + '</td>'
        _std += '<td class="no-wrap td">' + student.username + '</td>'
        _std += '<td class="no-wrap td">' + student.last_name + ' ' + student.first_name + '</td>'
        row = _std + get_row_semester(student_session, cols_per_module)
        data_arr.append(row)

    # for index, student_session in enumerate(students_session, start=1):
    #     student = student_session.student
    #     _std = '<td class="center td">' + str(index+31) + '</td>'
    #     _std += '<td class="no-wrap td">' + student.username + '</td>'
    #     _std += '<td class="no-wrap td">' + student.last_name + ' ' + student.first_name + '</td>'
    #     row = _std + get_row_semester(student_session, cols_per_module)
    #     data_arr.append(row)
    # for index, student_session in enumerate(students_session, start=1):
    #     student = student_session.student
    #     _std = '<td class="center td">' + str(index+31+31) + '</td>'
    #     _std += '<td class="no-wrap td">' + student.username + '</td>'
    #     _std += '<td class="no-wrap td">' + student.last_name + ' ' + student.first_name + '</td>'
    #     row = _std + get_row_semester(student_session, cols_per_module)
    #     data_arr.append(row)
    # for index, student_session in enumerate(students_session, start=1):
    #     student = student_session.student
    #     _std = '<td class="center td">' + str(index+31+31+31) + '</td>'
    #     _std += '<td class="no-wrap td">' + student.username + '</td>'
    #     _std += '<td class="no-wrap td">' + student.last_name + ' ' + student.first_name + '</td>'
    #     row = _std + get_row_semester(student_session, cols_per_module)
    #     data_arr.append(row)
    # for index, student_session in enumerate(students_session, start=1):
    #     student = student_session.student
    #     _std = '<td class="center td">' + str(index+31+31+31+31) + '</td>'
    #     _std += '<td class="no-wrap td">' + student.username + '</td>'
    #     _std += '<td class="no-wrap td">' + student.last_name + ' ' + student.first_name + '</td>'
    #     row = _std + get_row_semester(student_session, cols_per_module)
    #     data_arr.append(row)

    return data_arr


@app.route('/session/<session_id>/semester-result/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.result', 'Semester Result')
def semester_result(session_id=0):
    session = Session.query.filter_by(id=session_id).first_or_404()
    header = get_thead(session.configuration, 2)
    data_arr = get_semester_result_data(session_id, 2)

    sem_result = ''
    sem_result += '<table class="">'
    sem_result += '<thead>' + header + '</thead>'
    sem_result += '<tbody>'
    for data in data_arr:
        sem_result += '<tr>' + data + '</tr>'
    sem_result += '</tbody>'
    sem_result += '</table>'

    # data_arr.insert(10, '<td border="0"> </td>')
    # data_arr.insert(11, '<td border="0"> </td>')

    return render_template('session/semester-result.html',
        title='Semester ' + str(session.semester.semester) + ' Result', 
        header=header, sem_result=sem_result, session=session)



@app.route('/session/<session_id>/semester-result-print-browser/', methods=['GET', 'POST'])
# @register_breadcrumb(app, '.tree.session.result', 'Semester Result')
def semester_result_print_browser(session_id=0):
    session = Session.query.filter_by(id=session_id).first_or_404()
    header = get_thead(session.configuration, 2)
    data_arr = get_semester_result_data(session_id, 2)

    sem_result = ''
    sem_result += '<table class="">'
    sem_result += '<thead>' + header + '</thead>'
    sem_result += '<tbody>'
    for data in data_arr:
        sem_result += '<tr>' + data + '</tr>'
    sem_result += '</tbody>'
    sem_result += '</table>'

    return render_template('session/semester-result-print-browser.html',
        title='Semester ' + str(session.semester.semester) + ' Result', 
        header=header, sem_result=sem_result, session=session)


@app.route('/session/<session_id>/semester-result-print/<_id>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/semester-result-print/', methods=['GET', 'POST'])
def semester_result_print(session_id=0, _id=0,
                          insert1=43, insert2=43+56, insert3=43+56+57):
    session = Session.query.filter_by(id=session_id).first_or_404()
    header = get_thead(session.configuration, 2)
    data_arr = get_semester_result_data(session_id, 2)

    # data_arr.insert(insert1+1, '<td border="0"> </td>')
    # data_arr.insert(insert1+2, '<td border="0"> </td>')
    # data_arr.insert(insert1+3, '<td border="0"> </td>')

    # data_arr.insert(insert2+1, '<td border="0"> </td>')
    # data_arr.insert(insert2+2, '<td border="0"> </td>')
    # data_arr.insert(insert2+3, '<td border="0"> </td>')

    # data_arr.insert(insert3+1, '<td border="0"> </td>')
    # data_arr.insert(insert3+2, '<td border="0"> </td>')
    # data_arr.insert(insert3+3, '<td border="0"> </td>')

    return render_template('session/semester-result-print.html', 
        title='Semester ' + str(session.semester.semester) + ' Result', 
        header=header, data_arr=data_arr, session=session,
        insert1=insert1, insert2=insert2, insert3=insert3)




#######################################
#####                             #####
#####                             #####
#####             PDF             #####
#####                             #####
#####                             #####
#######################################


def get_module_cols(module_id):
    module = Module.query.get_or_404(module_id)
    percentages = module.percentages
    cols = []
    for percentage in percentages:
        type_id = percentage.type_id
        type = Type.query.get(type_id)
        cols.append(type.grade_table_field)
    return cols

def get_module_headers(module_id):
    module = Module.query.get(module_id)
    percentages = module.percentages
    headers = ['#', 'Matricule', 'Nom', 'Prenom']

    for percentage in percentages:
        type_id = percentage.type_id
        type = Type.query.get(type_id)
        headers.append(type.type + ' ('+str(int(percentage.percentage*100))+'%)')
        # headers.append(type.type + ' ('+  +'%)')
    return headers

def create_data_for_module(grades, cols, empty=''):
    data = []
    for index, grade in enumerate(grades, start=1):
        record = []
        student = grade.student_session.student

        record.append(index)
        record.append(student.username)
        record.append(student.last_name)
        record.append(student.first_name)
        if empty == 'yes':
            record.append('')
            if 'td' in cols:
                record.append('')
            if 'tp' in cols:
                record.append('')
            if 't_pers' in cols:
                record.append('')
            if 'stage' in cols:
                record.append('')
        else:
            record.append(grade.cour)
            # WARNING: this one shoold be Dynamic
            if 'td' in cols:
                record.append(grade.td)
            if 'tp' in cols:
                record.append(grade.tp)
            if 't_pers' in cols:
                record.append(grade.t_pers)
            if 'stage' in cols:
                record.append(grade.t_pers)

        data.append(record)
    return data

# print empty
# with grades
# with averages
# by order
def get_module_print_table(session_id=0, module_id=0, empty='', order='username'):
    grades = None
    if order == 'username':
        grades = Grade.query.filter_by(module_id=module_id)\
            .join(StudentSession).filter_by(session_id=session_id)\
            .join(Student).order_by(Student.username)\
            .all()
    else:
        grades = Grade.query.filter_by(module_id=module_id)\
            .join(StudentSession).filter_by(session_id=session_id)\
            .join(Student).order_by(Student.last_name, Student.first_name)\
            .all()

    cols = get_module_cols(module_id)
    headers = get_module_headers(module_id)
    data_arr = create_data_for_module(grades, cols, empty)
    module = Module.query.get(module_id)

    
    table = ''
    table += '<center><h4><b>Module: </b>' + module.display_name + '</h4></center>'
    table += '<center> <h5><b>Coefficient: </b>' + str(module.coefficient) + '   <b>-</b>   '
    table += '<b>Credit: </b>' + str(module.credit) + '</h5> </center>'

    table += '<table class="table table-condensed ">'
    table += '<tr>'
    for header in headers:
        table += '<th>' + header + '</th>'
    table += '</tr>'

    for data in data_arr:
        table += '<tr>'
        # table += '<td>'+str(data)+'</td>'
        for _da in data:
            table += '<td>' + str(_da) + '</td>'
        table += '</tr>'

    table += '</table>'

    return table



@app.route('/session/<session_id>/module/<module_id>/print/order/<order>/empty/<empty>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/module/<module_id>/print/empty/<empty>/order/<order>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/module/<module_id>/print/order/<order>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/module/<module_id>/print/empty/<empty>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/module/<module_id>/print/', methods=['GET', 'POST'])
def module_print(session_id=0, module_id=0, empty='', order='username'):
    table = get_module_print_table(session_id, module_id, empty, order)

    return render_template('session/semester-module-print.html', 
        title='module ***', table=table)



@app.route('/page-break/', methods=['GET'])
def page_break():
    return render_template('page-break.html')





# from flask_weasyprint import HTML, render_pdf

# @app.route('/pdf/weasyprint/')
# def your_view_weasyprint():
#     return '12'
#     # html = render_template('http://localhost:5000/session/2/semester-result-print/')
#     # return render_pdf(HTML(string=html))


# Flask-WeasyPrint
# https://pythonhosted.org/Flask-WeasyPrint/
# http://weasyprint.readthedocs.io/en/latest/install.html



import pdfkit
from flask import send_file, send_from_directory
from flask import Response

'''
be carefull returning the file in the right version
it looks like if i change the file it keeps returning the old one
it seems to work right when changing the URL
''' 
@app.route('/pdf/session/<session_id>/nbr/<id>/')
def print_semester_result(session_id=0, id=0):
    # options = {'orientation': 'landscape', 'page-size':'A4', 'dpi':400}
    options = {'orientation': 'landscape', 
        'page-size':'A4', 
        'encoding':'utf-8', 'dpi':400
        # 'margin-top':'0.5cm',
        # 'margin-bottom':'0.8cm',
        # 'margin-left':'0.5cm',
        # 'margin-right':'0.2cm'

    }

    # url = 'http://localhost:5001/session/1/semester-result-print/'+str(id)+'/'

    url = url_for('semester_result_print', session_id=session_id, _external=True)
    pdf_file_name = 'semester_zerbia.pdf'
    return html_to_pdf(url, pdf_file_name, options)



@app.route('/pdf/session/<session_id>/student/<student_id>/bultin-print/')
def print_semester_bultin(session_id, student_id):
    options = {'orientation': 'landscape', 
        'page-size':'A4', 
    }

    url = url_for('bultin_semester_print', session_id=session_id, student_id=student_id, _external=True)
    pdf_file_name = 'semester_bultin.pdf'
    return html_to_pdf(url, pdf_file_name, options)




@app.route('/session/<session_id>/module/<module_id>/students-print/empty/<empty>')
@app.route('/session/<session_id>/module/<module_id>/students-print/')
def print_module_students_empty(session_id=0, module_id=0, empty='no'):
    url = url_for('module_print', session_id=session_id, 
        module_id=module_id, _external=True)
    if empty == 'yes':
        url = url_for('module_print', session_id=session_id, 
            module_id=module_id, _external=True, empty='yes')

    pdf_file_name = 'module_students_print.pdf'
    return html_to_pdf(url, pdf_file_name)


@app.route('/print-page-break/')
def print_page_break():
    url = 'http://localhost:5000/page-break/'
    pdf_file_name = 'page-break.pdf'
    return html_to_pdf(url, pdf_file_name)


@app.route('/print-test/')
def print_test():
    url = 'https://www.w3schools.com/colors/colors_picker.asp'
    pdf_file_name = 'azerty.pdf'
    return html_to_pdf(url, pdf_file_name)

def html_to_pdf(url, pdf_file_name, options={}):
    wkhtmltopdf_path = app.config['WKHTMLTOPDF_PATH']
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    pdf = pdfkit.from_url(url, 'app\\pdf\\'+pdf_file_name, configuration=config, options=options)
    return send_from_directory('pdf', pdf_file_name)


#
#
#  
#
