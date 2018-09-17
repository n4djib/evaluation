from app import app, db
from flask import render_template, request, jsonify, redirect, url_for, flash
from app.models import Session, StudentSession, Grade, Unit, Semester, School, Module, Student, AnnualSession
# from flask_breadcrumbs import register_breadcrumb
from decimal import *
from ast import literal_eval
from sqlalchemy import or_
from app.routesCalculation import config_to_dict, init_all


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
            annual = '{id:"annual_'+str(an_s_id)+'", pId:"'+pId+'", url: "'+url+'", name:"Annual '+str(session.semester.annual)+' (an:'+str(an_s_id)+') Results", iconSkin:"icon17"},'
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
        name += F'{semester}             (s:{session.id} - a:{annual})'
        # name += F'{semester}             (session:{session.id} - prev:{prev_session} - a:{annual})'

        id = str(session.id)
        pId = 'promo_'+str(promo.id)
        # url = '/session/'+str(session.id)
        url = url_for('session', session_id=session.id)
        # name = '<span style=font-size:20px;>' + name + '</span>'
        if session.is_closed == True:
            p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, url: "'+url+'", iconSkin:"icon13"},'
        else:
            p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, url: "'+url+'"},'

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
        name = 'Next Session (1)'
        url = url_for('create_session', promo_id=promo.id, semester_id=first_semester_id)

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
                    name = 'Next Session (' + str(next_semester.get_nbr()) + ')'
                    url = url_for('create_session', promo_id=promo.id, semester_id=next_semester_id)
                    if seperate is True:
                        links += '{id:"seperate_'+id+'", pId:"'+pId+'", name:"", iconSkin:"icon0"},'
                    links += '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", target:"_top", url: "'+url+'", iconSkin:"icon01"},'
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

    students_list = Student.query.join(StudentSession).filter_by(session_id=session_id).all()
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
    students_session = StudentSession.query.filter_by(session_id=session_id).all()
    for student_session in students_session:
        if str(student_session.student_id) in students_from:
            grades = student_session.grades
            for grade in grades:
                db.session.delete(grade)
            grades_unit = student_session.grades_unit
            for grade_unit in grades_unit:
                db.session.delete(grade_unit)
            db.session.delete(student_session)
            dirty_remove = True
    db.session.commit()

    message_remove = 'No One Removed from Session: ' + str(session_id)
    if dirty_remove == True:
        dirty_remove = 'Removed Student(s) from Session: ' + str(session_id)

    return message_add + '   -   ' + message_remove

def get_students_previous(session):
    students_previous = Student.query.join(StudentSession)\
        .join(Session).filter_by(promo_id=session.promo_id).all()
    return students_previous

# def get_students_candidates(session, students_previous=[]):
def get_students_candidates(session):
    # I HAVE TO FIND ONLY THE ONES WITHOUT A SESSION
    # or just take ones from the Promo

    students_previous = get_students_previous(session)
    students_in_other_promos = Student.query.join(StudentSession)\
        .join(Session).filter(Session.promo_id != session.promo_id).all()

    candidates_list = []
    for student in students_previous:
        candidates_list.append(student.id)
    for student in students_in_other_promos:
        candidates_list.append(student.id)
    students_candidates = Student.query\
        .filter_by(branch_id=session.semester.branch_id)\
        .filter(Student.id.notin_(candidates_list))\
        .all()
    return students_candidates

# Note (security): can you change the id (post) and send it to another session ?????
@app.route('/session/<session_id>/add-student/', methods=['GET', 'POST'])
def student_session(session_id=0):
    students_from = request.form.getlist('from[]')
    students_to = request.form.getlist('to[]')

    if students_from != [] or students_to != []:
        msg = update_student_session(students_from, students_to, session_id)
        # re-initialize
        msg2 = init_all(session_id)
        flash(msg)
        return redirect(url_for('student_session', session_id=session_id))

    session = Session.query.filter_by(id=session_id).first()

    # students_previous = []
    students_previous = get_students_previous(session)
    # students_candidates = []
    # students_candidates = get_students_candidates(session, students_previous)
    students_candidates = get_students_candidates(session)
    # students_session = []
    students_session = Student.query.join(StudentSession).filter_by(session_id=session_id).all()

    return render_template('session/multiselect.html', 
        title='Session',
        students_previous=students_previous,
        students_candidates=students_candidates,
        students_session=students_session,
        session_id=session_id
      )

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
    grade_units = student_session.grades_unit
    row = ''
    for grade_unit in grade_units:
        row += get_row_unit(grade_unit, cols_per_module)

    row += F'<td class="semester right">{student_session.average}</td>'
    if cols_per_module >= 2:
        row += F'<td class="semester center">{student_session.credit}</td>'
    if cols_per_module == 3:
        row += F'<td class="semester center">{student_session.session_id}</td>'
    return row

