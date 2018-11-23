from app import app, db
from flask import render_template, request, jsonify, redirect, url_for, flash
from app.models import Promo, Session, StudentSession, Grade, GradeUnit, Unit, Semester,\
     School, Module, Student, AnnualSession, AnnualGrade, Type
from decimal import *
from ast import literal_eval
from sqlalchemy import or_
from app.routesCalculation import config_to_dict, init_all

# from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
# import sys

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


def get_annual_session(session, pId):
    # it shows only after last session in Annual chain
    annual = ''
    annual_dict = session.get_annual_dict()
    if annual_dict['A'] != -1:
        # append after last session in Annual
        annual_chain = session.get_annual_chain()
        if annual_chain[-1] == session.id:
            an_s_id = session.annual_session_id
            url = url_for('annual_session', annual_session_id=an_s_id)
            # name = 'Annual '+str(session.semester.annual)+' Results       (an:'+str(an_s_id)+')'
            name = 'Annual '+str(session.semester.annual)+' Results'
            annual = '{id:"annual_'+str(an_s_id)+'", pId:"'+pId+'", url: "'+url+'", name:"'+name+'", target:"_self", iconSkin:"icon17"},'
    return annual

def get_sessions_tree(promo):
    sessions = Session.query.filter_by(promo_id=promo.id).join(Semester)\
        .order_by(Semester.annual, Semester.semester).all()

    sessions_tree = ''
    # last_session = None
    for session in sessions:
        # semester = session.semester.display_name
        semester = session.semester.get_nbr()

        # prev_session = str(session.prev_session).replace('None', '')
        annual = str(session.annual_session_id)

        name = 'Semester: '
        if session.is_rattrapage:
            name = 'Rattrapage: '
        # name += F'{semester}             (s:{session.id} - a:{annual})'
        # name += F'{semester}             (session:{session.id} - prev:{prev_session} - a:{annual})'
        name += str(semester)

        id = str(session.id)
        pId = 'promo_'+str(promo.id)
        # url = '/session/'+str(session.id)
        url = url_for('session', session_id=session.id)
        # name = '<span style=font-size:20px;>' + name + '</span>'
        if session.is_closed == True:
            p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, url: "'+url+'", target:"_self", iconSkin:"icon13"},'
        else:
            p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, url: "'+url+'", target:"_self"},'

        sessions_tree += p
        sessions_tree += get_annual_session(session, pId)
        # last_session = session

    seperate = True
    if sessions_tree == '':
        seperate = False
    # return sessions_tree + get_creation_links(promo, last_session, seperate)
    return sessions_tree + get_creation_links(promo, seperate)

def get_creation_links(promo, seperate=True):
    sessions = promo.sessions
    semesters = promo.branch.semesters

    links = ''
    if len(semesters) > 0:
        first_semester_id = semesters[0].id

        id = 'new_' + str(promo.id)
        pId = 'promo_' + str(promo.id)
        # init
        name = 'Create First Semester'
        url = url_for('create_session', promo_id=promo.id, semester_id=first_semester_id)
        # url = url_for('create_next_session', promo_id=promo.id)
        # url = '123'

        if len(sessions) > 0:
            first_sessions = sessions[0]
            sessions_chain = first_sessions.get_chain()
            last_session_id = sessions_chain[-1]
            last_session = Session.query.get(last_session_id)

            if last_session is not None:
                next_semester = last_session.semester.get_next()
                if last_session is not None and next_semester is not None:
                    # next_semester_id = next_semester.get_nbr()
                    next_semester_id = next_semester.id
                    name = 'Create Next Semester (' + str(next_semester.get_nbr()) + ')'
                    # url = url_for('create_session', promo_id=promo.id, semester_id=next_semester_id)
                    url = url_for('create_next_session', promo_id=promo.id)
                    if seperate is True:
                        links += '{id:"seperate_'+id+'", pId:"'+pId+'", name:"", iconSkin:"icon0"},'
                    links += '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", target:"_top", url: "'+url+'", iconSkin:"icon01"},'
                    # if seperate is True:
                    #     links += '{id:"seperate_'+id+'", pId:"'+pId+'", name:"", iconSkin:"icon0"},'
        else:
            links += '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", target:"_top", url: "'+url+'", iconSkin:"icon01"},'

    return links 

