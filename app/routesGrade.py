from app import app, db
from flask import render_template, request, redirect, url_for, flash
from app.models import StudentSession, Grade, Module, Session, Student, Type, ModuleSession
from app.forms import ModuleSessionForm
from flask_breadcrumbs import register_breadcrumb
from datetime import datetime
from app.routesCalculation import calculate_student





def create_module_session(session_id, module_id):
    module_session = ModuleSession(session_id=session_id, module_id=module_id)
    db.session.add(module_session)
    db.session.commit()
    return module_session

def collect_data_from_grade(grade):
    grade_id = 'id: ' + str(grade.id) + ', '
    username = 'username: "' + grade.get_username() + '", '
    student_name = 'student_name: "' + grade.get_student_name() + '", '
    code = 'code: "' + str(grade.module.code) + '", '
    # module_name = 'module_name: "' + grade.module.get_label() + '", '
    module_name = 'module_name: "' + grade.module.get_label().replace('"', ' ') + '", '

    cour = 'cour: ' + str(grade.cour) + ', '
    td = 'td: ' + str(grade.td) + ', '
    tp = 'tp: ' + str(grade.tp) + ', '
    t_pers = 't_pers: ' + str(grade.t_pers) + ', '
    stage = 'stage: ' + str(grade.stage) + ', '
    saving_grade = 'saving_grade: ' + str(grade.saving_grade) + ', '
    average = 'average: ' + str(grade.average) + ', '
    credit = 'credit: ' + str(grade.credit) + ', '
    formula = 'formula: ' + str(grade.formula).replace("None", "") + ', '
    is_rattrapage = 'is_rattrapage: false, '
    original_grade = 'original_grade: null, '
    if grade.is_rattrapage is True:
        is_rattrapage = 'is_rattrapage: true, '
        # original_grade = 'original_grade: '+str( get_original_grade(grade) )+', '
        original_grade = 'original_grade: '+str( grade.get_ratt_original_grade() )+', '

    return grade_id + username + student_name + code + module_name \
         + cour + td + tp + t_pers + stage \
         + saving_grade + average + credit + formula  + is_rattrapage + original_grade

def collect_student_data_grid(grades, session, SHOW_SAVING_GRADE):
    data = ''
    for grade in grades:
        data_part = collect_data_from_grade(grade)
        is_savable = 'is_savable: false, '

        module_session = get_module_session(session, grade.module)
        if module_session.saving_enabled == True:
            is_savable = 'is_savable: true, '

        data += '{' + data_part + is_savable +'}, '
 
    return '[ ' + data + ' ]'
   
def collect_module_data_grid(grades, session, SHOW_SAVING_GRADE):
    data = ''
    for grade in grades:
        data_part = collect_data_from_grade(grade)
        is_savable = 'is_savable: false, '

        if SHOW_SAVING_GRADE == True:
            if session.is_rattrapage == True:
                if grade.is_rattrapage == True:
                    is_savable = 'is_savable: true, '
            else:
                is_savable = 'is_savable: true, '

        data += '{' + data_part + is_savable +'}, '
 
    return '[ ' + data + ' ]'

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
@register_breadcrumb(app, '.tree_session.session.grade', '*** Grades by ***', dynamic_list_constructor=grade_dlc)
def grade(session_id=0, module_id=0, student_id=0, _all=''):
    session = Session.query.get_or_404(session_id)
    module = Module.query.get(module_id)
    student = Student.query.get(student_id)
    module_session = None

    grid_title = F' *********** '
    grades = None
    data = '[]'
    type = ''
    SHOW_SAVING_GRADE = False

    if module_id != 0:
        module_session = get_module_session(session, module)
        SHOW_SAVING_GRADE = module_session.saving_enabled
        type = 'module'
        grid_title = F'Module: {module.code} - {module.display_name}'
        grades = Grade.query.filter_by(module_id=module_id)\
            .join(StudentSession).filter_by(session_id=session_id).all()
        #
        data = collect_module_data_grid(grades, session, SHOW_SAVING_GRADE)

        # what about type = 'student'
        get_hidden_values_flash(grades, session, module)

    if student_id != 0:
        type = 'student'
        grid_title = F'Student: {student.username} - {student.last_name} - {student.first_name}'
        grades = Grade.query.join(StudentSession)\
            .filter_by(session_id=session_id, student_id=student_id).all()
        for grade in grades:
            module_session = get_module_session(session, grade.module)
            if module_session != None and module_session.saving_enabled == True:
                SHOW_SAVING_GRADE = True
                # comment this if you wan't it to create all module_sessions
                # commented it to aviod looping all grades(modules)
                break
        #
        data = collect_student_data_grid(grades, session, SHOW_SAVING_GRADE)

    return render_template('grade/grade.html', title='Grade Edit', 
        data=data, _all=_all.lower(), grid_title=grid_title, type=type, 
        session=session, module=module, student=student, 
        module_session=module_session, SHOW_SAVING_GRADE=SHOW_SAVING_GRADE)


