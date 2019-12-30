from app import app, db
from flask import render_template, request, redirect, url_for, flash
from app.models import Promo, Session, StudentSession, Grade, GradeUnit, Unit, Semester,\
     School, Module, Student, Type, AnnualSession, AnnualGrade, Grade, Annual,\
     Classement, ClassementYear, ModuleSession, ClassementSemester
from app.forms import SessionConfigForm
from flask_breadcrumbs import register_breadcrumb
from decimal import *
from ast import literal_eval
# from sqlalchemy import or_
from datetime import datetime
from app.routesCalculation import init_all, reinitialize_session, update_session_configuraton
from app._shared_functions import extract_fields, check_session_is_complite



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
        '<br><br><br>Annual ('+str(session.semester.annual.annual )+') semester_id chain: <br>' + annual_semester +\
        '<br><br>Annual ('+str(session.semester.annual.annual )+') session_id chain: <br>' + annual_session +\
        '<br><br>Annual ('+str(session.semester.annual.annual )+') session_id dict: <br>' + annual_dict +\
        '<br><br>Previous of ('+str(session_id)+'): ' + previous_id

# ----------------------

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
                cells_nbr += 1
                val = getattr(grade, field)
                #if hasattr(a, 'property'):
                if val != None:
                    filled += 1
                    if val < 0 or val > 20:
                        errors += 1
        # saving_grade
        if grade.saving_grade != None:
            if grade.saving_grade > 20 or grade.saving_grade < 0:
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

def get_config_changed_flash(session):
    if session.is_config_changed():
        init_url = url_for('reinitialize_session', session_id=session.id)
        url = url_for('slow_redirect', url=init_url, message='Initializing')
        btn = '<a href="'+url+'" class="btn btn-warning" role="button">(Re)initialize</a>'
        flash('Configuration has changed, you need to Reinitialized  '+btn, 'alert-warning')

def session_dlc(*args, **kwargs):
    session_id = request.view_args['session_id']
    session = Session.query.get_or_404(session_id)
    nbr = session.semester.get_nbr()
    text = 'Semester'
    if session.is_rattrapage:
        text = 'Rattrapage'
    return [{'text': text+' ('+str(nbr)+')', 
        'url': url_for('session', session_id=session_id)}]

@app.route('/session/<session_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_session.session', '***', dynamic_list_constructor=session_dlc)
def session(session_id=0):
    session = Session.query.get_or_404(session_id)
    # if session.is_closed == False:
    #     get_config_changed_flash(session)

    annual_session = session.annual_session
    if annual_session != None:
        students_consistant = session.annual_session\
            .check_students_consistant_between_two_semesters()
        students_ratt_are_in_semesters = session.annual_session\
            .check_students_ratt_are_in_semesters(session)

    if session.is_historic:
        # test session-historic progress
        data_arr = create_data_session_historic(session)
        # title = 'Session Historique ('
        # title += str(session.promo.branch.name)+' - '
        # title += session.semester+')'
        title = session.get_title()
        return render_template('session/session-historic.html', title=title, 
            session=session, data_arr=data_arr)
    else:
        modules_list = []
        icons_module = []
        for unit in session.semester.units:
            for module in unit.modules:
                # 
                # 
                # 
                # 
                # 
                # 
                module.is_savable = False
                module_session = ModuleSession.query.filter_by(module_id=module.id).first()
                if module_session != None:
                    module.is_savable = module_session.saving_enabled
                # 
                # 
                # 
                # 
                # 
                # 
                # 
                # 
                # 
                # 
                modules_list.append(module)
                icon = get_icon_progress_module(session_id, module.id)
                icons_module.append(icon)

        students_list = Student.query.join(StudentSession)\
            .filter_by(session_id=session_id).order_by(Student.username).all()
        icons_student = []
        for student in students_list:
            icon = get_icon_progress_student(session_id, student.id)
            icons_student.append(icon)

        grades = Grade.query.join(StudentSession).filter_by(session_id=session_id).all()
        check = check_session_is_complite(grades, session)
        # title = 'Session ()'
        
        title = session.get_title()
        return render_template('session/session.html', 
            title=title, session=session,
            students=students_list, modules=modules_list,
            icons_module=icons_module, icons_student=icons_student, check=check)

@app.route('/session/<session_id>/unlock-session/', methods=['GET', 'POST'])
def unlock_session(session_id):
    session = Session.query.filter_by(id=session_id).first_or_404()
    session.reverse_status()

    # parallel_session = session.get_parallel_session()
    # if parallel_session != None:
    #     parallel_session.reverse_status()

    # if parallel_session != None:
    #     flash("Sessions ("+str(session.id)+") and ("+str(parallel_session.id)+") unlocked.", 'alert-success')
    # else:
    #     flash("Session ("+str(session.id)+") unlocked.", 'alert-success')

    db.session.commit()
    return redirect(url_for('session', session_id=session.id))

@app.route('/session/<session_id>/lock-session/', methods=['GET', 'POST'])
def lock_session(session_id):
    session = Session.query.get_or_404(session_id)

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

    session.reverse_status()

    # parallel_session = session.get_parallel_session()
    # if parallel_session != None:
    #     parallel_session.reverse_status()

    # if parallel_session != None:
    #     flash("Sessions ("+str(session.id)+") and ("+str(parallel_session.id)+") locked.", 'alert-success')
    # else:
    #     flash("Session ("+str(session.id)+") locked.", 'alert-success')
    
    db.session.commit()
    return redirect(url_for('session', session_id=session.id))

# WARNING: i have to check before i delete
# check that the session is not closed
@app.route('/session/<session_id>/delete-session/', methods=['GET', 'POST'])
def delete_session(session_id):
    session = Session.query.filter_by(id=session_id).first_or_404()
    if session.is_closed == True:
        flash("you can't delete this session because it is locked", "alert-danger")
        return redirect(url_for('session', session_id=session.id))

    sessions_chain = session.get_chain()

    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id

    # don't allow deletion if it is not the last one
    # and not ratt and not historic
    if session.get_next() is not None and not session.is_rattrapage and not session.is_historic:
        flash("you can't delete this Semester because it not the last one", 'alert-danger')
        return redirect(url_for('session', session_id=session.id))

    if session.is_closed is True:
        flash('Semester ('+str(session_id)+') was not deleted because it is Closed', 'alert-danger')
    else:
        # you can't delete a session if it has an AnnualSession

        # # 
        # # if rattrapage    delete annual first
        # # 
        # if session.is_rattrapage:
        #     annual_session = session.annual_session
        #     if annual_session != None:
        #         db.session.delete(annual_session)
        # # 
        # # 
        # # 
        annual_dict = session.get_annual_dict()
        if annual_dict['A'] == -1:
            # cleaning
            for ss in session.student_sessions:
                Grade.query.filter_by(student_session_id=ss.id).delete()
                GradeUnit.query.filter_by(student_session_id=ss.id).delete()
                db.session.delete(ss)
            db.session.delete(session)
            db.session.commit()
            flash('Semester ('+str(session_id)+') deleted')
        else:
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # if rattrapage
            if session.is_rattrapage:
            # cleaning
                for ss in session.student_sessions:
                    Grade.query.filter_by(student_session_id=ss.id).delete()
                    GradeUnit.query.filter_by(student_session_id=ss.id).delete()
                    db.session.delete(ss)
                db.session.delete(session)
                db.session.commit()
                flash('Semester ('+str(session_id)+') deleted')
            # 
            # 
            # 
            # 
            # 
            # 
            else:
            # 
            # 
            # 
            # 
            # 
            # 
                flash("you can't delete a Session related to an Annual", 'alert-danger')
        
    return redirect(url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id))

#######################################

@app.route('/session/<session_id>/config/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_session.session.config', 'Session Config' )
def session_config(session_id=0):
    session = Session.query.get_or_404(session_id)
    form = SessionConfigForm(session.id)

    # be carefull of existing Semesters

    if form.validate_on_submit():
        session.name = form.name.data
        session.start_date = form.start_date.data
        session.finish_date = form.finish_date.data
        # session.semester_id = form.semester_id.data
        session.type = form.type.data
        db.session.commit()
        # if session.is_historic:
        #     init_all(session)
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('session', session_id=session_id))
    elif request.method == 'GET':
        form.name.data = session.name
        form.start_date.data = session.start_date
        form.finish_date.data = session.finish_date
        # form.semester_id.data = session.semester_id
        # form.type.data = session.type
        form.is_historic.data = session.is_historic
    return render_template('session/session-config.html', 
        title='Session Config', form=form)

def create_data_session_historic(session):
    data_arr = ''
    student_sessions = StudentSession.query.filter_by(session_id=session.id)\
            .join(Student).order_by(Student.username).all()

    for student_session in student_sessions:
        student = student_session.student

        id = 'id: ' + str(student_session.id) + ', '
        name = 'name: "' + student.username+' - '+ student.last_name+' '+student.first_name + '", '
        average = 'average: ' + str(student_session.average) + ', '
        credit = 'credit: ' + str(student_session.credit) + ', '

        data_arr += '{'+ id + name + average + credit +'}, '

    return '[ ' + data_arr + ' ]'

@app.route('/session-historic/save/', methods = ['GET', 'POST'])
def session_historic_save():
    data_arr = request.json
    
    for data in data_arr:
        student_session = StudentSession.query.filter_by(id = int(data['id'])).first()

        # check if the student_sessino_id is a Historic
        session = student_session.session
        if not session.is_historic:
            return "returned before finoshing because it's Not Historic"

        # saved fields must be according to the Permission
        student_session.average = data['average']
        student_session.credit = data['credit']

    db.session.commit()

    return 'data saved'




#####################################################################################
#####                                                                           #####
#####    ######  ##          ###     ######   ######  ######## ##     ##        #####
#####   ##    ## ##         ## ##   ##    ## ##    ## ##       ###   ###        #####
#####   ##       ##        ##   ##  ##       ##       ##       #### ####        #####
#####   ##       ##       ##     ##  ######   ######  ######   ## ### ##        #####
#####   ##       ##       #########       ##       ## ##       ##     ##        #####
#####   ##    ## ##       ##     ## ##    ## ##    ## ##       ##     ## ###    #####
#####    ######  ######## ##     ##  ######   ######  ######## ##     ## ###    #####
#####                                                                           #####
#####################################################################################
                                                                      
def init_classement_laureats(promo_id):
    students = Student.query.join(StudentSession).join(Session).filter_by(promo_id=promo_id).all()
    student_in_classements = Student.query.join(Classement).filter_by(promo_id=promo_id).all()

    # insert missing students in classement
    for student in students:
        if student not in student_in_classements:
            classement = Classement(promo_id=promo_id, student_id=student.id)
            db.session.add(classement)
            student_in_classements.append(student)
    db.session.commit()

    promo = Promo.query.get_or_404(promo_id)
    annuals = promo.branch.annuals
    # semesters = annuals[0].semesters

    classements = Classement.query.filter_by(promo_id=promo_id).all()

    # insert missing students in classement_years
    for classement in classements:
        # fill classement_year
        for annual in annuals:
            classement_year = ClassementYear.query\
                .filter_by(classement_id=classement.id, year=annual.annual).first()
            if classement_year == None:
                classement_year = ClassementYear(
                    classement_id=classement.id, 
                    year=annual.annual
                )
                # 
                # 
                ##### disabled it to avoid creating classement_year
                # 
                # db.session.add(classement_year)
                # 
                # 

    for classement in classements:
        # fill classement_year
        for annual in annuals:
            # fill classement_semester
            for cy in classement.classement_years:
                for semester in annual.semesters:
                    classement_semester = ClassementSemester.query.filter_by(
                            classement_year_id = cy.id,
                            semester = semester.semester
                        ).first()
                    if classement_semester == None:
                        classement_semester = ClassementSemester(
                            classement_year_id=cy.id,
                            semester = semester.semester
                        )
                        db.session.add(classement_semester)
            
    db.session.commit()

    #
    # remove excess from Classement and ClassementYear
    #
    #
    return 'init_classement_laureats'