def get_year(promo):
    # return one (last)
    sessions = Session.query.filter_by(promo_id=promo.id)\
        .join(Semester).order_by('annual desc', Semester.semester, Session.start_date)\
        .all()
    for session in sessions:
        return session.semester.annual
    return '***'

def get_promos_tree(branch, open_p_id):
    promos = branch.promos
    promos_tree = ''
    for promo in promos:
        id = 'promo_' + str(promo.id)
        pId = 'branch_' + str(branch.id)
        name = ' ' + promo.display_name + ' (' + str(get_year(promo)) + ' Year)'
        font = '{"font-weight":"bold", "font-style":"italic"}'
        icon = 'pIcon15'

        open = 'true'
        if open_p_id != 0:
            open = 'false'
            if open_p_id == promo.id:
                open = 'true'

        sessions_tree = get_sessions_tree(promo)
        if sessions_tree == '':
            icon = 'icon15'
        p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:'+open+', iconSkin:"'+icon+'", font:'+font+'},'
        promos_tree += p + sessions_tree 
    return promos_tree

def get_branchs_tree(school, open_b_id, open_p_id):
    branches = school.branches
    branches_tree = ''
    for branch in branches:
        id = 'branch_'+str(branch.id)
        pId = 'school_'+str(school.id)
        p = get_promos_tree(branch, open_p_id)
        open = 'true'
        if open_b_id != 0:
            open = 'false'
            if open_b_id == branch.id:
                open = 'true'
        if p == '':
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+branch.name+'", open:'+open+', iconSkin:"icon11"},'
        else:
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+branch.name+'", open:'+open+', isParent:true},'
        
        branches_tree += b + p
    return branches_tree

def get_schools_tree(open_s_id=0, open_b_id=0, open_p_id=0):
    schools = School.query.all()
    schools_tree = ''
    for school in schools:
        id = 'school_'+str(school.id)
        icon = 'pIcon12'
        branchs_tree = get_branchs_tree(school, open_b_id, open_p_id)
        open = 'true'
        if open_s_id != 0:
            open = 'false'
            if open_s_id == school.id:
                open = 'true'
        s = '{ id:"'+id+'", pId:0, name:"'+school.name+'", open:'+open+', iconSkin:"'+icon+'", isParent:true },'
        schools_tree += s + branchs_tree
    return schools_tree

@app.route('/tree/school/<school_id>/branch/<branch_id>/promo/<promo_id>/', methods=['GET'])
@app.route('/tree/school/<school_id>/branch/<branch_id>/', methods=['GET'])
@app.route('/tree/school/<school_id>/', methods=['GET'])
@app.route('/tree/', methods=['GET', 'POST'])
def tree(school_id=0, branch_id=0, promo_id=0):
    zNodes = '[' + get_schools_tree(int(school_id), int(branch_id), int(promo_id)) + ']'
    return render_template('tree/tree.html', title='Tree', zNodes=zNodes)




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
        return ''
    if errors > 0:
        return 'refused.png'
    if cells_nbr == filled:
        return 'complite.png'
    if filled == 0:
        # return 'not_started.png'
        # return 'not_started2.png'
        return ''
    if cells_nbr!=filled and filled > 0  and  errors == 0:
        return 'in_progress.png'
    return ''

@app.route('/session/<session_id>/', methods=['GET', 'POST'])
def session(session_id=0):
    session = Session.query.filter_by(id=session_id).first_or_404()
    
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
    name = session.promo.name
    # name = session.promo.branch.name
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

# def get_students_candidates(session, students_previous=[]):
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
#

@app.route('/session/<session_id>/averages/', methods=['GET', 'POST'])
def grade_averages(session_id=0):
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
        averages.append(student_session.student.first_name)
        averages.append(student_session.student.last_name)
        for module in modules:
            grade = Grade.query.filter_by(student_session_id=student_session.id, module_id=module[0]).first()
            averages.append(grade.average)
        data.append(averages)

    return render_template('session/averages.html', title='Averages', 
        data=data, modules=modules, session_id=session_id)

