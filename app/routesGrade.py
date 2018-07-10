from app import app, db
from flask import render_template, request, jsonify, redirect, url_for, flash
from app.models import Session, StudentSession, Grade, Unit, Semester, School, Module, Student
# from flask_breadcrumbs import register_breadcrumb
from decimal import *

from ast import literal_eval
from app.routesCalculation import config_to_dict, init_all


def get_year(promo):
    # return one (last)
    sessions = Session.query.filter_by(promo_id=promo.id)\
        .join(Semester).order_by('year desc', Semester.semester, Session.start_date)\
        .all()
    for session in sessions:
        return session.semester.year
    return '***'

def get_sessions_tree(promo):
    ## order_by start_date
    ## later order by Previous
    # sessions = promo.sessions
    sessions = Session.query.filter_by(promo_id=promo.id).join(Semester)\
        .order_by('year', Semester.semester, Session.start_date)\
        .all()
        # it would be better if i order by Previous

    sessions_tree = ''
    for session in sessions:
        name = ''
        # semester = session.semester.display_name
        semester = str(session.semester.get_nbr())
        prev_session = str(session.prev_session).replace('None', '')
        if session.is_rattrapage:
            name = 'Rattrapage: ' + semester + '        s: ' + str(session.id) + ' - p: ' + prev_session
        else:
            name = 'Semester: ' + semester + '        s: ' + str(session.id) + ' - p: ' + prev_session

        id = str(session.id)
        pId = 'promo_'+str(promo.id)
        url = '/session/'+str(session.id)

        # name = '<span style=font-size:20px;>' + name + '</span>'
        
        if session.is_closed == True:
            p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, url: "'+url+'", iconSkin:"icon13"},'
        else:
            p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, url: "'+url+'"},'

        sessions_tree = sessions_tree + p
    sessions_tree += get_creation_links( str(promo.id), 'promo_'+str(promo.id) )
    return sessions_tree

def get_creation_links(id, pId):
    ret =  '{id:"d_'+id+'", pId:"'+pId+'", name:" "},'
    ret +=  '{id:"a_'+id+'", pId:"'+pId+'", name:"       123", iconSkin:"icon01"},'
    ret += '{id:"b_'+id+'", pId:"'+pId+'", name:"       456", iconSkin:"icon01"},'
    ret += '{id:"c_'+id+'", pId:"'+pId+'", name:"       789", iconSkin:"icon01"},'
    return ret

def get_promos_tree(branch):
    promos = branch.promos
    promos_tree = ''
    for promo in promos:
        id = 'promo_'+str(promo.id)
        pId = 'branch_'+str(branch.id)
        name = ' ' + promo.display_name + ' (' + str(get_year(promo)) + ' Année)'
        s = get_sessions_tree(promo)
        font = '{"font-weight":"bold", "font-style":"italic"}'
        icon = 'pIcon15'
        if s=='':
            icon='icon15'
        p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, iconSkin:"'+icon+'", font:'+font+'},'
        promos_tree += p + s 
    return promos_tree

def get_branchs_tree(school):
    branches = school.branches
    branches_tree = ''
    for branch in branches:
        id = 'branch_'+str(branch.id)
        pId = 'school_'+str(school.id)
        p = get_promos_tree(branch)
        if p == '':
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+branch.name+'", open:true, iconSkin:"icon11"},'
        else:
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+branch.name+'", open:true, isParent:true},'
        
        branches_tree += b + p
    return branches_tree

def get_schools_tree():
    schools = School.query.all()
    schools_tree = ''
    for school in schools:
        id = 'school_'+str(school.id)
        icon = 'pIcon12'
        s = '{ id:"'+id+'", pId:0, name:"'+school.name+'", open:true, iconSkin:"'+icon+'", isParent:true },'
        b = get_branchs_tree(school)
        schools_tree += s + b
    return schools_tree