def fill_classement_laureats_data(promo_id):
    promo = Promo.query.get_or_404(promo_id)
    classement_years = ClassementYear.query.join(Classement)\
        .filter_by(promo_id=promo_id).join(Student)\
        .order_by(Student.username, ClassementYear.year).all()
    for classement_year in classement_years:
        student_id = classement_year.classement.student_id
        annual = classement_year.year
        annual_grade = AnnualGrade.query.filter_by(student_id=student_id)\
            .join(AnnualSession).filter_by(promo_id=promo_id)\
            .join(Annual).filter_by(annual=annual).first()
        if annual_grade != None:
            # from annual_grade fill the fields
            classement_year.average_app = annual_grade.average_final
            classement_year.credit_app = annual_grade.credit_final
            # classement_year.decision_app = annual_grade.obs
            # classement_year.decision_app = annual_grade.observation
            classement_year.decision_app = annual_grade.decision

            # 
            # fill classement_semester
            for classement_semester in classement_year.classement_semesters:
                cs = classement_semester
                ag = annual_grade
                # fill semester 1
                if cs.semester == 1:
                    cs.average_app = ag.avr_r_1 if ag.avr_r_1 != None else ag.avr_1
                    cs.credit_app = ag.cr_r_1 if ag.cr_r_1 != None else ag.cr_1
                # fill semester 2
                if cs.semester == 2:
                    cs.average_app = ag.avr_r_2 if ag.avr_r_2 != None else ag.avr_2
                    cs.credit_app = ag.cr_r_2 if ag.cr_r_2 != None else ag.cr_2

    db.session.commit()

    # calculate_cumul field
    calculate_cumul_field(classement_years)

    return 'fill_classement_laureats_data'

# def calculate_cumul_field(promo_id):
def calculate_cumul_field(classement_years):
    student_id = None
    cumul = None
    prev_cumul = None
    for cy in classement_years:
        credit = cy.credit if cy.credit != None else cy.credit_app if cy.credit_app != None else 0
        if student_id != cy.classement.student_id:
            student_id = cy.classement.student_id
            cumul = credit
        else:
            cumul = cumul + credit

        if cy.credit == None and cy.credit_app == None:
            cy.credit_cumul = None
        else:
            cy.credit_cumul = cumul

    db.session.commit()
    return 'calculate_cumul_field'

def calulate_avr_classement(promo_id):
    promo = Promo.query.get_or_404(promo_id)
    classement_years = ClassementYear.query.join(Classement).filter_by(promo_id=promo_id)\
        .join(Student).order_by(Student.username, ClassementYear.year).all()

    getcontext().prec = 4
    for cy in classement_years:
        average_app = cy.average_app if cy.average_app != None else 0
        average =   cy.average if cy.average != None else average_app
        R_app = cy.R_app if cy.R_app != None else 0
        R =   cy.R if cy.R != None else R_app
        S_app = cy.S_app if cy.S_app != None else 0
        S =   cy.S if cy.S != None else S_app
        
        cy.avr_classement = average * (1 - Decimal((R+S)/20) )

    db.session.commit()

    return 'calulate_avr_classement'


DESICIONS = {
    'rattrapage': {
        'observation': 'Rattrapage',
        'obs_html': '<span class="label label-warning">Rattrapage</span>'
    },
    'admis_avec_dettes': {
        'observation': 'Admis avec dettes',
        'obs_html': '<span class="label label-warning">Admis avec dettes</span>'
    },
    'ajournee': {
        'observation': 'Ajournée',
        'obs_html': '<span class="label label-danger">Ajournée</span>'
    },
    'admis': {
        'observation': 'Admis',
        'obs_html': '<span class="label label-success">Admis</span>'
    },
    'admis_apres_ratt': {
        'observation': 'Admis apres Ratt.',
        'obs_html': '<span class="label label-info">Admis apres Ratt.</span>'
    }
}

def get_desions_list():
    desions_list = ['']
    for key in DESICIONS:
        desions_list.append( DESICIONS[key]['observation'] )

    return desions_list


def decision_to_html(decision):
    if decision in DESICIONS:
        return DESICIONS[decision]['obs_html']
    return ''

def decision_to_observation(decision):
    if decision in DESICIONS:
        return DESICIONS[decision]['observation']
    return ''

def observation_to_decision(observation):
    for key in DESICIONS:
        if DESICIONS[key]['observation'] == observation:
            return key
    return ''




def create_classement_merge_arr(classements, years, semesters):
    mergeCells = ''
    last_i = None
    for index, cs in enumerate(classements):
        i =  str( int( (index-(index%semesters))/semesters ) )  
        
        if i != last_i:
            col1 = ' {row:'+str(index)+', col:1, rowspan:'+str(semesters)+', colspan:1}, '
            col2 = ' {row:'+str(index)+', col:2, rowspan:'+str(semesters)+', colspan:1}, '
            col3 = ' {row:'+str(index)+', col:3, rowspan:'+str(semesters)+', colspan:1}, '
            mergeCells += col1 + col2  + col3

            for year in range(years):
                row = str(index + (year * 2) )
                col4 = ' {row: '+row+', col:4, rowspan: 2, colspan:1}, '
                col5 = ' {row: '+row+', col:5, rowspan: 2, colspan:1}, '
                col6 = ' {row: '+row+', col:6, rowspan: 2, colspan:1}, '
                col7 = ' {row: '+row+', col:7, rowspan: 2, colspan:1}, '
                col8 = ' {row: '+row+', col:8, rowspan: 2, colspan:1}, '
                col9 = ' {row: '+row+', col:9, rowspan: 2, colspan:1}, '
                col10 = ' {row: '+row+', col:10, rowspan: 2, colspan:1}, '

                col11 = ' {row: '+row+', col:11, rowspan: 2, colspan:1}, '
                col12 = ' {row: '+row+', col:12, rowspan: 2, colspan:1}, '
                col13 = ' {row: '+row+', col:13, rowspan: 2, colspan:1}, '
                col14 = ' {row: '+row+', col:14, rowspan: 2, colspan:1}, '
                col15 = ' {row: '+row+', col:15, rowspan: 2, colspan:1}, '
                mergeCells += col4 + col5 + col6 + col7 + col8 + col9 \
                    + col10 + col11 + col12 + col13 + col14 + col15
            
            last_i = i

    return '[ ' + mergeCells + ' ]'

def create_classement_data_grid(classements, years, semesters):
    data_arr = ''
    for index, cs in enumerate(classements):
        s = cs.classement_year.classement.student
        cy = cs.classement_year

        id = 'id: ' + str(cs.id) + ', '
        index = 'index: "' + str( int( (index-(index%semesters))/semesters ) + 1 ) + '", '
        name = 'name: "' + s.username+' - '+ s.last_name +' '+ s.first_name + '", '
        average = 'average: ' + str(cs.classement_year.classement.avr_classement) + ', '
        
        # Annual
        year = 'year: ' + str(cy.year) + ', '
        average_a = 'average_a: ' + str(cy.average) + ', '
        average_app_a = 'average_app_a: ' + str(cy.average_app) + ', '
        credit_a = 'credit_a: ' + str(cy.credit) + ', '
        credit_app_a = 'credit_app_a: ' + str(cy.credit_app) + ', '
        credit_cumul = 'credit_cumul: ' + str(cy.credit_cumul) + ', '

        dec = "" if cy.decision == None\
             else decision_to_observation(cy.decision)
        decision = 'decision: "' + str(dec) + '", '
        dec_app = "" if cy.decision_app == None\
             else decision_to_observation(cy.decision_app)
        decision_app = 'decision_app: "' + str(dec_app) + '", '

        R = 'R: ' + str(cy.R) + ', '
        R_app = 'R_app: ' + str(cy.R_app) + ', '
        S = 'S: ' + str(cy.S) + ', '
        S_app = 'S_app: ' + str(cy.S_app) + ', '
        avr_classement_a = 'avr_classement_a: ' + str(cy.avr_classement) + ', '


        # Semester
        semester_nbr = (cy.year * 2) - 2 + cs.semester
        semester = 'semester: ' + str(semester_nbr) + ', '
        average_s = 'average_s: ' + str(cs.average) + ', '
        average_app_s = 'average_app_s: ' + str(cs.average_app) + ', '
        credit_s = 'credit_s: ' + str(cs.credit) + ', '
        credit_app_s = 'credit_app_s: ' + str(cs.credit_app) + ', '

        b = 'b: ' + str(cs.b) + ', '
        b_app = 'b_app: ' + str(cs.b_app) + ', '
        d = 'd: ' + str(cs.d) + ', '
        d_app = 'd_app: ' + str(cs.d_app) + ', '
        s = 's: ' + str(cs.s) + ', '
        s_app = 's_app: ' + str(cs.s_app) + ', '
        avr_classement_s = 'avr_classement_s: ' + str(cs.avr_classement) + ', '


        data_arr += '{'+ id + index + name + average + year \
             + average_a + average_app_a + credit_a + credit_app_a + credit_cumul \
             + decision + decision_app + avr_classement_a  \
             + R + R_app + S + S_app \
             + semester + average_s + average_app_s + credit_s + credit_app_s \
             + b + b_app + d + d_app + s + s_app + '}, '

    return '[ ' + data_arr + ' ]'


@app.route('/classement-laureats/promo/<promo_id>/mode/<mode>', methods=['GET'])
@app.route('/classement-laureats/promo/<promo_id>/', methods=['GET'])
@register_breadcrumb(app, '.tree_promo.classement_laureats', 'Classement Laureats')
def classement_laureats(promo_id=0, type_id=0, mode=''):
    # now it init if it doesn't exist
    # add later the option to delete and init
    # msg1 = init_classement_laureats(promo_id)
    # 
    # 
    # 
    msg2 = fill_classement_laureats_data(promo_id)
    msg3 = calulate_avr_classement(promo_id)

    promo = Promo.query.get_or_404(promo_id)
    years = promo.branch.years_from_config()
    # semesters = promo.branch.semesters_from_config()
    semesters = years * 2

    classements = ClassementSemester.query\
        .join(ClassementYear)\
        .join(Classement).filter_by(promo_id=promo_id)\
        .join(Student)\
        .order_by(Student.username, ClassementYear.year, ClassementSemester.semester)\
        .all()

    mergeCells = create_classement_merge_arr(classements, years, semesters)
    data_arr = create_classement_data_grid(classements, years, semesters)
    

    # decisions_list = ['', 'Rattrapage', 'Admis avec dettes', 'Ajournée', 'Admis', 'Admis apres Ratt.']
    decisions_list = get_desions_list()


    return render_template( 'classement-laureats/classement-laureats.html', 
        data_arr=data_arr, mergeCells=mergeCells, 
        years=years, decisions_list=decisions_list, mode=mode)