@app.route('/session/<session_id>/semester-result-2/', methods=['GET', 'POST'])
def semester_result(session_id=0):
    session = Session.query.filter_by(id=session_id).first()
    cols_per_module = 2
    header = get_thead(session.configuration, cols_per_module)

    data_arr = []
    students_session = StudentSession.query.filter_by(session_id=session_id).all()
    for index, student_session in enumerate(students_session, start=1):
        student = student_session.student
        _std = F'<td>{index}</td><td>{student.username}</td><td>{student.first_name} - {student.last_name}</td>'
        row = _std + get_row_semester(student_session, cols_per_module)
        data_arr.append(row)
    return render_template('session/semester-result-2.html', title='Semester Result 2', 
        header=header, data_arr=data_arr, session_id=session_id)





@app.route('/session/<session>/module/<module>/<_all>/', methods=['GET', 'POST']) 
@app.route('/session/<session>/module/<module>/', methods=['GET', 'POST'])
@app.route('/session/<session>/student/<student>/<_all>/', methods=['GET', 'POST'])
@app.route('/session/<session>/student/<student>/', methods=['GET', 'POST'])
def grade(session=0, module=0, student=0, _all=''):
    grades = None
    if session == 0:
        type = 'module'
        grades = Grade.query.all()
    else:
        if module != 0:
            type = 'module'
            grades = Grade.query.filter_by(module_id=module)\
                .join(StudentSession).filter_by(session_id=session)\
                .all()
        if student != 0:
            type = 'student'
            grades = Grade.query\
                .join(StudentSession).filter_by(session_id=session, student_id=student)\
                .all()

    ### Initialize the Columns
    # cols = get_visible_cols(grades, type, _all)
    data = create_data_grid(grades, type)

    grid_title = ''
    if module!=0:
        module = Module.query.filter_by(id=module).first()
        grid_title = F'Module: {module.display_name}'
    if student!=0:
        student = Student.query.filter_by(id=student).first()
        grid_title = F'Student: {student.username} - {student.first_name} - {student.last_name}'

    return render_template('grade/grid.html', title='Grade Edit', 
        data=data, 
        _all=_all.lower(), 
        grid_title=grid_title, 
        type=type)

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
        formula = "formula: " + str(grade.formula).replace('None', '') + " "

        data += "{" + grade_id + name + cour + td + tp + t_pers + stage \
             + average + credit + formula + "}, "
 
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

# def get_next_semester(semester_id):
#     next_semester = Semester.query.filter_by(prev_semester=semester_id).first()
#     return next_semester.id


# WARNING: i have to check before i delete
# check that the session is not closed
@app.route('/session/<session_id>/delete-session/', methods=['GET', 'POST'])
def delete_session(session_id):
    session = Session.query.filter_by(id=session_id).first_or_404()
    sessions_chain = session.get_chain()

    school_id = session.promo.branch.school_id
    branch_id = session.promo.branch_id
    promo_id = session.promo_id

    # don't allow deletion if it is not the last one
    if session.get_next() is not None:
        flash("you can't delete this session because it not the last one")
        return redirect(url_for('session', session_id=session.id))

    if session.is_closed is True:
        flash('Session ('+str(session_id)+') was not deleted because it is Closed')
    else:
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

    # if Rattrapage exist -> it is next
    return session

@app.route('/session/<session_id>/students-rattrapage/', methods=['GET', 'POST'])
def students_rattrapage(session_id=0):
    students = StudentSession.query\
        .filter_by(session_id=session_id)\
        .filter(or_(StudentSession.credit<30, StudentSession.credit == None))\
        .all()
    return render_template('session/students-rattrapage.html', title='students-rattrapage', students=students, session_id=session_id)

