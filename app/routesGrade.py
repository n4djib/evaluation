from app import app, db
from flask import render_template, request, redirect, url_for, flash
from app.models import StudentSession, Grade, Module, Session, Student
from flask_breadcrumbs import register_breadcrumb



@app.route('/session/<session_id>/module/<module_id>/<_all>/', methods=['GET', 'POST']) 
@app.route('/session/<session_id>/module/<module_id>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/student/<student_id>/<_all>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/student/<student_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.grade', 'Grades')
def grade(session_id=0, module_id=0, student_id=0, _all=''):
    grades = None
    if session_id == 0:
        type = 'module'
        grades = Grade.query.all()
    else:
        if module_id != 0:
            type = 'module'
            grades = Grade.query.filter_by(module_id=module_id)\
                .join(StudentSession).filter_by(session_id=session_id)\
                .all()
        if student_id != 0:
            type = 'student'
            grades = Grade.query\
                .join(StudentSession).filter_by(session_id=session_id, student_id=student_id)\
                .all()

    ### Initialize the Columns
    # cols = get_visible_cols(grades, type, _all)
    data = create_data_grid(grades, type)

    grid_title = ''
    module = Module.query.filter_by(id=module_id).first()
    # grid_title = F'Module: {module.display_name}'
    grid_title = F'Module: ***********'
    if module_id!=0:
        grid_title = F'Module: {module.display_name}'
    if student_id!=0:
        student = Student.query.filter_by(id=student_id).first()
        grid_title = F'Student: {student.username} - {student.first_name} - {student.last_name}'

    session = Session.query.get(session_id)
    return render_template('grade/grade.html', title='Grade Edit', 
        data=data, _all=_all.lower(), grid_title=grid_title, type=type, session=session, module=module)

def create_data_grid(grades, type='module'):
    data = ""
    for grade in grades:
        grade_id = "id: " + str(grade.id) + ", "

        username = "username: '" + grade.get_username() + "', "
        name = "name: '" + grade.get_student_name() + "', "
        if type != "module":
            name = "name: '" + grade.module.name + "', "

        cour = "cour: " + str(grade.cour) + ", "
        td = "td: " + str(grade.td) + ", "
        tp = "tp: " + str(grade.tp) + ", "
        t_pers = "t_pers: " + str(grade.t_pers) + ", "
        stage = "stage: " + str(grade.stage) + ", "

        average = "average: " + str(grade.average) + ", "
        credit = "credit: " + str(grade.credit) + ", "
        # formula = "formula: `" + grade.formula + "` "
        formula = "formula: " + str(grade.formula).replace('None', '') + ", "

        is_rattrapage = "is_rattrapage: false,"
        if grade.is_rattrapage is True:
            is_rattrapage = "is_rattrapage: true,"

        data += "{" + username + grade_id + name + cour + td + tp + t_pers + stage \
             + average + credit + formula + is_rattrapage + "}, "
 
    return "[ " + data + " ]"

@app.route('/grade/save/', methods = ['GET', 'POST'])
def grade_save():
    data_arr = request.json

    for i, data in enumerate(data_arr, start=0):
        grade = Grade.query.filter_by(id = int(data['id'])).first()
        #
        # saved fields must be according to the Permission
        #
        grade.cour = data['cour']
        grade.td = data['td']
        grade.tp = data['tp']
        grade.t_pers = data['t_pers']
        grade.stage = data['stage']
        grade.average = data['average']
        grade.credit = data['credit']

        db.session.commit()

    return 'data saved'