def get_module_session(session, module):
    module_session = ModuleSession.query.\
        filter_by(session_id=session.id, module_id=module.id).first()
    if module_session == None:
        module_session = create_module_session(session.id, module.id)
    return module_session

def get_hidden_values_flash(grades, session, module):
    cols = get_module_cols(module)
    # fields = ['cour', 'td', 'tp', 't_pers', 'stage', 'saving_grade']
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
        # if 'saving_grade' in hidden_cols:
        #     if grade.saving_grade!=None and grade.saving_grade!='':
        #         hidden_value = True

    if hidden_value == True:
        url = url_for('grade', session_id=session.id, module_id=module.id, _all='all')
        btn = '<a href="'+url+'" class="btn btn-warning" role="button">Show All Fields</a>'
        flash('there is hidden value, because the Configuration changed  '+btn, 'alert-warning')

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
    if grade.saving_grade != data['saving_grade']:
        return True

    return False

@app.route('/grade/save/type/<type>/', methods = ['GET', 'POST'])
@app.route('/grade/save/', methods = ['GET', 'POST'])
def grade_save(type=''):
    data_arr = request.json

    student_id = None
    if type == 'student':
        student_id = int(data_arr[0]['id'])

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

        grade.saving_grade = data['saving_grade']

        ## commented this to not save Null Averages
        # grade.average = data['average']
        # grade.credit = data['credit']

        db.session.commit()

    # if type is student return : Annual and Semestre Average and Credit
    # NOTE: it calculate everytime
    if type == 'student':
        grade_id = int(data_arr[0]['id'])
        grade = Grade.query.get(grade_id)
        if grade == None:
            return 'type student but Grade not found'
        student_session = grade.student_session

        # return str(student_session.session.id) + ' - ' + str(student_session.student.id)
        return calculate_student(student_session.session, student_session.student)
        return 'Annual and Semestre Average and Credit'


    return 'data saved hhhhhhh'









######################################################################################
######################################################################################
####                        _       _                            _                ####
####                       | |     | |                          (_)               ####
####    _ __ ___   ___   __| |_   _| | ___     ___  ___  ___ ___ _  ___  _ __     ####
####   | '_ ` _ \ / _ \ / _` | | | | |/ _ \   / __|/ _ \/ __/ __| |/ _ \| '_ \    ####
####   | | | | | | (_) | (_| | |_| | |  __/   \__ \  __/\__ \__ \ | (_) | | | |   ####
####   |_| |_| |_|\___/ \__,_|\__,_|_|\___|   |___/\___||___/___/_|\___/|_| |_|   ####
####                                                                              ####
######################################################################################
######################################################################################



#
# it only allow one teacher
#
@app.route('/session/<session_id>/module/<module_id>/module-session/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree_session.session.grade.module_session', 'Module Session')
def module_session_config(session_id, module_id):
    module_session = ModuleSession.query.filter_by(session_id=session_id, module_id=module_id).first()

    form = ModuleSessionForm(module_session.id)
    if form.validate_on_submit():
        remember_savable = module_session.saving_enabled
        module_session.teacher_id = None if form.teacher_id.data == -1 else form.teacher_id.data
        module_session.start_date = form.start_date.data
        module_session.finish_date = form.finish_date.data
        module_session.exam_date = form.exam_date.data
        module_session.results_delivered_date = form.results_delivered_date.data
        module_session.exam_surveyors = form.exam_surveyors.data
        module_session.saving_enabled = form.saving_enabled.data
        # calculate session
        # module_session.session.set_dirty()
        if remember_savable != form.saving_enabled.data:
            # we recalculate to incorporate Saving
            module_session.session.calculate()
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
        form.saving_enabled.data = module_session.saving_enabled


    return render_template('grade/module_session.html', title='module_session', form=form)


##########################
##########################

def get_module_cols(module):
    # raise Exception ('ddddd:'+str(module.id))
    percentages = module.percentages
    cols = []
    for percentage in percentages:
        type_id = percentage.type_id
        type = Type.query.get_or_404(type_id)
        cols.append(type.grade_table_field)
    return cols