def init_student_rattrapage(session, rattrapage):
    students_session = StudentSession.query.filter_by(session_id=session.id)\
        .filter(or_(StudentSession.credit<30, StudentSession.credit==None))\
        .all()
    students_rattrapage = StudentSession.query.filter_by(session_id=rattrapage.id).all()
    std_sess = []
    std_ratt = []
    for student_sess in students_session:
        std_sess.append(student_sess.id)
    for student_ratt in students_rattrapage:
        std_ratt.append(student_ratt.id)

    # for student_sess in students_session:
    #     new_student_session = StudentSession(session_id=student_sess.session_id, student_id=student_sess.student_id)
    #     student_rattrapage = StudentSession.query.filter_by(*********).first()
    #     if student_rattrapage is None:
    #         db.session.add(student_session)
    db.session.commit()
    # init_grages_rattrapage()
    

@app.route('/session/<session_id>/create-rattrapage/', methods=['GET', 'POST'])
def create_rattrapage_session(session_id=0):
    session = Session.query.filter_by(id=session_id).first()
    rattrapage = create_rattrapage(session_id)
    if session == rattrapage:
        flash('Rattrapage (' + str(rattrapage.semester.semester) + ') already exists')
    else:
        flash('created Rattrapage (' + str(rattrapage.semester.semester) + ')')

    # transfer student to Ratt session
    if rattrapage != None:
        init_student_rattrapage(session, rattrapage)
    # redirect to the created session
    return redirect(url_for('session', session_id=rattrapage.id))

@app.route('/create-session/promo/<promo_id>/semester/<semester_id>/', methods=['GET', 'POST'])
def create_session(promo_id=0, semester_id=0):
    sessions = Session.query.filter_by(promo_id=promo_id, semester_id=semester_id).all()

    if len(sessions) > 0:
        # raise Exception("already exists")
        # check if the session of this simester exists
        already_created_session = Session.query.filter_by(promo_id=promo_id, semester_id=semester_id).first()
        if already_created_session is not None:
            flash('Session (' + str(already_created_session.semester.get_nbr()) + ') already exist')
            school_id = already_created_session.promo.branch.school_id
            branch_id = already_created_session.promo.branch_id
            promo_id = already_created_session.promo_id
            return redirect( url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id) )

    session = Session(promo_id=promo_id, semester_id=semester_id)
    db.session.add(session)
    db.session.commit() # can i remove this

    init_annual_session_id(session.id)
    
    flash('Session (' + str(session.semester.get_nbr()) + ') created')
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

@app.route('/session/<session_id>/create_next_session/', methods=['GET', 'POST'])
def create_next_session(session_id):
    session = Session.query.filter_by(id=session_id).first_or_404()
    next_semester = session.semester.get_next()
    if next_semester is None:
        flash('Semester (' + str(session.semester.get_nbr()) + ') is the last semester')
        return redirect(url_for('session', session_id=session.id))
    next_semester_id = next_semester.id
    return redirect(url_for('create_session', promo_id=session.promo_id, semester_id=next_semester_id))




# ----------------------
# ----------------------
# ----------------------


@app.route('/annual-session/<annual_session_id>/', methods=['GET', 'POST'])
def annual_session(annual_session_id=0):
    annual_session = AnnualSession.query.filter_by(id=annual_session_id).first_or_404()
    
    # units = session.semester.units
    modules_list = []
    icons_module = []
    icons_student = []

    # for unit in units:
    #     modules = unit.modules
    #     for module in modules:
    #         modules_list.append(module)
    #         icon = get_icon_progress_module(session_id, module.id)
    #         icons_module.append(icon)

    # students_list = Student.query.join(StudentSession).filter_by(session_id=session_id).all()
    students_list = []
    # for student in students_list:
    #     icon = get_icon_progress_student(session_id, student.id)
    #     icons_student.append(icon)

    # session.name = make_session_name(session)

    return render_template('session/annual-session.html', 
        title='Annual Session', annual_session=annual_session,
        students=students_list, modules=modules_list,
        icons_module=icons_module, icons_student=icons_student)
    # return render_template('session/annual-session.html', 
    #     title='Annual Session', annual_session=annual_session)


@app.route('/annual-session/<annual_session_id>/delete-session/', methods=['GET', 'POST'])
def delete_annual_session(annual_session_id):
    return 'delete_annual_session: ' + str(annual_session_id)