@app.route('/classement-laureats/save/', methods = ['POST'])
def classement_laureats_save():
    data_arr = request.json

    for i, data in enumerate(data_arr, start=0):
        # 
        # WRONG: id is the id of ClassementSemester not ClassementYear
        # 
        cs = ClassementSemester.query.get(data['id'])

        # saved fields must be according to the Permission
        
        # Saving CalssementSemester
        cs.average = data['average_s']
        cs.credit = data['credit_s']

        cs.b = data['b']
        cs.d = data['d']
        cs.s = data['s']

        # Saving CalssementYear
        if i % 2 == 0:
            cy = cs.classement_year
            cy.average = data['average_a']
            cy.credit = data['credit_a']
            cy.R = data['R']
            cy.S = data['S']

            observation = observation_to_decision(data['decision'])
            if observation != None and observation != '':
                cy.decision = observation
            else:
                cy.decision = None


    db.session.commit()

    # return str(data_arr)
    return 'data saved'



#######################################
#####    Classement in Session    #####
#######################################

@app.route('/session/<session_id>/classement/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_session.session.result.classement', 'Classement')
def classement(session_id):
    student_sessions = StudentSession.query\
        .filter_by(session_id=session_id)\
        .order_by(StudentSession.average.desc()).all()
    session = Session.query.get_or_404(session_id)
    title = 'classement'
    return render_template('session/classement.html',
         title=title, session=session, student_sessions=student_sessions)

@app.route('/session/<session_id>/classement-print/', methods=['GET', 'POST'])
def classement_print(session_id):
    student_sessions = StudentSession.query\
        .filter_by(session_id=session_id)\
        .order_by(StudentSession.average.desc()).all()
    session = Session.query.get_or_404(session_id)
    header = make_header_semester_print(session, 'Classement Semestre ('+str(session.semester.get_nbr())+')' )
    title = make_title_semester_print(session, label="Classement")
    return render_template('session/classement-print.html',
         title=title, session=session, header=header, student_sessions=student_sessions)


######################################################
#####                                            #####
#####   ########     ###    ######## ########    #####
#####   ##     ##   ## ##      ##       ##       #####
#####   ##     ##  ##   ##     ##       ##       #####
#####   ########  ##     ##    ##       ##       #####
#####   ##   ##   #########    ##       ##       #####
#####   ##    ##  ##     ##    ##       ##       #####
#####   ##     ## ##     ##    ##       ##       #####
#####                                            #####
######################################################

def create_rattrapage(session_id):
    session = Session.query.get_or_404(session_id)
    annual_dict = session.get_annual_dict()

    create_R1 = annual_dict['S1']==int(session_id) and annual_dict['R1']==-1
    create_R2 = annual_dict['S2']==int(session_id) and annual_dict['R2']==-1
    
    if create_R1 == True or create_R2 == True:
        new_session = Session(
            semester_id=session.semester_id, 
            promo_id=session.promo_id, 
            is_rattrapage=True, 
            annual_session_id=session.annual_session_id,
            # type=session.type
            is_historic=session.is_historic)
        # set start_date and finish_date    
        # would it reference Semester before it is saved ???
        new_session.configuration = session.configuration
        db.session.add(new_session)
        db.session.commit()
        return new_session
    else:
        # if it Ratt exists
        if annual_dict['S1'] == session.id:
            return Session.query.get_or_404( annual_dict['R1'] )
        if annual_dict['S2'] == session.id:
            return Session.query.get_or_404( annual_dict['R2'] )

    # # if Rattrapage exist -> it is next
    return session


# def transfer_grade_student_module(grade_from, grade_to, module_sess_from=None, module_sess_to=None):

#     return 'transfer grade student module'



def make_ratt_grade(grade, session_id, student_id, student_session_ratt_id):
    # ratt_modules = get_ratt_modules_list_semester(session_id, student_id)
    student_session = StudentSession.query.filter_by(session_id=session_id, student_id=student_id).first()
    ratt_modules = student_session.get_ratt_modules_list_semester()


    grade_in_ratt = Grade.query.filter_by(
        student_session_id=student_session_ratt_id, 
        module_id=grade.module_id).first()


    is_rattrapage = False
    if grade.module_id in ratt_modules:
        is_rattrapage = True

    # transfaire to new grade
    new_grade = Grade(
        student_session_id=student_session_ratt_id, 
        module_id=grade.module_id, 
        formula=grade.formula, 
        is_rattrapage=is_rattrapage
    )

    ## fill fields from grade.formula
    # { 'cour': 0, 'tp': 0, 'stage': 0, 
    #   'coefficient':4, 'credit':6, 
    #   'rattrapable': 'cour'
    # }
    dictionary = literal_eval(grade.formula)
    for field in dictionary:
        if field in ['cour', 'td', 'tp', 't_pers', 'stage']:
            val = getattr(grade, field)

            # skip rattrapable field if is_rattrapage
            if new_grade.is_rattrapage and field == dictionary['rattrapable']:
                val = None
                if grade_in_ratt != None:
                    val = getattr(grade_in_ratt, field)

            if grade.saving_grade != None:
                module_session = ModuleSession.query.filter_by(
                    module_id=grade.module_id).first()
                if module_session.saving_enabled:
                    val = grade.saving_grade

            setattr(new_grade, field, val)



    # if it exists save "Rattrabable" and delete record
    if grade_in_ratt is not None:
        db.session.delete(grade_in_ratt)

    return new_grade


def transfer_grades(session_id, ratt_id, student_session_ratt_id, student_id):
    grades = Grade.query.join(StudentSession)\
        .filter_by(session_id=session_id, student_id=student_id)\
        .all()

    for grade in grades:
        #
        #
        #
        #
        #
        #
        new_grade = make_ratt_grade(
            grade, 
            session_id, 
            student_id, 
            student_session_ratt_id
        )
        #
        #
        #
        #
        #
        #
        db.session.add(new_grade)

    return 'transfer grades'

def transfer_student_session(session_from, session_to, student_id):
    student_session = StudentSession.query\
        .filter_by(session_id=session_to, student_id=student_id)\
        .first()
    if student_session == None:
        student_session = StudentSession(session_id=session_to, student_id=student_id)
        db.session.add(student_session)
        db.session.commit()
    return student_session

def get_student_id_todo_rattrapage_semester(session_id):
    session = Session.query.get_or_404(session_id)
    student_sessions = session.get_students_to_enter_rattrapage()
    student_ids = []
    for student_session in student_sessions:
        student_ids.append(student_session.student.id)
    return student_ids

def create_rattrapage_sem(session_id, students):
    session = Session.query.get_or_404(session_id)
    students_todo_ratt = get_student_id_todo_rattrapage_semester(session_id)

    # don't create if there is no students
    if len(students_todo_ratt) == 0:
        return None

    # create ratt
    session_rattrapage = create_rattrapage(session_id)
    ratt_id = session_rattrapage.id

    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # transfer module_session_s
    module_session_s_sem = session.module_sessions
    for module_session_sem in module_session_s_sem:
        # if it exists transfer it
        if module_session_sem != None:
            # find if already exist
            module_session_ratt = ModuleSession.query.filter_by(
                session_id=session_rattrapage.id,
                module_id=module_session_sem.module_id).first()
            if module_session_ratt == None: # create it
                module_session_ratt = ModuleSession(session_id=session_rattrapage.id)
                db.session.add(module_session_ratt)
            module_session_ratt.module_id = module_session_sem.module_id
            module_session_ratt.teacher_id = module_session_sem.teacher_id
            #
            #
            #
            # module_session_ratt.saving_enabled = module_session_sem.saving_enabled
            #
            #
            #
    db.session.commit()

    # transfair students
    for student_id in students:
        # check the student need to enter RATT in this session
        if int(student_id) in students_todo_ratt:
            student_session_ratt = transfer_student_session(session_id, ratt_id, student_id)
            # if not historic
            if not session.is_historic:
                #
                #
                #
                #
                #
                transfer_grades(session_id, ratt_id, student_session_ratt.id, student_id)
                # student = Student.query.get(student_id)
                # transfer_grades(session, student_session_ratt, student)
                #
                #
                #
                #
                #
    db.session.commit()

    # initialize & calculate
    init_all(session_rattrapage)
    # if not historic
    if not session.is_historic:
        session_rattrapage.calculate()

    db.session.commit()

    #
    #
    #
    # don't forget to transfer the grades (cout=saving, tp=saving, td=saving)
    #       if the module is saving_enabled
    #       and i have to do it be 
    #
    #
    #
    return session_rattrapage

@app.route('/session/<session_id>/create-rattrapage/', methods=['GET', 'POST'])
def create_rattrapage_semester(session_id=0):
    session = Session.query.get_or_404(session_id)
    if session.is_closed == True:
        flash("You can't create Rattrapage from a closed Session", 'alert-danger')
        return redirect(url_for('students_rattrapage_semester', session_id=session_id))

    students = request.form.getlist('students[]')
    # create rattrapage
    session_rattrapage = create_rattrapage_sem(session_id, students)
    flash("Rattrapage was created", 'alert-success')
    return redirect(url_for('session', session_id=session_rattrapage.id))

@app.route('/create-next-session/promo/<promo_id>/', methods=['GET', 'POST'])
def create_next_session(promo_id=0):
    promo = Promo.query.get_or_404(promo_id)
    next_semester = promo.get_next_semester()

    url = url_for('create_session', promo_id=promo.id, semester_id=next_semester.id)
    return redirect( url_for('slow_redirect', url=url) )

    return ' *** create_next_session *** '

def has_next(promo_id, semester_id):
    sessions = Session.query.filter_by(promo_id=promo_id).join(Semester)\
        .join(Annual).order_by(Annual.annual, Semester.semester).all()

    existing_sem_nbrs = []
    for session in sessions:
        existing_sem_nbrs.append( session.semester.get_nbr() )

    semester = Semester.query.get_or_404(semester_id)
    current_nbr = semester.get_nbr()

    for exist_nbrs in existing_sem_nbrs:
        if exist_nbrs > current_nbr:
            return True
    
    return False




def create_session__(promo_id, semester_id):
    session = None

    sessions = Session.query.filter_by(
        promo_id=promo_id, semester_id=semester_id, is_rattrapage=False).all()
    if len(sessions) > 0:
        # check if the session of this semester exists
        session = Session.query\
            .filter_by(promo_id=promo_id, semester_id=semester_id, is_rattrapage=False)\
            .first()
        if session is not None:
            flash('Semester (' + str(session.semester.get_nbr()) + ') already exist', 'alert-warning')
    else:
        is_historic = False
        if has_next(promo_id, semester_id):  
           is_historic = True


        session = Session(promo_id=promo_id, semester_id=semester_id, is_historic=is_historic)
        db.session.add(session)
        db.session.commit()

        init_annual_session_id(session.id)
        flash('Semester (' + str(session.semester.get_nbr()) + ') created', 'alert-success')

    # transfair students
    previous_normal = session.get_previous_normal()
    if previous_normal != None:
        for student in previous_normal.student_sessions:
            transfer_student_session(previous_normal.id, session.id, student.student_id)
        init_all(session)

    # to fill configuration at creation
    update_session_configuraton(session)

    return session


@app.route('/create-session-api/', methods=['POST'])
def create_session_api():
    data = request.get_json(force=True) 

    promo_id = data['promo_id']
    semester_id = data['semester_id']

    print('')
    print('promo_id: ' + str(promo_id))
    print('semester_id: ' + str(semester_id))
    print('')

    session = create_session__(promo_id, semester_id)
    # if :
    # flash('Semester: {} was created'.format( session.semester.get_nbr() ))


    promo = Promo.query.get(promo_id)
    branch_id = promo.branch.id
    school_id = promo.branch.school.id
    url = url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id)

    return {"session_id": session.id, "rediret_to_url": url}


@app.route('/create-session/promo/<promo_id>/semester/<semester_id>/', methods=['GET', 'POST'])
def create_session(promo_id=0, semester_id=0):
    session = create_session__(promo_id, semester_id)
    
    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id
    return redirect( url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id) )


######################
### NEW RATTRAPAGE ###