def get_module_columns(module, show_avr):
    percentages = module.percentages
    headers = ['#', 'Matricule', 'Nom et Prenom']

    for percentage in percentages:
        type_id = percentage.type_id
        type = Type.query.get_or_404(type_id)
        headers.append(type.type + ' ('+str(int(percentage.percentage*100))+'%)')
        # headers.append(type.type + ' ('+  +'%)')
    if show_avr == 'yes':
        headers.append('<u>Moyen</u>')
        headers.append('<u>Credit</u>')
    return headers

def collect_data_for_module(grades, cols, empty=''):
    data = []
    for index, grade in enumerate(grades, start=1):
        record = []
        student = grade.student_session.student

        record.append(index)
        record.append(student.username)
        record.append(student.last_name + ' ' + student.first_name)
        # record.append(student.first_name)
        if empty == 'yes':
            #cour
            record.append('')
            if 'td' in cols:
                record.append('')
            if 'tp' in cols:
                record.append('')
            if 't_pers' in cols:
                record.append('')
            if 'stage' in cols:
                record.append('')
            if 'saving_grade' in cols:
                record.append('')
            if 'average' in cols:
                record.append('')
            if 'credit' in cols:
                record.append('')
        else:
            # if saving enabled and filled
            saving_grade = None
            if grade.saving_grade != None:
                module_session = ModuleSession.query.filter_by(
                    session_id=grade.student_session.session_id,
                    module_id=grade.module_id).first()
                if module_session.saving_enabled == True:
                    saving_grade = grade.saving_grade


            #cour
            record.append( saving_grade if saving_grade != None else grade.cour )
            # WARNING: this one shoold be Dynamic
            if 'td' in cols:
                record.append( saving_grade if saving_grade != None else grade.td )
            if 'tp' in cols:
                record.append( saving_grade if saving_grade != None else grade.tp )
            if 't_pers' in cols:
                record.append( saving_grade if saving_grade != None else grade.t_pers )
            if 'stage' in cols:
                record.append( saving_grade if saving_grade != None else grade.stage )
            # if 'saving_grade' in cols:
            #     record.append(grade.saving_grade)
            if 'average' in cols:
                record.append(grade.average)
            if 'credit' in cols:
                record.append(grade.credit)

        data.append(record)
    return data

# print empty
# with grades
# with averages
# sort
def create_module_print_table(session, module, empty, sort, show_avr):
    grades = None
    if sort == 'username':
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
    if show_avr == 'yes':
        cols.append('average')
        cols.append('credit')
    columns = get_module_columns(module, show_avr)
    data_arr = collect_data_for_module(grades, cols, empty)


    table = '<table style="width: 100%;">'
    table += '<thead><tr>'
    for column in columns:
        table += '<th>' + column + '</th>'
    table += ' </tr></thead>'

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

    time = '#é$/&?|[+{#%*#$='
    if module.time != None: time = module.time

    module_session = ModuleSession.query\
        .filter_by(module_id=module.id)\
        .join(Session).filter_by(id=session.id)\
        .first()

    teacher = None
    if module_session != None:
        teacher = module_session.teacher

    teacher_name = '#é$/&?|[+{#%*#$='
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
        </br><font size="+2"><b>Module: </b>{module.code} <b>-</b> {module.display_name}</font></br>
        <b>Coefficient: </b>{module.coefficient} <b>-</b> 
        <b>Credit: </b>{module.credit} <b>-</b> 
        <b>VHS: </b>{time} <b>-</b> 
        <b>Enseignant: </b>{teacher_name}
      </div>
    """
    return header

@app.route('/session/<session_id>/module/<module_id>/print/', methods=['GET', 'POST'])
def module_print(session_id=0, module_id=0):
    session = Session.query.get_or_404(session_id)
    module = Module.query.get_or_404(module_id)

    empty = request.args.get('empty', default='', type=str)
    sort = request.args.get('sort', default='username', type=str)
    show_avr = request.args.get('show', default='yes', type=str)

    # return "module_print: " + str(module.name)

    print_header = get_module_print_header(session, module)
    table = create_module_print_table(session, module, empty, sort, show_avr)
    
    branch = session.promo.branch.name
    semester = session.semester.get_nbr()
    dt = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    title = 'Releve de Notes '+branch+' S'+str(semester) + ' {'+module.get_label()+'}' + ' ['+session.promo.name+'] ('+str(dt)+')'

    return render_template('grade/module-print.html', 
        title=title, table=table, print_header=print_header, empty=empty)