#
#

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
        name = 'Result of ' + unit["display_name"] 
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
    header = '<th class="header5">N°</th><th class="header5">Username</th><th class="header5">Full Name</th>'

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
    row = F'<td class="right">{grade.average}</td>'
    if cols_per_module >= 2:
        row += F'<td class="center">{grade.credit}</td>'
    if cols_per_module == 3:
        row += F'<td class="center">**</td>'
    return row

def get_row_unit(grade_unit, cols_per_module):
    grades = grade_unit.student_session.grades
    row = ''
    for grade in grades:
        # get only the grades in unit
        if grade.module.unit_id == grade_unit.unit_id:
            row += get_row_module(grade, cols_per_module)

    row += F'<td class="unit right">{grade_unit.average}</td>'
    if cols_per_module >= 2:
        row += F'<td class="unit center">{grade_unit.credit}</td>'
    if cols_per_module == 3:
        row += F'<td class="unit center">**</td>'
    return row

def get_row_semester(student_session, cols_per_module=2):
    grade_units = student_session.grade_units
    row = ''
    for grade_unit in grade_units:
        row += get_row_unit(grade_unit, cols_per_module)

    row += F'<td class="semester right">{student_session.average}</td>'
    if cols_per_module >= 2:
        row += F'<td class="semester center">{student_session.credit}</td>'
    if cols_per_module == 3:
        row += F'<td class="semester center">{student_session.session_id}</td>'
    return row



@app.route('/session/<session_id>/module/<module_id>/<_all>/', methods=['GET', 'POST']) 
@app.route('/session/<session_id>/module/<module_id>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/student/<student_id>/<_all>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/student/<student_id>/', methods=['GET', 'POST'])
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

        data += "{" + grade_id + name + cour + td + tp + t_pers + stage \
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

    ############################## Test
    # return redirect(url_for('session', session_id=session.id))

    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id
    return redirect(url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id))

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
        flash("you can't delete this session because it not the last one")
        return redirect(url_for('session', session_id=session.id))

    if session.is_closed is True:
        flash('Session ('+str(session_id)+') was not deleted because it is Closed')
    else:
        # cleaning
        for ss in session.student_sessions:
            Grade.query.filter_by(student_session_id=ss.id).delete()
            GradeUnit.query.filter_by(student_session_id=ss.id).delete()
            db.session.delete(ss)
        db.session.delete(session)
        db.session.commit()
        flash('Session ('+str(session_id)+') deleted')
        
    return redirect(url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id))


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

# @app.route('/session/<session_id>/students-rattrapage/', methods=['GET', 'POST'])
# def students_rattrapage(session_id=0):
#     students = StudentSession.query\
#         .filter_by(session_id=session_id)\
#         .filter(or_(StudentSession.credit<30, StudentSession.credit == None))\
#         .join(Student).order_by(Student.username)\
#         .all()
#     return render_template('session/students-rattrapage.html', 
#         title='students-rattrapage', students=students, session_id=session_id)


@app.route('/session/<session_id>/students-rattrapage-form/', methods=['GET', 'POST'])
def students_rattrapage_form(session_id=0):
    students = StudentSession.query\
        .filter_by(session_id=session_id)\
        .filter(or_(StudentSession.credit<30, StudentSession.credit == None))\
        .join(Student).order_by(Student.username)\
        .all()
    return render_template('session/students-rattrapage-form.html', 
        title='students-rattrapage', 
        students=students, 
        session_id=session_id)


def init_student_rattrapage(session, rattrapage):
    students_session = StudentSession.query.filter_by(session_id=session.id)\
        .filter(or_(StudentSession.credit<30, StudentSession.credit==None))\
        .all()
    students_rattrapage = StudentSession.query.filter_by(session_id=rattrapage.id).all()

    std_sess = []
    std_ratt = []
    for student in students_session:
        std_sess.append(student.student_id)
    for student in students_rattrapage:
        std_ratt.append(student.student_id)

    # remove students from rattrapage
    for student_ratt in students_rattrapage:
        if student_ratt.student_id not in std_sess:
            db.session.delete(student_ratt)
    db.session.commit()

    # add students missing in rattrapage
    for student_sess in students_session:
        if student_sess.student_id not in std_ratt:
            ss = StudentSession(session_id=rattrapage.id, student_id=student_sess.student_id)
            db.session.add(ss)
    db.session.commit()

    # transfair all of there grades
    init_grades_rattrapage(session, rattrapage)
    # init_grade_units_rattrapage(session, rattrapage)
    
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
            student_session_id=student_rattrapage_id, module_id=grade_sess.module_id
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
    #