@app.route('/session/<session_id>/rattrapage/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_session.session.rattrapage', 'Rattrapage')
def students_rattrapage_semester(session_id=0):
    session = Session.query.get_or_404(session_id)
    students = session.get_students_to_enter_rattrapage()
    return render_template('session/students-rattrapage-semester.html', 
        title='ratt-semester', students=students, session=session)

@app.route('/session/<session_id>/rattrapage-print/', methods=['GET', 'POST'])
def students_rattrapage_semester_print(session_id=0):
    session = Session.query.get_or_404(session_id)
    students = session.get_students_to_enter_rattrapage()
    header = make_header_semester_print(session, 'Rattrapage ('+str(session.semester.semester)+')')
    title = make_title_semester_print(session, label="Rattrapage Semestre")
    return render_template('session/students-rattrapage-semester-print.html', 
        title=title, students=students, header=header)





#########################################################################
#####                                                               #####
#####       ###    ##    ## ##    ## ##     ##    ###    ##         #####
#####      ## ##   ###   ## ###   ## ##     ##   ## ##   ##         #####
#####     ##   ##  ####  ## ####  ## ##     ##  ##   ##  ##         #####
#####    ##     ## ## ## ## ## ## ## ##     ## ##     ## ##         #####
#####    ######### ##  #### ##  #### ##     ## ######### ##         #####
#####    ##     ## ##   ### ##   ### ##     ## ##     ## ##         #####
#####    ##     ## ##    ## ##    ##  #######  ##     ## ########   #####
#####                                                               #####
#########################################################################


@app.route('/annual-session/<annual_session_id>/create-rattrapage/', methods=['GET', 'POST'])
def create_rattrapage_annual(annual_session_id=0):
    students = request.form.getlist('students[]')

    annual_session = AnnualSession.query.get_or_404(annual_session_id)
    sessions = annual_session.sessions
    for session in sessions:
        create_rattrapage_sem(session.id, students)

    promo = annual_session.promo
    school_id = promo.branch.school_id
    branch_id = promo.branch_id
    promo_id = promo.id
    flash("All Rattrapages were created", 'alert-success')
    return redirect(url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id))

@app.route('/annual-session/<annual_session_id>/rattrapage/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_annual.annual.rattrapage', 'Annual Rattrapage')
def students_rattrapage_annual(annual_session_id=0):
    # students = get_students_to_enter_rattrapage_annual(annual_session_id)
    annual_session = AnnualSession.query.get_or_404(annual_session_id)
    students = annual_session.get_students_to_enter_rattrapage()

    return render_template('session/students-rattrapage-annual.html', 
        title='ratt-annual', students=students, annual_session=annual_session)

@app.route('/annual-session/<annual_session_id>/rattrapage-print/', methods=['GET', 'POST'])
def students_rattrapage_annual_print(annual_session_id=0):
    # students = get_students_to_enter_rattrapage_annual(annual_session_id)
    annual_session = AnnualSession.query.get_or_404(annual_session_id)
    students = annual_session.get_students_to_enter_rattrapage()

    header = make_header_annual_print(annual_session, 'Rattrapage Annuelle')
    title = make_title_annual_print(annual_session, "Rattrapage Annuelle")
    return render_template('session/students-rattrapage-annual-print.html', 
        title=title, students=students, header=header)


# headers #
def make_header_annual_print(annual_session, label="**label**"):
    school = annual_session.annual.branch.school.description
    branch = annual_session.annual.branch.description

    annual = annual_session.annual.get_string_literal()
    promo = annual_session.promo.name
    annual_pedagogique = annual_session.sessions[0].get_annual_pedagogique()

    header = F"""
      <div class="container" style="display: flex;">
        <div style="flex-grow: 1;">
            {school}<br/>
            Sous Direction des Affaires Pèdagogiques<br/>
            Département d'evaluation
        </div>
        <div style="flex-grow: 1;" align="center">
            Promo {promo}<br/>
            Année {annual_pedagogique}<br/>
            <b><font size="+2">{label}</font></b>
        </div>
        <div style="flex-grow: 1;" align="right">
            {annual}<br/>
            {branch}
        </div>
      </div>
    """
    return header

def make_header_semester_print(session, label="**label**"):
    school = session.promo.branch.school.description
    branch = session.promo.branch.description

    annual = session.semester.annual.get_string_literal()
    promo = session.promo.name
    annual_pedagogique = session.get_annual_pedagogique()

    label = label.replace(' ', ' ')

    header = F"""
      <div class="container" style="display: flex;">
        <div style="flex-grow: 1;">
            {school}<br/>
            Sous Direction des Affaires Pèdagogiques<br/>
            Département d'evaluation
        </div>
        <div style="flex-grow: 1;" align="center">
            Promo {promo}<br/>
            Année {annual_pedagogique}<br/>
            <b><font size="+2">{label}</font></b>
        </div>
        <div style="flex-grow: 1;" align="right">
            {annual}<br/>
            {branch}
        </div>
      </div>
    """
    return header

def make_title_annual_print(annual_session, label="**label**"):
    annual = str(annual_session.annual.annual)
    promo = annual_session.promo.name
    ann_pedagog = annual_session.get_annual_pedagogique()
    dt = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    title = label +' A('+annual+') ['+promo+' - '+ann_pedagog+'] {'+str(dt)+'}'
    return title


def make_title_semester_print(session, label="**label**"):
    semester = str(session.semester.get_nbr())
    annual = str(session.semester.annual.annual)
    promo = session.promo.name
    ann_pedagog = session.get_annual_pedagogique()
    dt = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    title = label +' S('+semester+') A('+annual+') ['+promo+' - '+ann_pedagog+'] {'+str(dt)+'}'
    return title

def make_title_semester_print_by_student(session, student, label="**label**"):
    semester = str(session.semester.get_nbr())
    annual = str(session.semester.annual.annual)
    promo = session.promo.name
    ann_pedagog = session.get_annual_pedagogique()
    dt = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    name = student.username+' - '+student.last_name+' '+student.first_name
    title = label +' S('+semester+') A('+annual+') '+name+' ['+promo+' - '+ann_pedagog+'] {'+str(dt)+'}'
    return title

def get_student_annual_list(annual_session, annual_dict):
    session_1 = annual_dict['S1']
    session_2 = annual_dict['S2']
    
    student_sessions = StudentSession.query\
        .filter( StudentSession.session_id.in_([session_1, session_2]) ).all()
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
def init_annual_grade(annual_session):
    annual_dict = annual_session.get_annual_dict()

    student_ids = get_student_annual_list(annual_session, annual_dict)
    # then fill annual grade if the record does not exist
    for student_id in student_ids:
        annual_grade = AnnualGrade.query\
            .filter_by(annual_session_id=annual_session.id, student_id=student_id)\
            .first()
        if annual_grade == None:
            annual_grade = AnnualGrade( annual_session_id=annual_session.id, student_id=student_id )
            db.session.add(annual_grade)
    db.session.commit()

    # NOTE:
    # delete users in Table Who are not supposed to be in annual
    students_annual = AnnualGrade.query.filter_by(annual_session_id=annual_session.id).all()
    students_annual_list = [s_a.student_id for s_a in students_annual]

    for student_id in students_annual_list:
        if student_id not in student_ids:
            annual_grade = AnnualGrade.query\
                .filter_by(annual_session_id=annual_session.id, student_id=student_id)\
                .first()
            db.session.delete(annual_grade)
    db.session.commit()

    return 'init_annual_grade'

def fetch_data_annual_session(annual_session):
    annual_grades = annual_session.annual_grades
    for ag in annual_grades:
        ag.fetch_data()

    db.session.commit()
    return "fetch_data_annual_session"


def make_link(ag, col, annual_dict):

    session_id = annual_dict[col]

    if session_id == -1:
        if col == 'S1':
            return str(ag.avr_1)
        if col == 'S2':
            return str(ag.avr_2)
        if col == 'R1':
            return str(ag.avr_r_1)
        if col == 'R2':
            return str(ag.avr_r_2)

    student = ag.student
    session = Session.query.get(session_id)
    if session == None:
        return ''

    href = ''
    avr = ''
    if col == 'S1':
        href = url_for('grade', session_id=session.id, student_id=student.id)
        avr = str(ag.avr_1)
    if col == 'S2':
        href = url_for('grade', session_id=session.id, student_id=student.id)
        avr = str(ag.avr_2)
    if col == 'R1':
        href = url_for('grade', session_id=session.id, student_id=student.id)
        avr = str(ag.avr_r_1)
    if col == 'R2':
        href = url_for('grade', session_id=session.id, student_id=student.id)
        avr = str(ag.avr_r_2)

    return '<a href="'+href+'">'+avr+'</a>'



def collect_data_annual_session(annual_session, sort='', historic_exist=False):
    annual_dict = annual_session.get_annual_dict()
    student_ids = get_student_annual_list(annual_session, annual_dict)

    annual_grades = []
    if sort == 'desc':
        annual_grades = AnnualGrade.query.filter_by(annual_session_id=annual_session.id)\
            .order_by(AnnualGrade.average_final.desc()).all()
    else:
        annual_grades = AnnualGrade.query.filter_by(annual_session_id=annual_session.id).all()

    array_data = []
    for index, ag in enumerate(annual_grades):
        student = ag.student
        
        cross_s1 = 'line-through' if ag.avr_r_1 != None else ''
        cross_s2 = 'line-through' if ag.avr_r_2 != None else ''
        cross_average = 'line-through' if ag.avr_r_1 != None or ag.avr_r_2 != None else ''


        bg_s1 = 'bg-yellow' if ag.cr_1 != None and ag.cr_1 < 30 else ''
        bg_s2 = 'bg-yellow' if ag.cr_2 != None and ag.cr_2 < 30 else ''
        bg_ann = 'bg-yellow-annual' if ag.credit != None and ag.credit < 60 else ''

        bg_s1_r = 'bg-yellow' if ag.cr_r_1 != None and ag.cr_r_1 < 30 else ''
        bg_s2_r = 'bg-yellow' if ag.cr_r_2 != None and ag.cr_r_2 < 30 else ''
        bg_ann_r = 'bg-yellow-annual' if ag.credit_r != None and ag.credit_r < 60 else ''

        bg_final = ''
        if ag.credit_final != None and ag.credit_final >= 30 and ag.credit_final < 60:
            bg_final = 'bg-yellow-annual'

        if ag.credit_final != None and ag.credit_final < 30:
            bg_final = 'bg-red'

        url = url_for('bultin_annual_print', annual_session_id=annual_session.id, student_id=student.id)
        bultin = '''<a href ="''' +  url + '''" class="btn btn-primary btn-xs" target="_blank" role="button"> Bultin </a>'''

        url_ratt = url_for('bultin_annual_print', annual_session_id=annual_session.id, student_id=student.id)
        bultin_ratt = '''<a href ="''' +  url_ratt + '''" class="btn btn-primary btn-xs" target="_blank" role="button"> Bultin Ratt </a>'''

        ratt = '' if ag.enter_ratt == False else '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'

        
        # S1 S2 R1 R2
        link_avr_1 = make_link(ag, 'S1', annual_dict)
        link_avr_2 = make_link(ag, 'S2', annual_dict)

        link_avr_r_1 = make_link(ag, 'R1', annual_dict)
        link_avr_r_2 = make_link(ag, 'R2', annual_dict)


        

        # bring decision from ClassementYear
        decision = ag.decision
        obs_html = '<td>' + decision_to_html(decision) + '</td>'

        annual = ag.annual_session.annual.annual
        promo = ag.annual_session.promo
        cy = ClassementYear.query.filter_by(year = annual)\
            .join(Classement).filter_by(student_id=ag.student_id,
                promo_id=promo.id).first()
        if cy != None:
            if cy.decision != None and cy.decision != '':
                decision = cy.decision
                obs_html = '<td>decision de committee</br>' + decision_to_html(decision) + '</td>'

        
        

        bultin = '<td>' + bultin  + '</td>'

        # hide bultin if any session is historic
        if historic_exist == True:
            bultin = ''

        array_data.append([
            '<td class="center">' + str(index+1) + '</td>', 
            '<td class="username">' + student.username + '</td>', 
            '<td class="name">' + student.get_student_name() + '</td>', 

            '<td class="right '+cross_s1+' '+bg_s1+'">'  + link_avr_1+ '</td>', 
            '<td class="center '+cross_s1+' '+bg_s1+'">' + str(ag.cr_1) + '</td>', 
            '<td class="right '+cross_s2+' '+bg_s2+'">'  + link_avr_2 + '</td>', 
            '<td class="center '+cross_s2+' '+bg_s2+'">' + str(ag.cr_2) + '</td>', 

            '<td class="right '+cross_average+' '+bg_ann+'">'  + str(ag.average) + '</td>', 
            '<td class="center '+cross_average+' '+bg_ann+'">' + str(ag.credit) + '</td>', 

            '<td class="center">' + ratt + '</td>', 

            '<td class="right '+bg_s1_r+'">'  + link_avr_r_1 + '</td>', 
            '<td class="center '+bg_s1_r+'">' + str(ag.cr_r_1) + '</td>', 
            '<td class="right '+bg_s2_r+'">'  + link_avr_r_2 + '</td>', 
            '<td class="center '+bg_s2_r+'">' + str(ag.cr_r_2) + '</td>', 

            '<td class="right '+bg_ann_r+'">' + str(ag.average_r) + '</td>', 
            '<td class="center '+bg_ann_r+'">' + str(ag.credit_r) + '</td>', 

            '<td class="right '+bg_final+'">'  + str(ag.average_final) + '</td>', 
            '<td class="center '+bg_final+'">' + str(ag.credit_final) + '</td>',  
            obs_html,
            bultin
        ])

    return array_data