# @app.route('/tree/school/<school_id>/branch/<branch_id>/', methods=['GET', 'POST'])
# @app.route('/tree/school/<school_id>/', methods=['GET', 'POST'])
@app.route('/tree/', methods=['GET', 'POST'])
# @register_breadcrumb(app, '.tree', 'Tree')
def tree(school_id=0, branch_id=0):
    zNodes = '['+get_schools_tree()+']'
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
    # grades_is_empty = False

    for grade in grades:
        # grades_is_empty = True
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

    # if grades_is_empty == False:
    #     return '(re)Init'

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
    session = Session.query.filter_by(id=session_id).first()
    students = Student.query.join(StudentSession).filter_by(session_id=session_id).all()

    units = session.semester.units
    modules_list = []
    icons_module = []
    for unit in units:
        modules = unit.modules
        for module in modules:
            modules_list.append(module)
            icon = get_icon_progress_module(session_id, module.id)
            # return "dddd"
            icons_module.append(icon)

    
    icons_student = []
    for student in students:
        icon = get_icon_progress_student(session_id, student.id)
        icons_student.append(icon)

    return render_template('session/session.html', 
        title='Session', 
        students=students,
        modules=modules_list,
        icons_module=icons_module,
        icons_student=icons_student,
        session_id=session_id,
        session=session
      )


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
            # db.session.commit()
            # add_student_to_grade(session, select)
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
        .filter_by(session_id=session.prev_session).all()
    return students_previous

def get_students_candidates(students_previous, session):
    # I HAVE TO FIND ONLY THE ONES WITHOUT A SESSION
    candidates_list = []
    for student in students_previous:
        candidates_list.append(student.id)
    students_candidates = Student.query.filter_by(branch_id=session.semester.branch_id).filter(Student.id.notin_(candidates_list)).all()

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

    students_previous = get_students_previous(session)
    students_candidates = get_students_candidates(students_previous, session)
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
#

