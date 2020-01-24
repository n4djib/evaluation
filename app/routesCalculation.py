from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.models import Session, StudentSession, AnnualGrade, Grade, GradeUnit, Semester, Type, Module
import copy
from ast import literal_eval
from flask_breadcrumbs import register_breadcrumb
# from app.routesSession import fetch_data_annual_grade    circular import
# from app.routesSession import init_student_annual_grade




def update_session_configuraton(session):
    if session != None:
        session.configuration = str( session.semester.config_dict() )
        
        # update parallel Config
        parallel_session = session.get_parallel_session()
        if parallel_session != None:
            parallel_session.configuration = str( parallel_session.semester.config_dict() )

        db.session.commit() 

def init_session(session):
    update_session_configuraton(session)
    for student_session in session.student_sessions:
        student_session.average = None if student_session.average == 0 else student_session.average
        student_session.credit = None if student_session.credit == 0 else student_session.credit
    db.session.commit()
    return 'init session'
    

def init_grade_unit(session):
    # delete all record and fill again
    units = session.semester.units
    students_session = StudentSession.query.filter_by(session_id=session.id).all()

    for student_session in students_session:
        grade_units = student_session.grade_units
        for grade_unit in grade_units:
            db.session.delete(grade_unit)
    db.session.commit()

    # delete if Historic
    if session.is_historic:
        return "init can't be done when Historic"

    for student_session in students_session:
        for unit in units:
            grade_unit = GradeUnit(student_session_id=student_session.id, unit_id=unit.id)
            grade_unit.unit_coefficient = unit.unit_coefficient
            grade_unit.is_fondamental = unit.is_fondamental
            db.session.add(grade_unit)
    db.session.commit()

    return 'init grade unit'

def init_grade(session):
    students_session = StudentSession.query.filter_by(session_id=session.id).all()
    # clone grades temporarily 
    # remove from database
    # insert with order
    copied_grades = []
    for student_session in students_session:
        grades = student_session.grades
        for grade in grades:
            copied_grades.append( copy.copy(grade) )
            db.session.delete(grade)
    db.session.commit()

    # delete if Historic
    if session.is_historic:
        return "init can't be done when Historic"

    for student_session in students_session:
        units = session.semester.units
        for unit in units:
            modules = unit.modules
            for module in modules:
                copied_grade = get_copied_grade(copied_grades, student_session.id, module.id)
                grade = Grade(student_session_id=student_session.id, module_id=module.id)
                if copied_grade != None:
                    grade.cour   = copied_grade.cour
                    grade.td     = copied_grade.td
                    grade.tp     = copied_grade.tp
                    grade.t_pers = copied_grade.t_pers
                    grade.stage  = copied_grade.stage

                    grade.is_rattrapage = copied_grade.is_rattrapage
                    # dirty is set in calculate grade
                    # grade.is_dirty = copied_grade.is_dirty
                    grade.is_dirty = True
                    grade.calculation = copied_grade.calculation

                grade.formula = get_formula(module.id)
                ## if i am going to use order then there is no need to delete grades
                # grade.order = module.order

                # grade.calculate()
                db.session.add(grade)

    db.session.commit()

    return 'init grade '

def init_module_session(session):
    units = session.semester.units
    for unit in units:
        modules = unit.modules
        for module in modules:
            app.routesGrade.create_module_session(session, module)
    return 'init module session '

def get_copied_grade(copied_grades, student_session_id, module_id):
    for copied_grade in copied_grades:
        if copied_grade.student_session_id == student_session_id and copied_grade.module_id == module_id:
            return copied_grade
    return None


# this should generate the formula from "Config String"
# not from the Tables directly
# but for now it is the same as "Config String
# because they are generated at the same time
def get_formula(module_id):
    module = Module.query.filter_by(id=module_id).first()

    formula = ""
    for percentage in module.percentages:
        type = Type.query.filter_by(id=percentage.type_id).first()
        formula += "'"+type.grade_table_field + "': " + str(percentage.percentage) + ", "

    coefficient = "'coefficient': " + str(module.coefficient) + ", "
    credit = "'credit': " + str(module.credit) + ", "

    # ratt = 'cour'
    # if :
    ratt = module.get_rattrapable_field()
    rattrapable = "'rattrapable': '" + ratt + "'"

    return "{" + formula + coefficient + credit + rattrapable + "}"