def collect_data_annual_session_print(annual_session, sort='', ratt=''):
    annual_dict = annual_session.get_annual_dict()
    student_ids = get_student_annual_list(annual_session, annual_dict)

    annual_grades = []
    if sort == 'desc':
        annual_grades = AnnualGrade.query.filter_by(annual_session_id=annual_session.id)\
            .order_by(AnnualGrade.average_final.desc()).all()
    else:
        annual_grades = AnnualGrade.query.filter_by(annual_session_id=annual_session.id).all()


    array_data = []
    for index, ag in enumerate(annual_grades):
        if ratt == 'ratt' and ag.enter_ratt == 0:
            continue

        username = ag.student.username
        name = ag.student.get_student_name()

        moyen1 = ag.avr_r_1 if ag.avr_r_1 != None else ag.avr_1
        credit1 = ag.cr_r_1 if ag.cr_r_1 != None else ag.cr_1
        session1 = '1' if ag.cr_r_1 == None else '2'

        moyen2 = ag.avr_r_2 if ag.avr_r_2 != None else ag.avr_2
        credit2 = ag.cr_r_2 if ag.cr_r_2 != None else ag.cr_2
        session2 = '1' if ag.cr_r_2 == None else '2'

        moyen_f = ag.average_final
        credit_f = ag.credit_final
        session_f = '1' if ag.cr_r_1 == None and ag.cr_r_2 == None else '2'

        decision = decision_to_observation(ag.decision)

        array_data.append([
            index+1, username, name,
            str(moyen1), str(credit1), str(session1), 
            str(moyen2), str(credit2), str(session2), 
            str(moyen_f), str(credit_f), str(session_f), 
            decision
        ])
    return array_data


def flash_check_annual_session(annual_dict_obj):
    S1 = annual_dict_obj['S1']
    S2 = annual_dict_obj['S2']
    R1 = annual_dict_obj['R1']
    R2 = annual_dict_obj['R2']
    need_init_recalc = False
    alert_reinit = 'alert-warning'
    alert_recalc = 'alert-warning'
    alert_errors = 'alert-danger'
    # 
    # 
    # 
    # 
    # 
    # 
    # 
    # check if there is some errors
    # 
    # 
    # 
    # 
    # 
    if S1 != None:
        nbr = str(annual_dict_obj['S1'].semester.get_nbr())
        if S1.is_config_changed():
            need_init_recalc = True
            btn = make_button_session_reinit(S1)
            flash("Semester ("+nbr+") init needed "+btn, alert_reinit)
        if S1.check_errors_exist():
            need_init_recalc = True
            flash("Semester ("+nbr+") has ERRORS ", alert_errors)
        else:
            if S1.check_recalculate_needed():
                need_init_recalc = True
                btn = make_button_session_recalc(S1)
                flash("Semester ("+nbr+") recalculate needed "+btn, alert_recalc)

    if S2 != None:
        nbr = str(annual_dict_obj['S2'].semester.get_nbr())
        if S2.is_config_changed():
            need_init_recalc = True
            btn = make_button_session_reinit(S2)
            flash("Semester ("+nbr+") init needed "+btn, alert_reinit)
        if S2.check_errors_exist():
            need_init_recalc = True
            flash("Semester ("+nbr+") has ERRORS ", alert_errors)
        else:
            if S2.check_recalculate_needed():
                need_init_recalc = True
                btn = make_button_session_recalc(S2)
                flash("Semester ("+nbr+") recalculate needed "+btn, alert_recalc)

    if R1 != None:
        nbr = str(annual_dict_obj['R1'].semester.get_nbr())
        if R1.is_config_changed():
            need_init_recalc = True
            btn = make_button_session_reinit(R1)
            flash("Ratt. ("+nbr+") init needed "+btn, alert_reinit)
        if R1.check_errors_exist():
            need_init_recalc = True
            flash("Ratt. ("+nbr+") has ERRORS ", alert_errors)
        else:
            if R1.check_recalculate_needed():
                need_init_recalc = True
                btn = make_button_session_recalc(R1)
                flash("Ratt. ("+nbr+") recalculate needed "+btn, alert_recalc)
    if R2 != None:
        nbr = str(annual_dict_obj['R2'].semester.get_nbr())
        if R2.is_config_changed():
            need_init_recalc = True
            btn = make_button_session_reinit(R2)
            flash("Ratt. ("+nbr+") init needed "+btn, alert_reinit)
        if R2.check_errors_exist():
            need_init_recalc = True
            flash("Ratt. ("+nbr+") has ERRORS ", alert_errors)
        else:
            if R2.check_recalculate_needed():
                need_init_recalc = True
                btn = make_button_session_recalc(R2)
                flash("Ratt. ("+nbr+") recalculate needed "+btn, alert_recalc)

    return need_init_recalc

def make_button_session_reinit(session):
    session_id = session.id
    annual_session_id = session.annual_session.id
    url_return = url_for('annual_session', annual_session_id=annual_session_id)
    reinit_url = url_for('reinitialize_session', session_id=session_id, url_return=url_return)
    slow_redirect_url = url_for('slow_redirect', url=reinit_url, message='(Re)initializing')
    btn = '<a id="re-init-"'+str(session_id)+' class="btn btn-warning"'
    btn += ' href="'+slow_redirect_url+'" >(Re)initialize</a>'
    return btn
   
def make_button_session_recalc(session):
    session_id = session.id
    annual_session_id = session.annual_session.id
    url_return = url_for('annual_session', annual_session_id=annual_session_id)
    recalc_url = url_for('calculate_session', session_id=session_id, url_return=url_return)
    slow_redirect_url = url_for('slow_redirect', url=recalc_url, message='(Re)recalculating')
    btn = '<a id="re-calc-"'+str(session_id)+' class="btn btn-warning"'
    btn += ' href="'+slow_redirect_url+'" >(Re)calculate</a>'
    return btn

def renegade_annual_session(annual_session_id):
    # if it doesn't have any sessions
    annual_session = AnnualSession.query.get_or_404(annual_session_id)
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

# if annual_session_id == None -> take from other session in the same Annual
# else -> init with the new one
def init_annual_session_id(session_id, annual_session_id=None):
    session = Session.query.get_or_404(session_id)
    chain = session.get_annual_chain()
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


@app.route('/annual-session/<annual_session_id>/refrech', methods=['GET', 'POST'])
def annual_session_refrech(annual_session_id=0):
    annual_session = AnnualSession.query.get_or_404(annual_session_id)

    init_annual_grade(annual_session)
    # fetch_data_annual_session(annual_session)
    # calculate_annual(annual_session)

    return redirect(url_for('annual_session', annual_session_id=annual_session_id))

@app.route('/annual-session/<annual_session_id>/calculate', methods=['GET', 'POST'])
def calculate_annual_session(annual_session_id=0):
    annual_session = AnnualSession.query.get_or_404(annual_session_id)
    init_annual_grade(annual_session)
    fetch_data_annual_session(annual_session)
    annual_session.calculate()
    db.session.commit()
    return redirect(url_for('annual_session', annual_session_id=annual_session_id))

@app.route('/annual-session/<session_id>/create-annual-session/', methods=['GET', 'POST'])
def create_annual_session(session_id):
    annual_session_id = None
    promo_id = None
    session = Session.query.get_or_404(session_id)
    chain = session.get_annual_chain()
    for ch in chain:
        session = Session.query.get(ch)
        if session.annual_session_id != None:
            annual_session_id = session.annual_session_id
            promo_id = session.promo_id
            break

    # check the existance of the record
    annual_session = AnnualSession.query.filter_by(id=annual_session_id).first()
    if annual_session_id != None and annual_session == None:
        raise Exception('the Annual Session:' + str(annual_session_id) + ' does not exist')

    if annual_session == None:
        annual = session.semester.annual
        promo_name = session.promo.name
        name = str(promo_name) + " - Annual " + str(annual.annual)
        annual_session = AnnualSession(name=name, promo_id=session.promo_id, annual_id=annual.id)
        db.session.add(annual_session)
        db.session.commit()
        annual_session_id = annual_session.id
    elif annual_session.annual_id == None:
        annual = session.semester.annual
        annual_session.annual_id = annual.id
        db.session.commit()

    init_annual_session_id(session.id, annual_session_id)

    return redirect(url_for('annual_session_refrech', annual_session_id=annual_session_id))





def annual_session_dlc(*args, **kwargs):
    annual_session_id = request.view_args['annual_session_id']
    annual_session = AnnualSession.query.get_or_404(annual_session_id)
    name = 'Annual ()'
    if annual_session.annual != None:
        name = 'Annual (' + str(annual_session.annual.annual) + ')'
    
    return [{'text': '' + name, 
        'url': url_for('annual_session', annual_session_id=annual_session_id) }]

@app.route('/annual-session/<annual_session_id>/<sort>/', methods=['GET', 'POST'])
@app.route('/annual-session/<annual_session_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_annual.annual', '***', dynamic_list_constructor=annual_session_dlc)
def annual_session(annual_session_id=0, sort=''):
    annual_session = AnnualSession.query.get_or_404(annual_session_id)

    # hide bultin if any session is historic
    historic_exist = False
    for session in annual_session.sessions:
        if session.is_historic == True:
            historic_exist = True
            break

    array_data = collect_data_annual_session(annual_session, sort, historic_exist)
    annual_dict_obj = annual_session.get_annual_dict_obj()
    check_ann = flash_check_annual_session(annual_dict_obj)

    students_consistant = annual_session.check_students_consistant_between_two_semesters()

    return render_template('session/annual-session.html', 
        title='Annual Session', annual_session=annual_session, 
        array_data=array_data, annual_dict_obj=annual_dict_obj, 
        check_ann=check_ann, historic_exist=historic_exist)