#######################################
#####                             #####
#####                             #####
#####             RATT            #####
#####                             #####
#####                             #####
#######################################


# def get_ratt_modules_list_annual():


# def get_ratt_modules_list_unit(grade_unit):
#     mudules_in_unit = [module.id for module in grade_unit.unit.modules]
#     s_s = grade_unit.student_session

#     grades = Grade.query.filter(Grade.module_id.in_(mudules_in_unit))\
#         .join(StudentSession)\
#         .filter_by(student_id=s_s.student_id, session_id=s_s.session_id).all()

#     _list = []
#     for grade in grades:
#         if grade.credit == grade.module.credit:
#             continue
#         _list.append( grade.module_id )
#     return _list


# # NOTE :: REMOVE THE ROUTE AFTER TESTING
# # @app.route('/session/<session_id>/<student_id>/ratt-modules-list/', methods=['GET', 'POST'])
# def get_ratt_modules_list_semester(session_id, student_id):
#     student_session = StudentSession.query\
#         .filter_by(session_id=session_id, student_id=student_id).first()

#     modules_list = []
#     for g_unit in student_session.grade_units:
#         if g_unit.credit == g_unit.unit.get_unit_cumul_credit():
#             continue
#         modules_list += get_ratt_modules_list_unit(g_unit)

#     return modules_list

# def get_ratt_modules_list_semester_html(session_id, student_id):
#     modules_list = get_ratt_modules_list_semester(session_id, student_id)
#     html = '<table>'
#     for module_id in modules_list:
#         module = Module.query.get(module_id)
#         html += '<tr>'
#         html += '<td>' + module.display_name + ' - ' + module.unit.display_name
#         html += ' - ' + '</td>'

#         html += '</tr>'

#     html += '</table>'

#     return html

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

@app.route('/session/<session_id>/create-rattrapage-form/', methods=['GET', 'POST'])
def create_rattrapage_form(session_id=0):
    students = request.form.getlist('students[]')

    # create rattrapage
    session_rattrapage = create_rattrapage(session_id)
    ratt_id = session_rattrapage.id

    # transfair students
    for student_id in students:
        student_session_ratt = transfer_student_session(session_id, ratt_id, student_id)
        transfer_grades(session_id, ratt_id, student_session_ratt.id, student_id)
    
    db.session.commit()

    return redirect(url_for('session', session_id=session_rattrapage.id))


# @app.route('/session/<session_id>/create-rattrapage/', methods=['GET', 'POST'])
# def create_rattrapage_session(session_id=0):
#     return 'create_rattrapage_session (removed)'
#     # session = Session.query.filter_by(id=session_id).first()
#     # rattrapage = create_rattrapage(session_id)
#     # if session == rattrapage:
#     #     flash('Rattrapage (' + str(rattrapage.semester.semester) + ') already exists')
#     # else:
#     #     flash('created Rattrapage (' + str(rattrapage.semester.semester) + ')')

#     # # transfer student to Ratt session
#     # if rattrapage != None:
#     #     init_student_rattrapage(session, rattrapage)
#     # # redirect to the created session
#     return redirect(url_for('session', session_id=rattrapage.id))


@app.route('/create-next-session/promo/<promo_id>/', methods=['GET', 'POST'])
def create_next_session(promo_id=0):
    promo = Promo.query.get(promo_id)
    next_semester = promo.get_next_semester()
    # first_semester = promo.sessions[0].semester.semester
    # create_session(promo.id, next_semester)
    return redirect( url_for('create_session', promo_id=promo.id, semester_id=next_semester) )
    return ' *** create_next_session *** '


