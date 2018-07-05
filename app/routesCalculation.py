from app import app, db
from flask import render_template, request, jsonify, redirect, url_for, flash
from app.models import Session, StudentSession, Grade, GradeUnit, Unit, Semester, Type, Module
from decimal import *
import copy
from ast import literal_eval


def init_session(session):
    conf_dict = config_to_dict(session.semester.id)
    # if session.configuration == str(conf_dict):
    #     return 'config not changed'
    #     # no need to init units
    # else:
    session.configuration = str(conf_dict)
    db.session.commit()
    return 'init session'

def init_grade_unit(session):
    # delete all record and fill again
    units = session.semester.units
    students_session = StudentSession.query.filter_by(session_id=session.id).all()

    for student_session in students_session:
        grades_unit = student_session.grades_unit
        for grade_unit in grades_unit:
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

                grade.formula = get_formula(module.id)
                ## if i am going to use order then there is no need to delete grades
                # grade.order = module.order
                calculate_grade(grade)
                db.session.add(grade)
    db.session.commit()

    return 'init grade '

def get_copied_grade(copied_grades, student_session_id, module_id):
    for copied_grade in copied_grades:
        if copied_grade.student_session_id == student_session_id and copied_grade.module_id == module_id:
            return copied_grade
    return None

def get_formula(module_id):
    module = Module.query.filter_by(id=module_id).first()

    formula = ""
    for percentage in module.percentages:
        type = Type.query.filter_by(id=percentage.type_id).first()
        formula += "'"+type.grade_table_field + "':" + str(percentage.percentage) + ", "

    coefficient = "'coefficient': " + str(module.coefficient) + ", "
    credit = "'credit': " + str(module.credit)
    return "{" + formula + coefficient + credit + "}"

def init_all(session_id):
    session = Session.query.filter_by(id=session_id).first()
    message1 = init_session(session)
    message2 = init_grade_unit(session)
    message3 = init_grade(session)
    return 'init all : ' + message1 + ' - ' + message2 + ' - ' + message3

@app.route('/session/<session_id>/reinitialize-session/', methods=['GET', 'POST'])
def reinitialize_session(session_id=0):
    message = init_all(session_id)
    flash(message)
    return redirect(url_for('session', session_id=session_id))


def dict_percentage(percentage):
    type = Type.query.filter_by(id=percentage.type_id).first()
    return {'type': type.type, 'per': str(percentage.percentage)} 

def dict_module(module):
    modules = {'m_id': module.id, 'name': module.name, 'display_name': module.display_name, 'coeff': module.coefficient, 'credit': module.credit}
    for percentage in module.percentages:
        modules.setdefault('percentages', []).append(dict_percentage(percentage))
    return modules

def dict_unit(unit):
    units = {'u_id': unit.id, 'name': unit.name, 'display_name': unit.display_name, 'coeff': unit.unit_coefficient, 'is_fondamental': unit.is_fondamental, 
        'unit_coeff': unit.get_unit_cumul_coeff(), 'unit_credit': unit.get_unit_cumul_credit() }
    for module in unit.modules:
        units.setdefault('modules', []).append(dict_module(module))
    return units

def dict_semester(semester):
    semesters = {'s_id': semester.id, 'name': semester.name, 'display_name': semester.display_name}
    for unit in semester.units:
        semesters.setdefault('units', []).append(dict_unit(unit))
    return semesters

def config_to_dict(semester_id):
    semester = Semester.query.filter_by(id=semester_id).first()
    if semester == None:
        return 'Semester with id: ' + semester_id + ' Not Found'
    
    dict_sem = dict_semester(semester)
    # return jsonify(dict_sem)
    return dict_sem
    # import json
    # with open('/your/path/to/a/dict/dump.txt') as handle:
    #     dictdump = json.loads(handle.read())

    # You can create the Python dictionary and serialize it
    # to JSON in one line and it's not even ugly.
    # my_json_string = json.dumps({'key1': val1, 'key2': val2})