@app.route('/annual-session/<annual_session_id>/print/<ratt>', methods=['GET', 'POST'])
@app.route('/annual-session/<annual_session_id>/print/sort/<sort>/<ratt>', methods=['GET', 'POST'])
@app.route('/annual-session/<annual_session_id>/print/sort/<sort>/', methods=['GET', 'POST'])
@app.route('/annual-session/<annual_session_id>/print/', methods=['GET', 'POST'])
def annual_session_print(annual_session_id=0, sort='', ratt=''):
    annual_session = AnnualSession.query.get_or_404(annual_session_id)
    array_data = collect_data_annual_session_print(annual_session, sort, ratt)
    # return str(array_data)
    # array_data = [
    #     [5, 'SF-2018-05', 'LAOUAR Meriem', Decimal('11.43'), 22, '2', Decimal('10.62'), 28, '2',    '1', '2', '3', 'Admis avec dettes'], 
    #     [5, 'SF-2018-05', 'LAOUAR Meriem', Decimal('11.43'), 22, '2', Decimal('10.62'), 28, '2',    '1', '2', '3', 'Admis avec dettes'], 
    #     [5, 'SF-2018-05', 'LAOUAR Meriem', Decimal('11.43'), 22, '2', Decimal('10.62'), 28, '2',    '1', '2', '3', 'Admis avec dettes'], 
    #     [5, 'SF-2018-05', 'LAOUAR Meriem', Decimal('11.43'), 22, '2', Decimal('10.62'), 28, '2',    '1', '2', '3', 'Admis avec dettes'], 
    # ]

    header = make_header_annual_print(annual_session, 'Resultat Annuelle')
    annual_dict_obj = annual_session.get_annual_dict_obj()
    title = make_title_annual_print(annual_session, "Annuelle")
    return render_template('session/annual-session-print.html', title=title, 
        array_data=array_data, header=header, annual_dict_obj=annual_dict_obj)


@app.route('/annual-session/<annual_session_id>/delete/', methods=['GET', 'POST'])
def delete_annual_session(annual_session_id):
    # if it doesn't have any sessions
    count = renegade_annual_session(annual_session_id)

    annual_session = AnnualSession.query.get_or_404(annual_session_id)
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




####################################################################
#####                                                          #####
#####    ########  ##     ## ##      ######## #### ##    ##    #####
#####    ##     ## ##     ## ##         ##     ##  ###   ##    #####
#####    ##     ## ##     ## ##         ##     ##  ####  ##    #####
#####    ########  ##     ## ##         ##     ##  ## ## ##    #####
#####    ##     ## ##     ## ##         ##     ##  ##  ####    #####
#####    ##     ## ##     ## ##         ##     ##  ##   ###    #####
#####    ########   #######  ########   ##    #### ##    ##    #####
#####                                                          #####
####################################################################

def get_thead_bultin_semester():
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

def get_header_bultin_semester(student_session):
    student = student_session.student
    semester = student_session.session.semester
    sem = semester.get_nbr()

    annual_string = str(semester.annual.annual)
    annual_string += '<sup>ére</sup>' if semester.annual.annual == 1 else '<sup>ème</sup>'

    # header
    header = '<center><h2>Releve de Notes Semeste '+str(sem)+'</h2></center>'
    header += "Le directeur de <b>"+student.branch.school.name+",</b> atteste que l'étudiant(e)</br>"
    header += 'Nom: <b>'+student.last_name+'</b>     '
    header += 'Prenom: <b>'+student.first_name+'</b>    '
    header += 'Né(e) le: <b>'+str(student.birth_date).replace('None', '#é$/&?|[+{#%*#$=')+'</b>'
    header += ' à <b>'+str(student.birth_place).replace('None', '#é$/&?|[+{#%*#$=')+'</b></br>'
    header += 'Inscrit(e) en <b>' + str(annual_string) + ' année</b>   '
    header += 'Corps des: <b>'+student.branch.description+'</b></br>'
    header += 'Sous le matricule: <b>' + student.username + '</b>'
    header += "  a obtenu les résultats suivants durant l'année pédagogique: "
    header += "<b>"+student_session.session.get_annual_pedagogique()+"</b>"
    header += '</br></br>'

    return header

def get_footer_bultin_semester(student_session):
    # footer
    footer = '</br>'
    footer += 'Moyenne Semestrielle: <b>'+str(student_session.average)+'</b>    '
    footer += 'Crédits cumulés dans le Semeste: <b>'+str(student_session.credit)+'</b></br>'
    # footer += 'Décision de la commission de classement et '
    # footer += 'd''orientation:  <b>******</b></br></br>'
    footer += 'Ouargla le:  ..................'

    return footer


# EMPTY = '<font color="red"><b>X</b></font>'
def EMPTY(text):
    return '<font color="red"><b>' + text + '</b></font>'

def get_ratt_bultin(ratt):
    if ratt == True:
        return '2'
    return '1'

def get_bultin_semester(student_session):
    student = student_session.student
    semester = student_session.session.semester

    # Table
    grade_units = student_session.grade_units
    table = get_thead_bultin_semester()


    for grade_unit in grade_units:
        modules_in_unit = [module.id for module in grade_unit.unit.modules]
        grades_in_unit = Grade.query\
            .filter_by(student_session_id=student_session.id)\
            .filter(Grade.module_id.in_(modules_in_unit)).all()

        grades_tr = ''
        rowspan = 0

        for grade in grades_in_unit:
            module = grade.module
            if rowspan > 0:
                grades_tr += '<tr>'
            grades_tr += '<td>'+str(module.code).replace('None', EMPTY('#é$/&'))+'</td>'
            grades_tr += '<td class="intitule">'+module.display_name.replace(' ', ' ')+'</td>'
            grades_tr += '<td>'+str(module.credit)+'</td> <td>'+str(module.coefficient)+'</td>'
            grades_tr += '<td>'+str(grade.average).replace('None', EMPTY('X'))+'</td>'
            grades_tr += '<td>'+str(grade.credit).replace('None', EMPTY('X'))+'</td>'
            grades_tr += '<td>'+get_ratt_bultin(grade.check_is_rattrapage())+'</td>'
            if rowspan == 0:
                grades_tr += '<td rowspan=_rowspan_>'+str(grade_unit.average).replace('None', EMPTY('X'))+'</td>'
                grades_tr += '<td rowspan=_rowspan_>'+str(grade_unit.credit).replace('None', EMPTY('X'))+'</td>'
                grades_tr += '<td rowspan=_rowspan_>'+get_ratt_bultin(grade_unit.check_is_rattrapage())+'</td>'
            
            grades_tr += '</tr>'
            rowspan += 1

        unit = grade_unit.unit
        tr =  '<td rowspan='+str(rowspan)+'>'+unit.display_name+'</td>'
        tr += '<td rowspan='+str(rowspan)+'>'+str(unit.get_unit_cumul_credit())+'</td>'
        tr += '<td rowspan='+str(rowspan)+'>'+str(unit.unit_coefficient)+'</td>'
        tr += grades_tr.replace('_rowspan_', str(rowspan) )

        table += '<tr>' + tr + '</tr>'

    return table


@app.route('/session/<session_id>/student/<student_id>/bultin-print/', methods=['GET', 'POST'])
def bultin_semester_print(session_id, student_id):
    # return '1'
    student_session = StudentSession.query\
        .filter_by(session_id=session_id, student_id=student_id).first()
    bultin = get_bultin_semester(student_session)

    header = get_header_bultin_semester(student_session)
    footer = get_footer_bultin_semester(student_session)

    session = Session.query.get_or_404(session_id)
    student = student_session.student
    title = make_title_semester_print_by_student(session, student, 'Bultin - ')


    # print('------')
    # print('------')
    # print(str( student_session.get_last_grade_modification() ))
    # print('------')
    # print('------')


    # return table
    return render_template('student/bultin-semester-print.html', 
            title=title, bultin=bultin, header=header, footer=footer, 
            session_id=session_id, student_session=student_session)

@app.route('/session/<session_id>/bultin-print-all/', methods=['GET', 'POST'])
def bultin_semester_print_all(session_id):
    student_sessions = StudentSession.query\
        .filter_by(session_id=session_id).all()

    bultins = []
    for student_session in student_sessions:
        header = get_header_bultin_semester(student_session)
        bultin = '<table class="table table-bordered">'
        bultin += get_bultin_semester(student_session)
        bultin += '</table>'
        footer = get_footer_bultin_semester(student_session)

        bultins.append( header + bultin + footer )

    session = Session.query.get_or_404(session_id)
    # branch = session.promo.branch.name
    # semester = session.semester.get_nbr()
    # promo = session.promo.name
    # dt = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    # title = 'Bultin All - '+branch+' S'+str(semester) + ' ['+promo+'] ('+str(dt)+')'
    title = make_title_semester_print(session, 'Bultin All - ')

    return render_template('student/bultin-semester-print-all.html', 
            title=title, bultins=bultins, session_id=session_id)


# ----------------------
# ----------------------
# ----------------------

def get_thead_bultin_annual():
    header = '<tr class="head">'
    header += '<th class="rotate" rowspan=3><div>Semestre</div></th>'
    header += '<th colspan=3>Unité d''Enseignement</th>'
    header += '<th colspan=4>Matière d''Enseignement</th>'
    header += '<th colspan=9>Résultats obtenus</th>'
    header += '</tr>'
    header += '<tr class="head">'
    header += '<th rowspan=2>Nature</th>'
    header += '<th rowspan=2>Crédit</br>requis</th>'
    header += '<th rowspan=2>Coeff</th>'

    header += '<th rowspan=2>Code</th>'
    header += '<th rowspan=2>Intitulé</th>'
    header += '<th rowspan=2>Crédit</br>requis</th>'
    header += '<th rowspan=2>Coeff</th>'

    header += '<th colspan=3>Matière</th> <th colspan=3>U.E</th> <th colspan=3>Semestre</th>'
    header += '</tr>'
    header += '<tr class="head">'
    header += '<th>Moy</th> <th>Cr</th> <th>S</th>'
    header += '<th>Moy</th> <th>Cr</th> <th>S</th>'
    header += '<th>Moy</th> <th>Cr</th> <th>S</th>'
    header += '</tr>'

    return header