def init_all(session):
    message1 = init_session(session)
    message2 = init_grade_unit(session)
    message3 = init_grade(session)
    message4 = init_module_session(session)
    return F'init all : {message1} - {message2} - {message3}'




def calculate_student(session, student):
    # ss = StudentSession.query.filter_by(session_id=session.id, student_id=student.id).first()
    # # return str(len(ss))

    # return 'StudentSession ' + str(ss.id)
    # return 'session ' + str(session.id) + ' student ' + str(student .id)

    grades = Grade.query.join(StudentSession)\
        .filter_by(session_id=session.id, student_id=student.id).all()

    for grade in grades:
        grade.calculate()
    db.session.commit()

    grade_units = GradeUnit.query.join(StudentSession)\
        .filter_by(session_id=session.id, student_id=student.id).all()
    for grade_unit in grade_units:
        grade_unit.calculate()
    db.session.commit()

    # get only first
    ss = None
    students_session = StudentSession.query\
        .filter_by(session_id=session.id, student_id=student.id).all()
    for student_session in students_session:
        ss = student_session
        student_session.calculate()
        db.session.commit()

    if ss != None:
        calc = 'Ce Semestre (Moy: '+str(ss.average)+' - Cr: '+str(ss.credit)+')'

        if student_session.session.semester.has_fondamental():
            calc += ' (f: '+str( ss.units_fond_aquired() )+')'

        annual_session =  ss.session.annual_session
        if annual_session != None:
            ag = AnnualGrade.query\
                .filter_by(annual_session_id=annual_session.id, student_id=student.id)\
                .first()

            if ag == None:
                ag = app.routesSession.init_student_annual_grade(
                    annual_session, student.id)
                # print(str(ag.id))
                # print()
                db.session.commit()

            print()
            print(ag.id)
            print()

            # i have to fetch the data first
            ag.fetch_data()
            db.session.commit()

            # calculate
            ag.calculate()
            db.session.commit()

            calc += '</br>'

            annual = annual_session.annual.annual
            first_sem = annual*2 - 1
            second_sem = first_sem + 1

            if ag.avr_1 is not None:
                calc += 'S{} (Moy: {} - Cr: {}) -- '.format(first_sem, ag.avr_1, ag.cr_1)
            if ag.avr_r_1 is not None:
                calc += 'R{} (Moy: {} - Cr: {}) -- '.format(first_sem, ag.avr_r_1, ag.cr_r_1)
            if ag.avr_2 is not None:
                calc += 'S{} (Moy: {} - Cr: {}) -- '.format(second_sem, ag.avr_2, ag.cr_2)
            if ag.avr_r_2 is not None:
                calc += 'R{} (Moy: {} - Cr: {}) -- '.format(second_sem, ag.avr_r_2, ag.cr_r_2)
            calc = calc[:-4]
            calc = calc.replace('None', '')

            calc += '</br>'

            if session.is_rattrapage:
                calc += 'Annual avant Ratt. (Moy: '+str(ag.average)+' - Cr: ' + str(ag.credit)+')  -  '

            calc += 'Annual Final (Moy: '+str(ag.average_final)+' - Cr: ' + str(ag.credit_final)+')'

        return calc
    return 'calculate_student grades'

@app.route('/session/<session_id>/reinitialize-session/', methods=['GET', 'POST'])
def reinitialize_session(session_id=0):
    session = Session.query.get_or_404(session_id)
    url_return = request.args.get('url_return', default='', type=str)
    message = init_all(session)
    message += "</br>" + session.calculate()
    #
    #
    #
    #
    #
    #
    # db.session.commit()
    #
    #
    #
    #
    #
    #
    flash(message)
    if url_return != '':
        return redirect(url_return)
    return redirect(url_for('session', session_id=session_id))

