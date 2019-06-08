from app import app, db
from flask import render_template, request, redirect, url_for, flash
from app.models import StudentSession, Grade, Module, Session, Student, Type, ModuleSession
from app.forms import ModuleSessionForm
from flask_breadcrumbs import register_breadcrumb
from datetime import datetime





def grade_dlc(*args, **kwargs):
    session_id = request.view_args['session_id']
    
    if 'module_id' in request.view_args:
        module_id = request.view_args['module_id']
        module = Module.query.get_or_404(module_id)
        text = 'Module ('+module.code+' '+module.name+')'
        return [{'text': text, 
            'url': url_for('grade', session_id=session_id, module_id=module_id)}]

    elif 'student_id' in request.view_args:
        student_id = request.view_args['student_id']
        student = Student.query.get_or_404(student_id)
        text = 'Student ('+student.username+' '+student.last_name+' '+student.first_name+')'
        return [{'text': text, 
            'url': url_for('grade', session_id=session_id, student_id=student_id)}]

    # return [{'text': '***', 'url': '']



@app.route('/session/<session_id>/module/<module_id>/<_all>/', methods=['GET', 'POST']) 
@app.route('/session/<session_id>/module/<module_id>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/student/<student_id>/<_all>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/student/<student_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.grade', 'Grades by ***** ', dynamic_list_constructor=grade_dlc)
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

    module = Module.query.filter_by(id=module_id).first()
    student = Student.query.filter_by(id=student_id).first()
    session = Session.query.get_or_404(session_id)
    # 
    # Note: it will return only one Record
    module_session = ModuleSession.query.\
        filter_by(session_id=session_id, module_id=module_id).first()


    if type == 'module':
        get_hidden_values_flash(grades, session_id, module.id)

    # grid_title = F'Module: {module.display_name}'
    grid_title = F'Module: ***********'
    if module_id!=0:
        grid_title = F'Module: {module.code} - {module.display_name}'
    if student_id!=0:
        student = Student.query.filter_by(id=student_id).first_or_404()
        grid_title = F'Student: {student.username} - {student.last_name} - {student.first_name}'

    return render_template('grade/grade.html', title='Grade Edit', 
        data=data, _all=_all.lower(), grid_title=grid_title, type=type, 
        session=session, module=module, student=student, module_session=module_session)


def get_hidden_values_flash(grades, session_id, module_id):
    cols = get_module_cols(module_id)
    fields = ['cour', 'td', 'tp', 't_pers', 'stage']
    hidden_cols = []
    for field in fields:
        if field not in cols: 
            hidden_cols.append(field)

    hidden_value = False

    for grade in grades:
        if 'cour' in hidden_cols:
            if grade.cour!=None and grade.cour!='':
                hidden_value = True
        if 'td' in hidden_cols:
            if grade.td!=None and grade.td!='':
                hidden_value = True
        if 'tp' in hidden_cols:
            if grade.tp!=None and grade.tp!='':
                hidden_value = True
        if 't_pers' in hidden_cols:
            if grade.t_pers!=None and grade.t_pers!='':
                hidden_value = True
        if 'stage' in hidden_cols:
            if grade.stage!=None and grade.stage!='':
                hidden_value = True

    if hidden_value == True:
        url = url_for('grade', session_id=session_id, module_id=module_id, _all='all')
        btn = '<a href="'+url+'" class="btn btn-warning" role="button">Show All Fields</a>'
        flash('there is hidden value, because the Configuration changed  '+btn, 'alert-warning')

def get_original_grade(grade):
    original_grade = 0
    parallel_session = grade.student_session.session.get_parallel_session()
    original = Grade.query.filter_by(module_id=grade.module_id)\
        .join(StudentSession).filter_by(
            session_id=parallel_session.id, 
            student_id=grade.student_session.student_id).first()
    # get the rattrapable
    if original != None:
        field = grade.module.get_rattrapable_field()
        original_grade = getattr(original, field)
    return original_grade