def get_semester_modules_html(student_session):
    semester = student_session.session.semester
    row_span_sem = semester.nbr_of_modules()

    sem_tr = '<tr>'
    sem_tr += '<td class="rotate" rowspan='+str(row_span_sem)+'><div>Semestre '+str(semester.get_nbr())+'</div></td>'

    # take considiration of Rattrapage
    sem_result = '<td rowspan='+str(row_span_sem)+'>'+str(student_session.average)+'</td>'
    sem_result += '<td rowspan='+str(row_span_sem)+'>'+str(student_session.credit)+'</td>'
    sem_result += '<td rowspan='+str(row_span_sem)+'>'+get_ratt_bultin(student_session.check_is_rattrapage()) +'</td>'

    grade_units = student_session.grade_units
    
    row_unit = 0

    for grade_unit in grade_units:
        modules_in_unit = [module.id for module in grade_unit.unit.modules]
        grades_in_unit = Grade.query\
            .filter_by(student_session_id=student_session.id)\
            .filter(Grade.module_id.in_(modules_in_unit)).all()
        
        unit = grade_unit.unit
        unit_tr = '<td rowspan=_unit-rowspan_>'+unit.display_name+'</td>'
        unit_tr += '<td rowspan=_unit-rowspan_>'+str(unit.get_unit_cumul_credit())+'</td>'
        unit_tr += '<td rowspan=_unit-rowspan_>'+str(unit.unit_coefficient)+'</td>'

        unit_result = '<td rowspan=_unit-rowspan_>'+str(grade_unit.average).replace('None', EMPTY('X'))+'</td>'
        unit_result += '<td rowspan=_unit-rowspan_>'+str(grade_unit.credit).replace('None', EMPTY('X'))+'</td>'
        unit_result += '<td rowspan=_unit-rowspan_>'+get_ratt_bultin(grade_unit.check_is_rattrapage())+'</td>'

        row_module = 0
        if row_module == 0:
            sem_tr += unit_tr

        for grade in grades_in_unit:
            module = grade.module
            grade_tr = '<td>'+str(module.code).replace('None', EMPTY('#é$/&'))+'</td>'
            grade_tr += '<td class="intitule">'+module.display_name.replace(' ', ' ')+'</td>'
            grade_tr += '<td>'+str(module.credit)+'</td> <td>'+str(module.coefficient)+'</td>'
            grade_tr += '<td>'+str(grade.average).replace('None', EMPTY('X'))+'</td>'
            grade_tr += '<td>'+str(grade.credit).replace('None', EMPTY('X'))+'</td>'
            grade_tr += '<td>'+get_ratt_bultin(grade.check_is_rattrapage())+'</td>'
            if row_module == 0:
                grade_tr += unit_result
            if row_unit == 0 and row_module == 0:
                grade_tr += sem_result
            
            sem_tr += grade_tr + '</tr>'
            row_module += 1

        sem_tr = sem_tr.replace( '_unit-rowspan_', str(row_module) )
        row_unit += 1
    
    return sem_tr

def get_active_student_sessions(annual_session_id, student_id):
    annual_session = AnnualSession.query\
        .filter_by(id=annual_session_id).first()

    # i have to remove the normal session when there is ratt
    annual_dict = annual_session.get_annual_dict()
    sessions = []

    s1 = r1 = s2 = r2 = None

    if annual_dict['S1'] != -1:
        s1 = StudentSession.query.filter_by(
            session_id=annual_dict['S1'], student_id=student_id).first()
    if annual_dict['R1'] != -1:
        r1 = StudentSession.query.filter_by(
            session_id=annual_dict['R1'], student_id=student_id).first()
    if annual_dict['S2'] != -1:
        s2 = StudentSession.query.filter_by(
            session_id=annual_dict['S2'], student_id=student_id).first()
    if annual_dict['R2'] != -1:
        r2 = StudentSession.query.filter_by(
            session_id=annual_dict['R2'], student_id=student_id).first()

    if s1 != None and r1 == None:
        sessions.append(s1)
    if s1 != None and r1 != None:
        sessions.append(r1)

    if s2 != None and r2 == None:
        sessions.append(s2)
    if s2 != None and r2 != None:
        sessions.append(r2)

    return sessions


def get_header_bultin_annual(annual_grade):
    student = annual_grade.student
    annual_pedagogique = annual_grade.annual_session.get_annual_pedagogique()
    annual_literal = annual_grade.annual_session.annual.get_string_literal()

    # header
    header = F"""
      <div class="container" style="display: flex;">
        <div style="flex-grow: 1; margin:0px; padding:0px;">
            <img src='/static/img/logo.png'>
        </div>
        <div style="flex-grow: 1; " align="center">
            <font size="">
            REPUBLIQUE ALGERIENNE DEMOCRATIQUE ET POPULAIRE</br>
            MINISTERE DE LA SANTE DE LA POPULATION ET DE LA REFORME HOSPITALIRE</br></br>
            <b>INSTITUT NATIONAL DE FORMATION SUPERIEUR PARAMEDICALE DE OUARGLA</br>
            DEPARTEMENT D’EVALUATION</br>
            </b></font>
            <font size="+3"><b>Releve de Notes</b></font>
        </div>
        <div style="flex-grow: 1; margin:0px; padding:0px;" align="right">
            <img src='/static/img/logo-empty.png'>
        </div>
      </div>
    """

    header += "Le directeur de <b>"+student.branch.school.name+",</b> atteste que l'étudiant(e)</br>"
    header += 'Nom:  <b>'+student.last_name+'</b>     '
    header += 'Prenom:  <b>'+student.first_name+'</b>    '
    header += 'Né(e) le: <b>'+str(student.birth_date).replace('None', '#é$/&?|[+{#%*#$=')+'</b>'
    header += ' à <b>'+str(student.birth_place).replace('None', '#é$/&?|[+{#%*#$=')+'</b></br>'
    header += 'Inscrit(e) en <b>' + annual_literal + '</b>   '
    header += 'Corps des:  <b>'+student.branch.description+'</b></br>'
    header += 'Sous le matricule: <b>' + student.username + '</b>'
    header += "  a obtenu les résultats suivants durant l'année pédagogique: <b>"+annual_pedagogique+"</b>"
    header += '</br>'

    return header

def get_footer_bultin_annual(annual_grade):
    # footer
    footer = '</br>'
    # you have to take average_r
    #    in case of Rattrapage

    footer += "Moyenne Annuelle: <b>"+str(annual_grade.average_final)+"</b>    "
    footer += "Crédits cumulés dans l'année: <b>"+str(annual_grade.annual_session.get_annual_pedagogique())+"</b>"
    footer += " et <b>"+str(annual_grade.credit_final)+"</b></br>"
    footer += "Décision de la commission de classement et "
    footer += "d'orientation:  <b>" + decision_to_observation(annual_grade.decision)
    footer += "</b>                                      Le Directeur de l’INFSPM</br>"
    footer += "Ouargla le: .................."
    return footer


def get_bultin_annual(annual_grade):
    student_sessions = get_active_student_sessions(annual_grade.annual_session_id, annual_grade.student_id)

    # Table
    bultin = get_thead_bultin_annual()

    for student_session in student_sessions:
        bultin += get_semester_modules_html(student_session)

    return bultin

@app.route('/annual-session/<annual_session_id>/student/<student_id>/bultin-print/', methods=['GET', 'POST'])
# @register_breadcrumb(app, '.tree_session.session.classement.bultin', 'Bultin')
def bultin_annual_print(annual_session_id, student_id):
    annual_grade = AnnualGrade.query.filter_by(annual_session_id=annual_session_id, student_id=student_id).first()
    # student = Student.query.get_or_404(student_id)

    header = get_header_bultin_annual(annual_grade)
    footer = get_footer_bultin_annual(annual_grade)

    bultin = get_bultin_annual(annual_grade)
    return render_template('student/bultin-annual-print.html',
        title='Bultin-Annual', table=bultin, header=header, footer=footer, 
        annual_session_id=annual_session_id, student_id=student_id)

@app.route('/annual-session/<annual_session_id>/bultin-print-all/', methods=['GET', 'POST'])
# @register_breadcrumb(app, '.tree_session.session.classement.bultin', 'Bultin')
def bultin_annual_print_all(annual_session_id):
    # annual_session = AnnualSession.query.get_or_404(annual_session_id)
    annual_grades = AnnualGrade.query.filter_by(annual_session_id=annual_session_id).all()
    
    bultins = []
    for annual_grade in annual_grades:
        header = get_header_bultin_annual(annual_grade)
        bultin = '<table class="table table-bordered">'
        bultin += get_bultin_annual(annual_grade)
        bultin += '</table>'
        footer = get_footer_bultin_annual(annual_grade)

        bultins.append( header + bultin + footer )

    return render_template('student/bultin-annual-print-all.html',
        title='Bultin-Annual', bultins=bultins, 
        annual_session_id=annual_session_id)




#########################################################################
#####                                                               #####
#####    ########  ########  ######  ##     ## ##       ########    #####
#####    ##     ## ##       ##    ## ##     ## ##          ##       #####
#####    ##     ## ##       ##       ##     ## ##          ##       #####
#####    ########  ######    ######  ##     ## ##          ##       #####
#####    ##   ##   ##             ## ##     ## ##          ##       #####
#####    ##    ##  ##       ##    ## ##     ## ##          ##       #####
#####    ##     ## ########  ######   #######  ########    ##       #####
#####                                                               #####
#########################################################################


@app.route('/session/<session_id>/averages/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_session.session.average', 'Averages')
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


# Note: the Data is taken from the Config String

def get_th_1(session, cols_per_module):
    conf_dict = literal_eval(session.configuration)
    header = '<th class="left">Unit</th>'
    for unit in conf_dict['units']:
        display_name = unit["display_name"]
        unit_coefficient = unit["unit_coefficient"]
        unit_name = F'{display_name} ({unit_coefficient})'
        colspan = cols_per_module
        for module in unit['modules']:
            colspan += cols_per_module
        header += F'<th class="unit center" colspan={colspan}>{unit_name}</th>'
    display_name = conf_dict["display_name"]
    return header + F'<th class="semester center" rowspan=4 colspan={cols_per_module}>{display_name}</th>'

URL_PRINT = False

def get_th_2(session, cols_per_module):
    conf_dict = literal_eval(session.configuration)
    header = '<th class="left">Module</th>'
    for unit in conf_dict['units']:
        for module in unit['modules']:
            module_name = module["code"] + ' ' + module["display_name"]
            url = url_for('grade', session_id=session.id, module_id=module['m_id'])
            link = F'<a style="text-decoration: none; color:#111;" href="{url}">{module_name}</a>'
            global URL_PRINT
            if URL_PRINT == False:
                link = module_name
            header += F'''
                <th style="word-wrap: break-word" colspan={cols_per_module}>
                    <font size="-1"><center>
                      {link}
                    </center></font>
                </th>'''
        name = 'Resultat de ' + unit["display_name"] 
        header += F'<th style="word-wrap: break-word" class="unit center" rowspan=3 colspan={cols_per_module}>{name}</th>'
    return header

def get_th_3(session, cols_per_module):
    conf_dict = literal_eval(session.configuration)
    header = '<th class="left">Required Credit</th>'
    for unit in conf_dict['units']:
        for module in unit['modules']:
            credit = module['credit']
            header += F'<th colspan={cols_per_module}><center>{credit}</center></th>'
    return header

def get_th_4(session, cols_per_module):
    conf_dict = literal_eval(session.configuration)
    header = '<th class="left">Coefficient</th>'
    for unit in conf_dict['units']:
        for module in unit['modules']:
            coeff = module['coeff']
            header += F'<th colspan={cols_per_module}><center>{coeff}</center></th>'
    return header

def get_cols_ths(index, label, class_name, cols_per_module):
    onclick = 'onclick="sortTable('+str(index)+')" '
    label_a = label['a']
    label_c = label['c']
    label_s = label['s']

    if cols_per_module < 1:
        cols_per_module = 1
    if cols_per_module > 3:
        cols_per_module = 3

    index_c = index + 1
    th = ''
    if cols_per_module == 1 or cols_per_module == 2 or cols_per_module == 3:
        th += F'<th {onclick} class="{class_name} center sorter no-wrap">{label_a}<img id="sort-{index}" class="sort-icon" ((img))></th>'
    if cols_per_module == 2 or cols_per_module == 3:
        if class_name == 'semester':
            th += F'<th onclick="sortTable({index_c})" class="{class_name} center sorter no-wrap">{label_c}<img id="sort-{index_c}" class="sort-icon" ((img))></th>'
        else:
            th += F'<th class="{class_name} center no-wrap">{label_c}</th>'
    if cols_per_module == 3:
        th += F'<th class="{class_name} center no-wrap">{label_s}</th>'
    return th