@app.route('/create-session/promo/<promo_id>/semester/<semester_id>/', methods=['GET', 'POST'])
def create_session(promo_id=0, semester_id=0):
    # sessions = Session.query.filter_by(promo_id=promo_id, semester_id=semester_id).all()
    sessions = Session.query.filter_by(
        promo_id=promo_id, semester_id=semester_id, is_rattrapage=False).all()
    
    session = None
    if len(sessions) > 0:
        # check if the session of this simester exists
        session = Session.query\
            .filter_by(promo_id=promo_id, semester_id=semester_id, is_rattrapage=False)\
            .first()
        if session is not None:
            flash('Session (' + str(session.semester.get_nbr()) + ') already exist')
    else:
        session = Session(promo_id=promo_id, semester_id=semester_id)
        db.session.add(session)
        db.session.commit() # can i remove this
        init_annual_session_id(session.id)
        flash('Session (' + str(session.semester.get_nbr()) + ') created')

    # transfair students
    previous_normal = session.get_previous_normal()
    if previous_normal != None:
        for student in previous_normal.student_sessions:
            transfer_student_session(previous_normal.id, session.id, student.student_id)
        init_all(session.id)

    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id
    return redirect( url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id) )

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

# @app.route('/session/<session_id>/create_next_session/', methods=['GET', 'POST'])
# def create_next_session(session_id):
#     session = Session.query.filter_by(id=session_id).first_or_404()
#     next_semester = session.semester.get_next()
#     if next_semester is None:
#         flash('Semester (' + str(session.semester.get_nbr()) + ') is the last semester')
#         return redirect(url_for('session', session_id=session.id))
#     next_semester_id = next_semester.id
#     return redirect(url_for('create_session', promo_id=session.promo_id, semester_id=next_semester_id))


########################################
########################################
########################################

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


# def calculate_annual_average(session1, session2):
#     average = 0
#     return average

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


        # don't forget to include is_fondamental
        if sess_1 != None and sess_2 != None:
            an.average = (sess_1.average + sess_2.average)/2
            # calculate_annual_average(sess_1, sess_2)
            an.credit  = sess_1.credit + sess_2.credit
        else:
            an.average = None
            an.credit  = None

        if ratt_1 != None or ratt_2 != None:
            an.average_r = None
            an.credit_r = None
            r1 = ratt_1
            r2 = ratt_2
            if ratt_1 == None and sess_1 != None:
                r1 = sess_1
            if ratt_2 == None and sess_2 != None:
                r2 = sess_2
            if r1 != None and r2 != None:
                an.average_r = (r1.average + r2.average)/2
                an.credit_r  = r1.credit + r2.credit
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

        array_data.append([index+1, name, 
            an.s1, an.c1, an.rs1, an.rc1,
            an.s2, an.c2, an.rs2, an.rc2, 
            an.average, an.credit, 
            an.average_r, an.credit_r, 
            an.saving_average, an.saving_credit, 
            ''
        ])

    return array_data



@app.route('/annual-session/<annual_session_id>/refrech', methods=['GET', 'POST'])
def annual_session_refrech(annual_session_id=0):
    init_annual_grade(annual_session_id)
    calculate_annual(annual_session_id)
    return redirect(url_for('annual_session', annual_session_id=annual_session_id))

@app.route('/annual-session/<annual_session_id>/', methods=['GET', 'POST'])
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


# ----------------------
# ----------------------
# ----------------------

# def get_grade_tr(student_session, grade_unit):
#     modules_in_unit = [module.id for module in grade_unit.unit.modules]
#     grades_in_unit = Grade.query\
#         .filter_by(student_session_id=student_session.id)\
#         .filter(Grade.module_id.in_(modules_in_unit)).all()

#     trs = ''
#     for grade in grades_in_unit:
#         module = grade.module
#         trs += '<tr>'

#         trs += '<td>'+str(module.code).replace('None', '-')+'</td>'
#         # trs += '<td>'+module.display_name+'</td>'
#         trs += '<td>'+module.name+'</td>'
#         trs += '<td>'+str(module.coefficient)+'</td> <td>'+str(module.credit)+'</td>'
#         trs += '<td>'+str(grade.average)+'</td> <td>'+str(grade.credit)+'</td>'
#         trs += '<td>-1</td>'