@app.route('/annual-session/<session_id>/create_annual_session/', methods=['GET', 'POST'])
def create_annual_session(session_id):
    annual_session_id = None
    promo_id = None
    chain = Session.query.get(session_id).get_annual_chain()
    for ch in chain:
        session = Session.query.get(ch)
        if session.annual_session_id != None:
            annual_session_id = session.annual_session_id
            promo_id = session.promo_id
            break

    # check the existance of the record
    annual_session = AnnualSession.query.filter_by(id=annual_session_id).first()
    if annual_session_id != None and annual_session == None:
        raise Exception('the AnnualSession:' + str(annual_session_id) + ' does not exist')

    if annual_session == None:
        annual_session = AnnualSession(name="ddd", promo_id=promo_id)
        db.session.add(annual_session)
        db.session.commit()
        annual_session_id = annual_session.id

    init_annual_session_id(session.id, annual_session_id)
    return 'create_annual_session: ' + str(session_id)


# ----------------------
# ----------------------
# ----------------------


@app.route('/session/<session_id>/relation/', methods=['GET', 'POST'])
def show_relation(session_id=0):
    session = Session.query.filter_by(id=session_id).first()

    semesters = '*semesters*'
    sessions = '*sessions*'
    annual_semester = '*annual_semester*'
    annual_session = '*annual_session*'
    annual_dict = '*annual_dict*'
    previous = '*previous*'

    semesters = str(session.semester.get_chain())
    sessions = str(session.get_chain())
    annual_semester = str(session.semester.get_annual_chain())
    annual_session = str(session.get_annual_chain())
    annual_dict = str(session.get_annual_dict())
    previous = str(session.get_previous().id)

    return  'Semester ('+str(session.semester.id)+') chain: <br>' + semesters +\
        '<br><br>Session ('+str(session.id)+') chain: <br>' + sessions +\
        '<br><br><br>Annual ('+str(session.semester.annual )+') semester_id chain: <br>' + annual_semester +\
        '<br><br>Annual ('+str(session.semester.annual )+') session_id chain: <br>' + annual_session +\
        '<br><br>Annual ('+str(session.semester.annual )+') session_id dict: <br>' + annual_dict +\
        '<br><br>Previous of ('+str(session_id)+'): ' + previous


# ----------------------


#
## PDF 
#  


@app.route('/session/<session_id>/semester-result-3/<_id>/', methods=['GET', 'POST'])
def semester_result3(session_id=0, _id=0):
    session = Session.query.filter_by(id=session_id).first()
    cols_per_module = 2
    header = get_thead(session.configuration, cols_per_module)

    data_arr = []
    i = 0
    students_session = StudentSession.query.filter_by(session_id=session_id).all()
    count = 0
    while count < 15:
        for index, student_session in enumerate(students_session, start=1):
            student = student_session.student
            i += 1
            _std = F'<td>{i}</td><td>{student.username}</td><td>{student.first_name} - {student.last_name}</td>'
            row = _std + get_row_semester(student_session, cols_per_module)
            data_arr.append(row)
        count += 1

    return render_template('session/semester-result-3.html', title='Semester Result 2', 
        header=header, data_arr=data_arr, session_id=session_id, id=_id)

import pdfkit
from flask import send_file, send_from_directory
from flask import Response

# Flask-WeasyPrint
# https://pythonhosted.org/Flask-WeasyPrint/
# http://weasyprint.readthedocs.io/en/latest/install.html

'''
be carefull returning the file in the right version
it looks like if i change the file it keeps returning the old one
it seems to work right when changing the URL
'''
@app.route('/pdf/<id>/')
def your_view(id=0):
    options = {
        'orientation': 'landscape'
    }
    url = 'http://localhost:5001/session/2/semester-result-3/'+str(id)+'/'
    # url = 'http://localhost:5001/session/2/'
    wkhtmltopdf_path = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
    pdf = pdfkit.from_url(url, 'app\\pdf\\out.pdf', configuration=config, options=options)

    # filename = '..\\out.pdf'
    filename = 'out.pdf'

    return send_from_directory('pdf', filename)
    
    # return send_file(filename, mimetype='application/pdf', as_attachment=True)

    # @app.route('/return-files', methods=['GET'])
    # def return_file():
    #     return send_from_directory(directory='uploads', filename='g.mp4', as_attachment=True)

    # resp = Response(pdf)
    # resp.headers['Content-Disposition'] = "inline; filename=%s" % filename
    # resp.mimetype = 'application/pdf'
    # return resp

    # content = get_file('out.pdf')
    # return Response(content, mimetype="text/html")
    # return send_file('..\\out.pdf')
    # return send_from_directory(directory='', filename='out.pdf')
    return '123'


#
#
#  
#