def calculate_semester(student_session):
    grades_unit = student_session.grades_unit
    cumul_semester_coeff = student_session.session.semester.get_semester_cumul_coeff()
    cumul_semester_credit = student_session.session.semester.get_semester_cumul_credit()

    fondamental_unit_average = 0
    unit_fondamental_id = None

    average = 0
    credit = 0
    for grade_unit in grades_unit:
        if grade_unit.is_fondamental == True:
            fondamental_unit_credit = grade_unit.credit
            unit_fondamental_id = grade_unit.unit_id
        if grade_unit.average == None:
            average = None
            break

        unit = Unit.query.filter_by(id=grade_unit.unit_id).first()
        average += grade_unit.average * unit.unit_coefficient / cumul_semester_coeff
        credit += grade_unit.credit

    student_session.average = average
    if average == None:
        student_session.credit = None
    else:
        student_session.average = round(average, 2)
        unit_fondamental = Unit.query.filter_by(id=unit_fondamental_id).first()
        if average >= 10 and fondamental_unit_credit == unit_fondamental.get_unit_cumul_credit():
            credit = cumul_semester_credit
        
        student_session.credit = credit
    return 'calculated semester'

def calculate_unit(grade_unit):
    # grades in a unit
    grades = Grade.query.filter_by(student_session_id=grade_unit.student_session_id)\
        .join(Module).filter_by(unit_id=grade_unit.unit_id).all()
    cumul_unit_coeff = grade_unit.unit.get_unit_cumul_coeff()
    cumul_unit_credit = grade_unit.unit.get_unit_cumul_credit()

    average = 0
    credit = 0
    for grade in grades:
        if grade.average == None:
            average = None
            break
        average += grade.average * grade.module.coefficient / cumul_unit_coeff
        credit += grade.credit

    grade_unit.average = average
    if average == None:
        grade_unit.credit = None
    else:
        grade_unit.average = round(average, 2)
        if grade_unit.average >= 10 and grade_unit.is_fondamental == False:
            grade_unit.credit = cumul_unit_credit
        else:
            grade_unit.credit = credit
    return 'unit calculated'

def calculate_grade(grade):
    formula = grade.formula
    dictionary = eval(formula)

    grade.average = 0
    for field in dictionary:
        if field in ['cour', 'td', 'tp', 't_pers', 'stage']:
            val = getattr(grade, field)
            percentage = dictionary[field]
            if val == None:
                grade.average = None
                break

            getcontext().prec = 4
            percentage = Decimal(percentage)
            grade.average += round( val * percentage , 2)

    grade.credit = None
    if grade.average != None:
        if grade.average >= 10:
            grade.credit = dictionary['credit']
        else:
            grade.credit = 0

    return 'calculated'

@app.route('/session/<session_id>/calculate-all/', methods=['GET', 'POST'])
def grade_calculate_all(session_id):
    message = init_all(session_id)
    flash(message)

    grades = Grade.query.join(StudentSession).filter_by(session_id=session_id).all()
    for grade in grades:
        calculate_grade(grade)
    db.session.commit()

    grades_unit = GradeUnit.query.join(StudentSession).filter_by(session_id=session_id).all()
    for grade_unit in grades_unit:
        calculate_unit(grade_unit)
    db.session.commit()

    students_session = StudentSession.query.filter_by(session_id=session_id).all()
    for student_session in students_session:
        calculate_semester(student_session)
    db.session.commit()

    flash('calculated')
    return redirect(url_for('session', session_id=session_id))

#
#
#

@app.route('/session/<session_id>/classement-justification/', methods=['GET', 'POST'])
def classement_justification(session_id):
    students_session = StudentSession.query.filter_by(session_id=session_id).all()
    return render_template('session/classement-justification.html', title='Session', students_session=students_session)


def get_module_justification(grade, configuration):
    conf_dict = literal_eval(configuration)
    module = 'cour: '+str(grade.cour)
    return module

@app.route('/session/<session_id>/justification/<student_id>/', methods=['GET', 'POST'])
def justification(session_id, student_id):
    student_session = StudentSession.query.filter_by(session_id=session_id, student_id=student_id).first()
    
    grades_unit = student_session.grades_unit
    grades = student_session.grades
    # session = student_session.session
    configuration = student_session.session.configuration
    # display result & calculate at the same time

    # units = []
    # for 

    modules = []
    for grade in grades:
        modules += [get_module_justification(grade, configuration)]
        
    return render_template('session/justification.html', title='Session', modules=modules)