#         trs += '</tr>'

#     return trs

# def get_tr_bultin_units(student_session):
#     grade_units = student_session.grade_units
#     tr_unit = ''
#     for grade_unit in grade_units:
#         tr = '<tr>'
#         unit = grade_unit.unit
#         tr += '<td>' + unit.name + '</td>'
#         tr += '<td>' + str( unit.get_unit_cumul_credit() ) + '</td>'
#         tr += '<td>' + str( unit.unit_coefficient ) + '</td>'

#         grade = get_grade_tr(student_session, grade_unit)
#         tr += '<td>' + grade + '</td>'

#         tr += '</tr>'

#         tr_unit += tr
#     return tr_unit

def get_header_bultin_semester():
    header = '<tr class="head">'
    header += '<th colspan=3>Unité d''Enseignement</th>'
    header += '<th colspan=4>Matière d''Enseignement</th>'
    header += '<th colspan=6>Résultats obtenus</th>'
    header += '</tr>'
    header += '<tr class="head">'
    header += '<th rowspan=2>Nature</th>'
    header += '<th rowspan=2>Crédit requis</th>'
    header += '<th rowspan=2>Coeff</th>'

    header += '<th rowspan=2>Code</th>'
    header += '<th rowspan=2>Intitulé</th>'
    header += '<th rowspan=2>Crédit requis</th>'
    header += '<th rowspan=2>Coeff</th>'

    header += '<th colspan=3>Matière</th> <th colspan=3>U.E</th>'
    header += '</tr>'
    header += '<tr class="head">'
    header += '<th>Moyenne</th> <th>Credit</th> <th>Session</th>'
    header += '<th>Moyenne</th> <th>Credit</th> <th>Session</th>'
    header += '</tr>'

    return header


def get_tr_bultin_semester(student_session):
    grade_units = student_session.grade_units

    table = ''
    table += get_header_bultin_semester()


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
            grades_tr += '<td>'+str(module.code).replace('None', '-')+'</td>'
            grades_tr += '<td class="intitule">'+module.display_name.replace(' ', ' ')+'</td>'
            grades_tr += '<td>'+str(module.coefficient)+'</td> <td>'+str(module.credit)+'</td>'
            grades_tr += '<td>'+str(grade.average)+'</td> <td>'+str(grade.credit)+'</td>'
            grades_tr += '<td>-1-</td>'
            if rowspan == 0:
                grades_tr += '<td rowspan=_rowspan_>'+str(grade_unit.average).replace('None', '-')+'</td>'
                grades_tr += '<td rowspan=_rowspan_>'+str(grade_unit.credit).replace('None', '-')+'</td>'
                grades_tr += '<td rowspan=_rowspan_>+1+</td>'
            
            grades_tr += '</tr>'
            rowspan += 1

        unit = grade_unit.unit
        tr =  '<td rowspan='+str(rowspan)+'>'+unit.display_name+'</td>'
        tr += '<td rowspan='+str(rowspan)+'>'+str(unit.get_unit_cumul_credit())+'</td>'
        tr += '<td rowspan='+str(rowspan)+'>'+str(unit.unit_coefficient)+'</td>'
        tr += grades_tr.replace('_rowspan_', str(rowspan) )

        table += '<tr>' + tr + '</tr>'

    return '<table class="table table-bordered">' + table + '</table>'


@app.route('/session/<session_id>/student/<student_id>/bultin/', methods=['GET', 'POST'])
def bultin_semester(session_id, student_id):
    student_session = StudentSession.query\
        .filter_by(session_id=session_id, student_id=student_id).first()

    table = get_tr_bultin_semester(student_session)

    return render_template('student/bultin-semester.html', title='****', table=table)








# ----------------------
# ----------------------
# ----------------------