def get_th_5(session, cols_per_module):
    conf_dict = literal_eval(session.configuration)
    cls = 'class="module center sorter no-wrap"'

    # header =  '<th class="module">N°</th>'
    # header += '<th onclick="sortTable(1)" '+cls+'>Matricule<img id="sort-1" class="sort-icon" ((img))></th>'
    # header += '<th onclick="sortTable(2)" '+cls+'>Nom<img id="sort-2" class="sort-icon" ((img))></th>'
    
    header = F'''
        <th class="module">N°</th>
        <th onclick="sortTable(1, 'asc')" {cls}>Matricule<img id="sort-1" class="sort-icon" ((img))></th>'
        <th onclick="sortTable(2, 'asc')" {cls}>Nom<img id="sort-2" class="sort-icon" ((img))></th>
    '''

    label = {'a':'M', 'c':'C', 's':'S'}
    index = 3
    for unit in conf_dict['units']:
        for module in unit['modules']:
            header += get_cols_ths(index, label, 'module', cols_per_module)
            index += cols_per_module
        header += get_cols_ths(index, label, 'unit', cols_per_module)
        index += cols_per_module

    # semester
    header += get_cols_ths(index, label, 'semester', cols_per_module)
    return header

def get_thead(session, cols_per_module=2):
    th_1 = get_th_1(session, cols_per_module)
    th_2 = get_th_2(session, cols_per_module)
    th_3 = get_th_3(session, cols_per_module)
    th_4 = get_th_4(session, cols_per_module)
    th_5 = get_th_5(session, cols_per_module)

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
        s = 1
        if grade.check_is_rattrapage():
            s = 2
        row += F'<td class="center td">{s}</td>'
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
        s = 1
        if grade_unit.check_is_rattrapage():
            s = 2
        row += F'<td class="unit center td">{s}</td>'
    return row

def get_row_semester(student_session, cols_per_module=2):
    grade_units = student_session.grade_units
    row = ''
    for grade_unit in grade_units:
        row += get_row_unit(grade_unit, cols_per_module)

    yellow = ''
    if (student_session.credit < 30):
        yellow = 'yellow'

    
    row += F'<td class="semester right td {yellow}">{student_session.average}</td>'
    if cols_per_module >= 2:
        row += F'<td class="semester center td {yellow}">{student_session.credit}</td>'
    if cols_per_module == 3:
        s = 1
        if student_session.check_is_rattrapage():
            s = 2
        row += F'<td class="semester center td {yellow}">{s}</td>'
    return row


def collect_semester_result_data(session, cols_per_module=2):
    data_arr = []
    students_session = StudentSession.query.filter_by(session_id=session.id)\
        .join(Student).order_by(Student.username).all()

    for index, student_session in enumerate(students_session, start=1):
        student = student_session.student
        name = student.last_name + ' ' + student.first_name
        # name = name.replace(' ', ' ')
        _std = '<td class="center td">' + str(index) + '</td>'
        _std += '<td class="no-wrap td">' + student.username + '</td>'
        _std += '<td class="no-wrap td name">' + name + '</td>'
        row = _std + get_row_semester(student_session, cols_per_module)
        data_arr.append(row)

    return data_arr

def make_link_button(route, label, session_id, student_id, target='popup', size='', btn='btn-primary'):
    href = url_for(route, session_id=session_id, student_id=student_id)
    bultin = '<a style="margin-left:1px;margin-bottom:1px;" target="'+target+'" class="btn '+btn+' '+size+'" role="button" '
    bultin += ' href ="'+href+'" '
    if target == 'popup':
        bultin += ' onclick="window.open(`'+href+'`, `popup`, `width=max,height=max`); " '
    bultin += '>'+label+'</a>'
    return bultin

def collect_semester_result_data__plus_buttons(session, cols_per_module=2):
    data_arr = []
    students_session = StudentSession.query.filter_by(session_id=session.id)\
        .join(Student).order_by(Student.username).all()

    for index, student_session in enumerate(students_session, start=1):
        student = student_session.student

        btn_grades = '<td>'+ make_link_button(
            'grade', 
            'Notes', 
            session.id, 
            student.id, 
            '_target', 
            size='btn-xs',
            btn='btn-default') +'</td>'

        btn_bultin = '<td>'+ make_link_button(
            'bultin_semester_print', 'Bultin', 
            session.id, 
            student.id, 
            '_target', 
            size='btn-xs',
            btn='btn-success') +'</td>'
        btn_just = '<td>'+ make_link_button(
            'justification', 
            'Justification', 
            session.id, 
            student.id, 
            '_target', 
            size='btn-xs') +'</td>'

        name = student.last_name + ' ' + student.first_name
        # name = name.replace(' ', ' ')
        _std = '<td class="center td">' + str(index) + '</td>'
        _std += '<td class="no-wrap td">' + student.username + '</td>'
        _std += '<td class="no-wrap td">' + name + '</td>'
        row = _std + get_row_semester(student_session, cols_per_module)

        row += btn_grades
        row += btn_bultin
        row += btn_just
        data_arr.append(row)

    return data_arr

@app.route('/session/<session_id>/semester-result/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_session.session.result', 'Relevé Resultat')
def semester_result(session_id=0):
    session = Session.query.get_or_404(session_id)

    filter_word = request.args.get('filter_word', default='', type=str)
    sort = request.args.get('sort', default=0, type=int)
    order = request.args.get('order', default='desc', type=str)
    cols = request.args.get('cols', default=2, type=int)

    cols_per_module = 2
    if cols == 2 or cols == 3:
        cols_per_module = cols

    params = {
        'filter_word': filter_word, 
        'sort': sort, 
        'order': order, 
        'cols': cols,
        'URL': url_for('semester_result', session_id=session_id),
        'URL_PRINT': url_for('semester_result_print', session_id=session_id)
    }


    global URL_PRINT
    URL_PRINT = True

    t_head = get_thead(session, cols_per_module)
    data_arr = collect_semester_result_data__plus_buttons(session, cols_per_module)

    # 1 - change URL in browser
    # 2 - change href in print button
    

    return render_template('session/semester-result.html',
        title='Semester ' + str(session.semester.semester) + ' Result', 
        t_head=t_head, data_arr=data_arr, session=session, params=params)


def get_semester_result_print_header(session):
    school = session.promo.branch.school.description
    branch = session.promo.branch.description
    annual = session.semester.annual.get_string_literal()
    semester = session.get_name()
    promo = session.promo.name
    annual_pedagogique = session.get_annual_pedagogique()

    header = F"""
      <div class="container" style="display: flex;">
        <div style="flex-grow: 1;">
            {school}<br/>
            Sous Direction des Affaires Pèdagogiques<br/>
            Département d'evaluation
        </div>
        <div style="flex-grow: 1;" align="center">
            Promo {promo}<br/>
            Année {annual_pedagogique}<br/>
            <b><font size="+2">Relevé {semester}</font></b>
        </div>
        <div style="flex-grow: 1;" align="right">
            {annual}<br/>
            {branch}
        </div>
      </div>
    """
    return header

@app.route('/session/<session_id>/semester-result-print/', methods=['GET'])
def semester_result_print(session_id=0):
    session = Session.query.filter_by(id=session_id).first_or_404()

    filter_word = request.args.get('filter_word', default='', type=str)
    sort = request.args.get('sort', default=0, type=int)
    order = request.args.get('order', default='desc', type=str)
    cols = request.args.get('cols', default=2, type=int)

    cols_per_module = 2
    if cols == 2 or cols == 3:
        cols_per_module = cols

    params = {
        'filter_word': filter_word, 
        'sort': sort, 
        'order': order, 
        'cols': cols, 
        'URL': url_for('semester_result', session_id=session_id),
        'URL_PRINT': url_for('semester_result_print', session_id=session_id)
    }

    global URL_PRINT
    URL_PRINT = False

    t_head = get_thead(session, cols_per_module)
    data_arr = collect_semester_result_data(session, cols_per_module)

    header = get_semester_result_print_header(session)
    title = make_title_semester_print(session, 'Releve')

    return render_template('session/semester-result-print.html',
        title=title, header=header, t_head=t_head, data_arr=data_arr, 
        session=session, params=params)


#######################################
#####                             #####
#####             PDF             #####
#####                             #####
#######################################

# @app.route('/page-break/', methods=['GET'])
# def page_break():
#     return render_template('page-break.html')


# from flask_weasyprint import HTML, render_pdf

# @app.route('/pdf/weasyprint/')
# def your_view_weasyprint():
#     return '12'
#     # html = render_template('http://localhost:5000/session/2/semester-result-print/')
#     # return render_pdf(HTML(string=html))


# Flask-WeasyPrint
# https://pythonhosted.org/Flask-WeasyPrint/
# http://weasyprint.readthedocs.io/en/latest/install.html



# import pdfkit
# from flask import send_file, send_from_directory
# from flask import Response

'''
be carefull returning the file in the right version
it looks like if i change the file it keeps returning the old one
it seems to work right when changing the URL
''' 
# @app.route('/pdf/session/<session_id>/nbr/<id>/')
# def print_semester_result(session_id=0, id=0):
#     # options = {'orientation': 'landscape', 'page-size':'A4', 'dpi':400}
#     options = {'orientation': 'landscape', 
#         'page-size':'A4', 
#         'encoding':'utf-8', 'dpi':400
#         # 'margin-top':'0.5cm',
#         # 'margin-bottom':'0.8cm',
#         # 'margin-left':'0.5cm',
#         # 'margin-right':'0.2cm'

#     }

#     # url = 'http://localhost:5001/session/1/semester-result-print/'+str(id)+'/'

#     url = url_for('semester_result_print', session_id=session_id, _external=True)
#     pdf_file_name = 'semester_zerbia.pdf'
#     return html_to_pdf(url, pdf_file_name, options)




# @app.route('/pdf/session/<session_id>/student/<student_id>/bultin-print/')
# def print_semester_bultin(session_id, student_id):
#     options = {'orientation': 'landscape', 
#         'page-size':'A4', 
#     }

#     url = url_for('bultin_semester_print', session_id=session_id, student_id=student_id, _external=True)
#     pdf_file_name = 'semester_bultin.pdf'
#     return html_to_pdf(url, pdf_file_name, options)


# @app.route('/session/<session_id>/module/<module_id>/students-print/empty/<empty>')
# @app.route('/session/<session_id>/module/<module_id>/students-print/')
# def print_module_students_empty(session_id=0, module_id=0, empty='no'):
#     url = url_for('module_print', session_id=session_id, 
#         module_id=module_id, _external=True)
#     if empty == 'yes':
#         url = url_for('module_print', session_id=session_id, 
#             module_id=module_id, _external=True, empty='yes')

#     pdf_file_name = 'module_students_print.pdf'
#     return html_to_pdf(url, pdf_file_name)


# @app.route('/print-page-break/')
# def print_page_break():
#     url = 'http://localhost:5000/page-break/'
#     pdf_file_name = 'page-break.pdf'
#     return html_to_pdf(url, pdf_file_name)


# @app.route('/print-test/')
# def print_test():
#     url = 'https://www.w3schools.com/colors/colors_picker.asp'
#     pdf_file_name = 'azerty.pdf'
#     return html_to_pdf(url, pdf_file_name)

# def html_to_pdf(url, pdf_file_name, options={}):
#     wkhtmltopdf_path = app.config['WKHTMLTOPDF_PATH']
#     config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
#     pdf = pdfkit.from_url(url, 'app\\pdf\\'+pdf_file_name, configuration=config, options=options)
#     return send_from_directory('pdf', pdf_file_name)



#
#
#  
#