@app.route('/session/<session_id>/calculate-session/', methods=['GET', 'POST'])
def calculate_session(session_id):
    session = Session.query.get_or_404(session_id)
    url_return = request.args.get('url_return', default='', type=str)
    message = session.calculate()
    flash(message)
    if url_return != '':
        return redirect(url_return)
    return redirect(url_for('session', session_id=session_id))


#
#
#

def get_module_name(module_id, conf_dict):
    for unit in conf_dict['units']:
        for module in unit['modules']:
            if module['m_id'] == module_id:
                return module['display_name']
    return '** get_module_name **'

def rename_type(calculation):
    types = Type.query.all()
    for type in types:
        calculation = calculation.replace(type.grade_table_field, type.type)
    return calculation


def get_module_justification(grade, conf_dict):
    name = get_module_name(grade.module_id, conf_dict)
    # module = name + '  →  ' + grade.calculation
    return [name] + [rename_type(grade.calculation)] + [grade.average] + [grade.credit]

def get_unit_name(unit_id, conf_dict):
    for unit in conf_dict['units']:
        if unit['u_id'] == unit_id:
            return unit['display_name']
    return '** get_unit_name **'

def get_unit_justification(grade_unit, conf_dict):
    name = get_unit_name(grade_unit.unit_id, conf_dict)
    justification = ['    <b>UNIT</b> : ' + name]
    if grade_unit.calculation != None and grade_unit.calculation != '':
        # justification += ['    ' + grade_unit.calculation]
        justification += [grade_unit.calculation]
    else:
        justification += '**********'

    justification += [grade_unit.average]
    justification += [grade_unit.credit]
    return justification

def get_semester_justification(student_session, conf_dict):
    name = student_session.session.semester.display_name
    semester = ['        <b>SEMESTER</b> : ' + name]
    semester += ['    ' + str(student_session.calculation)]
    semester += [str(student_session.average)]
    semester += [str(student_session.credit)]
    return  semester

@app.route('/session/<session_id>/justification/<student_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_session.session.classement.justification', 'Justification')
def justification(session_id, student_id):
    student_session = StudentSession.query.filter_by(session_id=session_id, student_id=student_id).first()
    grade_units = student_session.grade_units
    grades = student_session.grades
    session = student_session.session
    conf_dict = literal_eval( session.configuration )

    std = student_session.student
    name = std.username+' - '+std.last_name + ' ' + std.first_name
    sem_nbr = str(session.semester.get_nbr())
    type = 'Rattrapage' if session.is_rattrapage == True else 'Semestre'
    semester = type + ' ('+sem_nbr+')'
    header = '<h2><center>Justificatiion de calcule </center></h2>'
    header += '<h3><center>'+semester+'</center></h3>'
    header += 'Nom: '+name+ ''

    justs = []
    for grade_unit in grade_units:
        for grade in grades:
            if grade_unit.unit_id == grade.module.unit_id:
                justs.append( get_module_justification(grade, conf_dict) )
        justs.append( get_unit_justification(grade_unit, conf_dict) )
    justs.append( get_semester_justification(student_session, conf_dict) )
    return render_template('session/justification-print.html',
         title='Session', justs=justs, header=header)

# @app.route('/session/<session_id>/justification/username/<username>/', methods=['GET', 'POST'])
# # @register_breadcrumb(app, '.tree_session.session.classement.justification', 'Justification')
# def justification_by_username(session_id, username):
#     student_session = StudentSession.query.filter_by(session_id=session_id)\
#         .join(student).filter_by(username=username).first()
#     grade_units = student_session.grade_units
#     grades = student_session.grades
#     session = student_session.session
#     conf_dict = literal_eval( session.configuration )

#     justs = []
#     for grade_unit in grade_units:
#         for grade in grades:
#             if grade_unit.unit_id == grade.module.unit_id:
#                 justs.append( get_module_justification(grade, conf_dict) )
#         justs.append( get_unit_justification(grade_unit, conf_dict) )
#     justs.append( get_semester_justification(student_session, conf_dict) )
#     return render_template('session/justification-print.html', title='Session', justs=justs)
    
import app.routesSession
import app.routesGrade
