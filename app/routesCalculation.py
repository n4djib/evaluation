from app import app, db
from flask import render_template, redirect, url_for, flash
from app.models import Session, StudentSession, Grade, GradeUnit, Semester, Type, Module
# from decimal import *
import copy
from ast import literal_eval
from flask_breadcrumbs import register_breadcrumb



def config_to_dict(semester_id):
    semester = Semester.query.filter_by(id=semester_id).first()
    if semester == None:
        return F'Semester with id: {semester_id} Not Found'
    dict_semester = semester.config_dict()
    return dict_semester

def init_session(session):
    conf_dict = config_to_dict(session.semester_id)
    session.configuration = str(conf_dict)
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

    for student_session in students_session:
        for unit in units:
            grade_unit = GradeUnit(student_session_id=student_session.id, unit_id=unit.id)
            grade_unit.unit_coefficient = unit.unit_coefficient
            grade_unit.is_fondamental = unit.is_fondamental
            # grade_unit.order = unit.order
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

                    grade.is_rattrapage  = copied_grade.is_rattrapage

                grade.formula = get_formula(module.id)
                ## if i am going to use order then there is no need to delete grades
                # grade.order = module.order

                # calculate_grade(grade)
                grade.calculate()
                db.session.add(grade)
    db.session.commit()

    return 'init grade '

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
    credit = "'credit': " + str(module.credit)
    return "{" + formula + coefficient + credit + "}"

def init_all(session_id):
    session = Session.query.filter_by(id=session_id).first()
    message1 = init_session(session)
    message2 = init_grade_unit(session)
    message3 = ''
    message3 = init_grade(session)
    
    # message3 = 'init_grade(session)'
    return F'init all : {message1} - {message2} - {message3}'

@app.route('/session/<session_id>/reinitialize-session/', methods=['GET', 'POST'])
def reinitialize_session(session_id=0):
    message = init_all(session_id)
    flash(message)
    return redirect(url_for('session', session_id=session_id))


@app.route('/session/<session_id>/calculate-all/', methods=['GET', 'POST'])
def calculate_all(session_id):
    message = 'calculate_all'
    message = init_all(session_id)
    flash(message)

    # # it would be better if:
    # #   i don't save the grades
    # #   butt send them to grade_unit.calculate
    # #   this way i would not have to visit the database multiple times

    # grades = Grade.query.join(StudentSession).filter_by(session_id=session_id).all()
    # for grade in grades:
    #     grade.calculate()
    # db.session.commit()
    # # commit should be removed
    # # for more speed make a list of tuples (module_id, unit_id)
    # #   select it directly from Config (config string)
    # #   and use it in the next loop rather than (grade.module.unit_id)

    grade_units = GradeUnit.query.join(StudentSession).filter_by(session_id=session_id).all()
    for grade_unit in grade_units:
        grade_unit.calculate()
        # grades_in_unit = []
        # for grade in grades:
        #     if grade.module.unit_id == grade_unit.unit_id:
        #         grades_in_unit.append(grade)
        # grade_unit.calculate(grades_in_unit)
        # # grade_unit.calculate(<grades> of this grade_unit)
    db.session.commit()

    students_session = StudentSession.query.filter_by(session_id=session_id).all()
    for student_session in students_session:
        student_session.calculate()
        # student_session.calculate(<grade_units> of this student_session)
    db.session.commit()

    # db.session.query().filter(StudentSession.session_id == session_id).update({"avrage": (10)})
    # db.session.commit()

    # flash('calculated')
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
        justification += ['    ' + grade_unit.calculation]
    else:
        justification += '**********'

    justification += [grade_unit.average]
    justification += [grade_unit.credit]
    return justification

# def get_semester_name(student_session, conf_dict):
#     # for unit in conf_dict['units']:
#     #     if unit['u_id'] == unit_id:
#     #         return unit['display_name']
#     return student_session.session.semester.display_name
#     return '** get_semester_name **'

def get_semester_justification(student_session, conf_dict):
    name = student_session.session.semester.display_name
    semester = ['        <b>SEMESTER</b> : ' + name]
    semester += ['    ' + str(student_session.calculation)]
    semester += [str(student_session.average)]
    semester += [str(student_session.credit)]
    return  semester

@app.route('/session/<session_id>/justification/<student_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.classement.justification', 'Justification')
def justification(session_id, student_id):
    student_session = StudentSession.query.filter_by(session_id=session_id, student_id=student_id).first()    
    grade_units = student_session.grade_units
    grades = student_session.grades
    session = student_session.session
    conf_dict = literal_eval( session.configuration )

    justs = []
    for grade_unit in grade_units:
        for grade in grades:
            if grade_unit.unit_id == grade.module.unit_id:
                justs.append( get_module_justification(grade, conf_dict) )
        justs.append( get_unit_justification(grade_unit, conf_dict) )
    justs.append( get_semester_justification(student_session, conf_dict) )
    return render_template('session/justification.html', title='Session', justs=justs)

@app.route('/session/<session_id>/classement/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.classement', 'Classement')
def classement(session_id):
    students_session = StudentSession.query\
        .filter_by(session_id=session_id)\
        .order_by(StudentSession.average.desc()).all()
    return render_template('session/classement.html', title='Session', session_id=session_id, students_session=students_session)