def get_th_1(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th>Unit</th>'
    for unit in conf_dict['units']:
        unit_name = unit['display_name'] + " ("+ str(unit['coeff']) + ")"
        colspan = cols_per_module
        for module in unit['modules']:
            colspan += cols_per_module
        header += '<th class="unit" colspan='+str(colspan)+'><center>' + unit_name + '</center></th>'
    return header + '<th class="semester" rowspan=4 colspan='+str(cols_per_module)+'><center>' + conf_dict["display_name"] + '</center></th>'

def get_th_2(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th>Module</th>'
    for unit in conf_dict['units']:
        for module in unit['modules']:
            header += '<th colspan='+str(cols_per_module)+'><center>' + module['display_name'] + '</center></th>'
        name = "Result of " + unit['display_name'] 
        # table = "<table>  <tr><td>" + str(unit['unit_coeff']) + "</td></tr>  <tr><td>" + str(unit['coeff']) + "</td></tr>  </table>"
        table = ""
        header += '<th class="unit" rowspan=3 colspan='+str(cols_per_module)+'><center>' + name + table + '</center></th>'
    return header

def get_th_3(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th>Required Credit</th>'
    for unit in conf_dict['units']:
        for module in unit['modules']:
            header += '<th colspan='+str(cols_per_module)+'><center>' + str(module['credit']) + '</center></th>'
    return header

def get_th_4(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th>Coefficient</th>'
    for unit in conf_dict['units']:
        for module in unit['modules']:
            header += '<th colspan='+str(cols_per_module)+'><center>' + str(module['coeff']) + '</center></th>'
    return header

def get_th_5(configuration, cols_per_module):
    conf_dict = literal_eval(configuration)
    header = '<th class="header5">N°</th><th class="header5">Username</th><th class="header5">Full Name</th>'

    average = 'A'
    credit = 'C'
    session = 'S'

    th_module = '<th class="header5"><center>' + average + '</center></th>'
    th_unit = '<th class="unit"><center>' + average + '</center></th>'
    th_semester = '<th class="semester"><center>' + average + '</center></th>'

    if cols_per_module >= 2:
        th_module += '<th class="header5"><center>' + credit + '</center></th>'
        th_unit += '<th class="unit"><center>' + credit + '</center></th>'
        th_semester += '<th class="semester"><center>' + credit + '</center></th>'
    if cols_per_module == 3:
        th_module += '<th class="header5"><center>' + session + '</center></th>'
        th_unit += '<th class="unit"><center>' + session + '</center></th>'
        th_semester += '<th class="semester"><center>' + session + '</center></th>'
    
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

    return """
        <tr>
          <th style='border: 0;'  colspan=2 rowspan=4></th>
          """ + th_1 + """
        </tr>
        <tr>
          """ + th_2 + """
        </tr>
        <tr>
          """ + th_3 + """
        </tr>
        <tr>
          """ + th_4 + """
        </tr>
        <tr>
          """ + th_5 + """
        </tr>
    """


def get_row_module(grade, cols_per_module):
    average = str(grade.average).replace('None', '')
    credit = str(grade.credit).replace('None', '')

    row = '<td class="right">'+average+'</td>'
    if cols_per_module >= 2:
        row += '<td class="center">'+credit+'</td>'
    if cols_per_module == 3:
        row += '<td class="center">'+'**'+'</td>'
    return row

def get_row_unit(grade_unit, cols_per_module):
    grades = grade_unit.student_session.grades
    row = ''
    for grade in grades:
        # get only the grades in unit
        if grade.module.unit_id == grade_unit.unit_id:
            row += get_row_module(grade, cols_per_module)

    average = str(grade_unit.average).replace('None', '')
    credit = str(grade_unit.credit).replace('None', '')

    row += '<td class="unit right">'+average+'</td>'
    if cols_per_module >= 2:
        row += '<td class="unit center">'+credit+'</td>'
    if cols_per_module == 3:
        row += '<td class="unit center">'+'**'+'</td>'
    return row

def get_row_semester(student_session, cols_per_module=2):
    grade_units = student_session.grades_unit
    row = ''
    for grade_unit in grade_units:
        row += get_row_unit(grade_unit, cols_per_module)

    average = str(student_session.average).replace('None', '')
    credit = str(student_session.credit).replace('None', '')

    row += '<td class="semester right">'+average+'</td>'
    if cols_per_module >= 2:
        row += '<td class="semester center">'+credit+'</td>'
    if cols_per_module == 3:
        row += '<td class="semester center">'+str(student_session.session_id)+'</td>'
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
        username = student.username
        name = student.first_name + ' - ' + student.last_name
        _std = '<td>'+str(index)+'</td>  <td>'+username+'</td>  <td>'+name+'</td>'
        row = _std + get_row_semester(student_session, cols_per_module)
        data_arr.append(row)

    return render_template('session/semester-result-2.html', title='Semester Result 2', 
        header=header, data_arr=data_arr, session_id=session_id)

#
#
#
#

@app.route('/session/<session>/module/<module>/<_all>/', methods=['GET', 'POST']) 
@app.route('/session/<session>/module/<module>/', methods=['GET', 'POST'])
@app.route('/session/<session>/student/<student>/<_all>/', methods=['GET', 'POST'])
@app.route('/session/<session>/student/<student>/', methods=['GET', 'POST'])
# @register_breadcrumb(app, '.session .grade', 'Grade')
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
        grid_title = 'Module: ' + module.display_name
    if student!=0:
        student = Student.query.filter_by(id=student).first()
        grid_title = 'Student: ' + str(student.username) + ' - ' + student.first_name + ' - ' + student.last_name

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
#@login_required
def grade_save():
    data_arr = request.json
    for i, data in enumerate(data_arr, start=0):
        grade = Grade.query.filter_by(id = int(data['id'])).first()

        #
        #
        # saved fields must be according to the Permission
        #
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

def create_session(session_id, is_rattrapage=False):
    session = Session.query.filter_by(id=session_id).first()
    # create first

    # create with previous
    ### check if already exists
    previous_session = Session.query.filter_by(prev_session=session_id).first()
    if previous_session is None:
        new_session = Session(semester_id=session.semester_id, 
                              promo_id=session.promo_id, 
                              prev_session=session.id, 
                              is_rattrapage=is_rattrapage)
        db.session.add(new_session)
        db.session.commit()
        return 'create_next_session'
    return 'create_next_session already exists ' + str(previous_session.id)

@app.route('/session/<session_id>/create-next/', methods=['GET', 'POST'])
def create_next_session(session_id=0):
    # create next session

    ### check if already exists
    msg = create_session(session_id)
    flash(msg)

    # find students to pas to next session
    students_session = StudentSession.query.filter_by(session_id=session_id).all()

    # next_session = Session(semester_id=session.semester_id)

    return redirect(url_for('session', session_id=session_id))

@app.route('/session/<session_id>/create-rattrapage-session/', methods=['GET', 'POST'])
def create_rattrapage_session(session_id=0):
    return 'create_rattrapage_session'



# ----------------------

@app.route('/session/<session_id>/relation/', methods=['GET', 'POST'])
def show_relation(session_id=0):
    session = Session.query.filter_by(id=session_id).first()

    sessions = str(session.get_chain())
    semesters = str(session.semester.get_chain())

    return  'Session ('+str(session.id)+') chain: <br>' + sessions +\
     '<br><br>Semester ('+str(session.semester.id)+') chain: <br>' + semesters