def create_data_grid(grades, type='module'):
    data = ''
    for grade in grades:
        grade_id = 'id: ' + str(grade.id) + ', '
        username = 'username: "' + grade.get_username() + '", '
        name = 'name: "' + grade.get_student_name() + '", '
        if type != 'module':
            name = 'name: "' + grade.module.display_name + '", '

        cour = 'cour: ' + str(grade.cour) + ', '
        td = 'td: ' + str(grade.td) + ', '
        tp = 'tp: ' + str(grade.tp) + ', '
        t_pers = 't_pers: ' + str(grade.t_pers) + ', '
        stage = 'stage: ' + str(grade.stage) + ', '

        average = 'average: ' + str(grade.average) + ', '
        credit = 'credit: ' + str(grade.credit) + ', '
        formula = 'formula: ' + str(grade.formula).replace("None", "") + ', '

        is_rattrapage = 'is_rattrapage: false, '
        original_grade = 'original_grade: null '
        if grade.is_rattrapage is True:
            is_rattrapage = 'is_rattrapage: true, '
            original_grade = 'original_grade: '+str( get_original_grade(grade) )+' '

        data += '{' + username + grade_id + name + cour + td + tp + t_pers + stage \
             + average + credit + formula + is_rattrapage + original_grade +'}, '
 
    return '[ ' + data + ' ]'


def grade_going_to_change(grade, data):
    if grade.cour != data['cour']:
        return True
    if grade.td != data['td']:
        return True
    if grade.tp != data['tp']:
        return True
    if grade.t_pers != data['t_pers']:
        return True
    if grade.stage != data['stage']:
        return True

    return False

@app.route('/grade/save/', methods = ['GET', 'POST'])
def grade_save():
    data_arr = request.json

    for i, data in enumerate(data_arr, start=0):
        grade = Grade.query.filter_by(id = int(data['id'])).first()

        if grade_going_to_change(grade, data) == True:
            grade.is_dirty = True

        # saved fields must be according to the Permission
        #
        grade.cour = data['cour']
        grade.td = data['td']
        grade.tp = data['tp']
        grade.t_pers = data['t_pers']
        grade.stage = data['stage']


        # commected this to not save Null Averages
        # grade.average = data['average']
        # grade.credit = data['credit']

        db.session.commit()

    return 'data saved'


##########################
##########################



#
# it only allow one teacher
#
@app.route('/session/<session_id>/module/<module_id>/module-session/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.grade.module_session', 'Module Session')
def module_session_update(session_id, module_id):
    module_sessions = ModuleSession.query.\
        filter_by(session_id=session_id, module_id=module_id)\
        .all()

    if len(module_sessions) == 0:
        #create new module_session
        module_session = ModuleSession(
            session_id=session_id, 
            module_id=module_id
        )
        db.session.add(module_session)
        db.session.commit()
    else:
        module_session = module_sessions[0]

    form = ModuleSessionForm(module_session.id)
    if form.validate_on_submit():    
        module_session.teacher_id = None if form.teacher_id.data == -1 else form.teacher_id.data
        module_session.start_date = form.start_date.data
        module_session.finish_date = form.finish_date.data
        module_session.exam_date = form.exam_date.data
        module_session.results_delivered_date = form.results_delivered_date.data
        module_session.exam_surveyors = form.exam_surveyors.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('grade', session_id=session_id, module_id=module_id))
    elif request.method == 'GET':
        form.teacher_id.data = module_session.teacher_id
        form.start_date.data = module_session.start_date
        form.finish_date.data = module_session.finish_date
        form.exam_date.data = module_session.exam_date
        form.results_delivered_date.data = module_session.results_delivered_date
        form.exam_surveyors.data = module_session.exam_surveyors

    return render_template('grade/module_session.html', title='module_session', form=form)


##########################
##########################