def get_semester_result_data(session_id, cols_per_module=2):
    data_arr = []
    students_session = StudentSession.query.filter_by(session_id=session_id)\
        .join(Student).order_by(Student.username).all()
    for index, student_session in enumerate(students_session, start=1):
        student = student_session.student
        _std = '<td>' + str(index) + '</td>'
        _std += '<td class=no-wrap>' + student.username + '</td>'
        _std += '<td class=no-wrap>' + student.last_name + ' ' + student.first_name + '</td>'
        row = _std + get_row_semester(student_session, cols_per_module)
        data_arr.append(row)

    for index, student_session in enumerate(students_session, start=1):
        student = student_session.student
        _std = '<td>' + str(index) + '</td>'
        _std += '<td class=no-wrap>' + student.username + '</td>'
        _std += '<td class=no-wrap>' + student.last_name + ' ' + student.first_name + '</td>'
        row = _std + get_row_semester(student_session, cols_per_module)
        data_arr.append(row)

    return data_arr


@app.route('/session/<session_id>/semester-result/', methods=['GET', 'POST'])
def semester_result(session_id=0):
    session = Session.query.filter_by(id=session_id).first_or_404()
    header = get_thead(session.configuration, 2)
    data_arr = get_semester_result_data(session_id, 2)
    return render_template('session/semester-result.html',
        title='Semester ' + str(session.semester.semester) + ' Result', 
        header=header, data_arr=data_arr, session=session)

@app.route('/session/<session_id>/semester-result-print/<_id>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/semester-result-print/', methods=['GET', 'POST'])
def semester_result_print(session_id=0, _id=0):
    session = Session.query.filter_by(id=session_id).first_or_404()
    headers = get_thead(session.configuration, 2)
    data_arr = get_semester_result_data(session_id, 2)
    return render_template('session/semester-result-print.html', 
        title='Semester ' + str(session.semester.semester) + ' Result', 
        headers=headers, data_arr=data_arr, session=session, id=_id)



# 
## PDF 
# 

def get_module_cols(module_id):
    module = Module.query.get(module_id)
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
    headers = []
    for percentage in percentages:
        type_id = percentage.type_id
        type = Type.query.get(type_id)
        headers.append(type.type + ' ('+str(int(percentage.percentage*100))+'%)')
        # headers.append(type.type + ' ('+  +'%)')
    return headers

def create_data_for_module(grades, cols):
    data = []
    for grade in grades:
        record = []
        student = grade.student_session.student
        # record.append(#)
        record.append(student.username)
        record.append(student.last_name)
        record.append(student.first_name)
        record.append(grade.cour)
        if 'td' in cols:
            record.append(grade.td)
        if 'tp' in cols:
            record.append(grade.tp)
        if 't_pers' in cols:
            record.append(grade.t_pers)

        data.append(record)
    return data

# print empty
# with percentages
# with notes
# with averages
@app.route('/session/<session_id>/module/<module_id>/print/<_full>/', methods=['GET', 'POST'])
@app.route('/session/<session_id>/module/<module_id>/print/', methods=['GET', 'POST'])
def module_print(session_id=0, module_id=0, _full=''):
    grades = Grade.query.filter_by(module_id=module_id)\
        .join(StudentSession).filter_by(session_id=session_id)\
        .join(Student).order_by(Student.username)\
        .all()
    cols = get_module_cols(module_id)
    headers = get_module_headers(module_id)
    data_arr = create_data_for_module(grades, cols)
    module = Module.query.get(module_id)

    return render_template('session/semester-module-print.html', title='module ***', 
        headers=headers, data_arr=data_arr, module=module)


# def view_session_dlc(*args, **kwargs):
#     session_id = request.view_args['session_id']
#     session = Session.query.get(session_id)
#     return [{'text': session.id}]

# @app.route('/ss/dd/<session_id>/', methods=['GET', 'POST'])
# @register_breadcrumb(app, '.', 'Home')
# def semester__print(session_id=0):
#     return 'aaaaaaa'

#
#
#

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


@app.route('/session/<session_id>/module/<module_id>/students-empty/')
def print_module_students_empty(session_id=0, module_id=0):
    url = url_for('module_print', session_id=session_id, module_id=module_id, _external=True)
    # url = 'http://localhost:5000/session/1/module/1/print/'
    pdf_file_name = 'module_students_print.pdf'
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