def get_module_cols(module):
    percentages = module.percentages
    cols = []
    for percentage in percentages:
        type_id = percentage.type_id
        type = Type.query.get_or_404(type_id)
        cols.append(type.grade_table_field)
    return cols

def get_module_columns(module):
    percentages = module.percentages
    headers = ['#', 'Matricule', 'Nom', 'Prenom']

    for percentage in percentages:
        type_id = percentage.type_id
        type = Type.query.get_or_404(type_id)
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
                record.append(grade.stage)

        data.append(record)
    return data

# print empty
# with grades
# with averages
# by order
def get_module_print_table(session, module, empty='', order='username'):
    grades = None
    if order == 'username':
        grades = Grade.query.filter_by(module_id=module.id)\
            .join(StudentSession).filter_by(session_id=session.id)\
            .join(Student).order_by(Student.username)\
            .all()
    else:
        grades = Grade.query.filter_by(module_id=module.id)\
            .join(StudentSession).filter_by(session_id=session.id)\
            .join(Student).order_by(Student.last_name, Student.first_name)\
            .all()

    cols = get_module_cols(module)
    columns = get_module_columns(module)
    data_arr = create_data_for_module(grades, cols, empty)


    table = '<table class="table table-condensed ">'
    table += '<thead>'
    table += '<tr style="background-color: lightgrey;">'
    for column in columns:
        table += '<th>' + column + '</th>'
    table += '</thead> </tr>'

    table += '<tbody>'
    for data in data_arr:
        table += '<tr>'
        # table += '<td>'+str(data)+'</td>'
        for _da in data:
            table += '<td>' + str(_da) + '</td>'
        table += '</tr>'

    table += '</tbody>'
    table += '</table>'

    return table

def get_module_print_header(session, module):
    school = session.promo.branch.school.description
    branch = session.promo.branch.description
    annual = session.semester.annual.get_string_literal()
    semester = session.get_name()
    promo = session.promo.name
    annual_pedagogique = session.get_annual_pedagogique()

    time = '?????'
    if module.time != None: time = module.time

    module_session = ModuleSession.query\
        .filter_by(module_id=module.id)\
        .join(Session).filter_by(id=session.id)\
        .first()

    teacher = None
    if module_session != None:
        teacher = module_session.teacher

    teacher_name = '???'
    if teacher != None:
        teacher_name = teacher.last_name + ' ' + teacher.first_name

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
            <b><font size="+2">Relevé de Notes {semester}</font></b>
        </div>
        <div style="flex-grow: 1;" align="right">
            {annual}<br/>
            {branch}
        </div>
      </div>
      
      <div class="container" >
        <h4><b>Module: </b>{module.code} <b>-</b> {module.display_name}</h4>
        <b>Coefficient: </b>{module.coefficient} <b>-</b> 
        <b>Credit: </b>{module.credit} <b>-</b> 
        <b>VHS: </b>{time} <b>-</b> 
        <b>Enseignant: </b>{teacher_name}
      </div>
    """
    return header

@app.route('/session/<session_id>/module/<module_id>/print/order/<order>/empty/<empty>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/module/<module_id>/print/empty/<empty>/order/<order>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/module/<module_id>/print/order/<order>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/module/<module_id>/print/empty/<empty>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/module/<module_id>/print/', methods=['GET', 'POST'])
def module_print(session_id=0, module_id=0, empty='', order='username'):
    session = Session.query.get_or_404(session_id)
    module = Module.query.get_or_404(module_id)

    print_header = get_module_print_header(session, module)
    table = get_module_print_table(session, module, empty, order)
    
    branch = session.promo.branch.name
    semester = session.semester.get_nbr()
    dt = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    title = 'Releve de Notes '+branch+' S'+str(semester) + ' {'+module.get_label()+'}' + ' ['+session.promo.name+'] ('+str(dt)+')'

    return render_template('grade/module-print.html', title=title, table=table, print_header=print_header)



