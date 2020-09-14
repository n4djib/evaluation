from app import app, db
from flask import render_template, jsonify, request
from app.models import School, Branch, Annual, Semester, Module, Promo,\
     Session, ModuleSession, Attendance, ModuleCalendar, Student
from flask_breadcrumbs import register_breadcrumb
from app.permissions_and_rules import AttendancePermission


from datetime import datetime, timedelta



@app.route('/select-list/api/event/<event_id>/session/<session_id>')
def select_list_calendar_api(event_id, session_id):
    module_calendar = ModuleCalendar.query.get(event_id)

    print('')
    print('------ggggggg------')

    if module_calendar == None:
        return 'Event Not Found ...'

    print(module_calendar.id)
    module_id = 0
    module_session = module_calendar.module_session
    # print(module_session.id)
    print('')
    print('------------')
    print('')

    if module_session != None:
        module_id = module_session.module.id

    print('+++++++++++++')
    print('+++++++++++++')

    return select_list_calendar(session_id=session_id, module_id=module_id, event_id=event_id)


@app.route('/save-select-list', methods=['POST'])
def save_select_list_calendar():
    data = request.get_json(force=True)

    event_id = data['id']
    # school_id = data['school_id']
    # branch_id = data['branch_id']
    promo_id = data['promo_id']
    session_id = data['session_id']
    module_id = data['module_id']
    start_date = data['start_date']
    end_date = data['end_date']
    start_time = data['start_time']
    end_time = data['end_time']

    d_start = datetime.strptime(start_date, "%Y-%m-%d")
    t_start = datetime.strptime(start_time, "%H:%M")
    new_d_start = datetime(d_start.year, d_start.month, d_start.day, t_start.hour, t_start.minute)

    d_end = datetime.strptime(end_date, "%Y-%m-%d")
    t_end = datetime.strptime(end_time, "%H:%M")
    new_d_end = datetime(d_end.year, d_end.month, d_end.day, t_end.hour, t_end.minute)

    module_calendar = ModuleCalendar.query.get(event_id)
    if module_calendar == None:
        return 'ERROR: module_calendar: ' + str(event_id) + ' not found'
    
    module_session = module_calendar.module_session

    # save datetime
    module_calendar.start_event = new_d_start
    module_calendar.end_event = new_d_end
    db.session.commit()

    module = Module.query.get(module_id)
    promo = Promo.query.get(promo_id)

    if module == None or promo == None:
        return 'ERROR: module or promo not found'

    if module_session == None and promo_id != 0 and module_id != 0:
        session = Session.query.get_or_404(session_id)
        # module_session = ModuleSession(
        #     promo_id=promo_id, 
        #     module_id=module.id, 
        #     module_code=module.code, 
        #     module_name=module.name, 
        #     is_rattrapage=session.is_rattrapage
        # )
        # db.session.add(module_session)
        # db.session.commit()
        from app.routesGrade import create_module_session
        module_session = create_module_session(session, module)
        module_session.module_code = module.code
        module_session.module_name = module.name

    if module_session == None:
        return 'ERROR: module_session not found'

    # connect module_session
    module_calendar.module_session_id = module_session.id

    # changing module
    module_session.module_id = module_id
    module_session.module_code = module.code
    module_session.module_name = module.name
    db.session.commit()

    return 'save_select_list_calendar'


@app.route('/save-attendance', methods=['POST'])
def save_attendance():
    data_array = request.get_json(force=True)

    for data in data_array:
        attendance = Attendance.query.get(data['id'])
        attendance.attended = data['checked']

    db.session.commit()
    return 'save_attendance'


#######################
#######################
#######################
#######################

# @app.route('/select-list/session/<session_id>')
# @app.route('/select-list/session/<session_id>/module/<module_id>')
# @app.route('/select-list/session/<session_id>/module/<module_id>/event/<event_id>')
def select_list_calendar(school_id=0, branch_id=0, promo_id=0, session_id=0, module_id=0, event_id=0):
    school = branch = promo = session = module = None
    event = None

    if event_id != 0:
        event = ModuleCalendar.query.get_or_404(event_id)

    # from semester conclude annual and bring both semesters
    if session_id != 0:
        session = Session.query.get_or_404(session_id)
        promo_id = session.promo_id
    if promo_id != 0:
        promo = Promo.query.get_or_404(promo_id)
        branch_id = promo.branch_id
    if branch_id != 0:
        branch = Branch.query.get_or_404(branch_id)
        school_id = branch.school_id
    if school_id != 0:
        school = School.query.get_or_404(school_id)

    # if there is a session and a module is chosen
    if session != None and module_id != 0:
        module = Module.query.get_or_404(module_id)

    return render_template('attendance/select-list-module-calendar.html',
        school=school, branch=branch, promo=promo, session=session, 
        module=module, event=event)



def make_html_options(_list, name):
    html_options = '<option value="">Select '+name+'</option>'
    for l in _list:
        html_options += '<option value="'+str(l.id)+'">'+str(l.name)+'</option>'
    return html_options


@app.route('/select-options-schools', methods=['GET'])
def get_schools():
    schools = School.query.all()
    return make_html_options(schools, 'School')


@app.route('/select-options-branches-by-school/<school_id>', methods=['GET'])
def get_branches_by_school(school_id):
    school = School.query.get_or_404(school_id)
    return make_html_options(school.branches, 'Branch')


@app.route('/select-options-promos-by-branch/<branch_id>', methods=['GET'])
def get_promos_by_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    return make_html_options(branch.promos, 'Promo')


@app.route('/select-options-session-by-promo/<promo_id>', methods=['GET'])
def get_semesters_by_promo(promo_id):
    sessions = Session.query.filter_by(promo_id=promo_id)\
        .join(Semester).order_by(Semester.display_name, Session.timestamp).all()

    html_options = '<option value="">Select Semester</option>'
    for session in sessions:
        id = str(session.id)
        display_name = str(session.semester.display_name)
        historic = ' (historic)' if session.is_historic else ''
        rattrapage = ' (rattrapage)' if session.is_rattrapage else ''
        if session.is_historic == True:
            continue
        html_options += '<option value="'+id+'">'+display_name+historic+rattrapage+'</option>'
    return html_options


@app.route('/select-options-module-by-session/<session_id>', methods=['GET'])
@app.route('/select-options-module-by-session/<session_id>/module/<module_id>', methods=['GET'])
def get_modules_by_session(session_id, module_id=0):
    session = Session.query.get_or_404(session_id)

    units = session.semester.units
    modules = []
    for unit in units:
        for mod in unit.modules:
            modules.append(mod)

    html_options = ''
    ### if there is a module_session
    if module_id == 0:
        html_options += '<option value="">Select Module</option>'

    for module in modules:
        selected = ''
        if str(module.id) == str(module_id):
            selected = 'selected'
        html_options += '<option value="'+str(module.id)+'" '+selected+'>'+module.code+' - '+module.name+'</option>'
    return html_options


#########################################
#########################################
#########################################

def make_student_ids_list(attendances):
    student_ids = []
    for attendance in attendances:
        student_ids.append(attendance.student_id)

    return student_ids


def init_attendance(module_calendar):
    module_session = module_calendar.module_session

    if module_session == None:
        return

    # pin point the session
    semester = module_session.module.unit.semester

    session = Session.query.filter(Session.is_rattrapage==False)\
        .join(Semester).filter_by(semester=semester.semester)\
        .join(Annual).filter_by(annual=semester.annual.annual).first()

    # students in attendance
    attendances = module_calendar.attendances
    attendance_student_ids = make_student_ids_list(attendances)

    # add students to attendance
    student_sessions = session.student_sessions
    for ss in student_sessions:
        if ss.student_id not in attendance_student_ids:
            # add
            attendance = Attendance(
                module_calendar_id=module_calendar.id,
                student_id=ss.student_id
            )
            db.session.add(attendance)

    db.session.commit()

    # remove students from attendance
    # for attendance in attendances:

    return 'init_attendance'


@app.route('/attendance/calendar/<calendar_id>')
def attendance(calendar_id=0):
    module_calendar = ModuleCalendar.query.get_or_404(calendar_id)
    
    init_attendance(module_calendar)

    attendances = module_calendar.attendances

    return render_template('attendance/attendance.html', 
        attendances=attendances)


# def calendar_dlc(*args, **kwargs):
#     session_id = request.view_args['session_id']
#     session = Session.query.get_or_404(session_id)
#     nbr = session.semester.get_nbr()
#     text = 'Semester'
#     if session.is_rattrapage:
#         text = 'Rattrapage'
#     return [{'text': text+' ('+str(nbr)+')', 
#         'url': url_for('session', session_id=session_id)}]


# @app.route('/calendar')
@app.route('/calendar/session/<session_id>')
# @register_breadcrumb(app, '.tree_session.session.calendar', '***', dynamic_list_constructor=calendar_dlc)
@register_breadcrumb(app, '.tree_session.session.calendar', 'Calendar')
def calendar(session_id=0):
    permission = AttendancePermission(session_id)
    if not permission.check():
        return permission.deny()
    title = 'Calendar for ***'
    return render_template('attendance/calendar.html', title=title, session_id=session_id)


def generate_modal(event_id):
    event = ModuleCalendar.query.get(event_id)
    return '<h1>Modal for Event id: '+str(event.id)+'</h1>'


def modify_end_time(start_event, end_event):
    # if it falls into any knon combination of start and end time
    # 8:30 - 10:00    # 10:00 - 11:30
    # 13:30 - 15:00   # 15:00 - 16:30
    
    start = start_event.strftime('%H:%M')
    end = end_event.strftime('%H:%M')
    
    if (start == '08:30' and end == '10:00') \
        or (start == '10:00' and end == '11:30') \
        or (start == '13:30' and end == '15:00') \
        or (start == '15:00' and end == '16:30'):
        end_time = end_event - timedelta(minutes=2)
        return end_time

    return end_event


@app.route('/load-event-calendar')
def load_event():
    events = ModuleCalendar.query.all()

    data = []
    for event in events:
        module_session = event.module_session
        # title = '<Untitled>'
        title = ''
        if module_session != None:
            module = module_session.module
            if module != None:
                title = module.code + ' - ' + module.name

        color = 'lightgreen'
        if event.module_session == None:
            color = 'lightblue'

        event.end_event = modify_end_time(event.start_event, event.end_event)
        start_event = event.start_event.strftime('%Y-%m-%d %H:%M')
        end_event = event.end_event.strftime('%Y-%m-%d %H:%M')

        data += [{
            'id': event.id,
            'title': title,
            'start': start_event,
            'end': end_event,
            # 'description': 'description for Long Event',
            'color': color,
            'textColor': 'black',
            'type': '1',
            'modalContent': generate_modal(event.id),
            # rendering: 'background'
        }]
    
    return jsonify(data)


def calculate_diff(start, end, time_format):
    diff = datetime.strptime(end, time_format) - datetime.strptime(start, time_format)
    return diff.seconds / 60


@app.route('/insert-event-calendar', methods=['POST'])
def insert_event():
    data = request.get_json(force=True)

    time_format = "%Y-%m-%d %H:%M:%S" 

    # to avoid inserting events by one click (30 minutes)
    diff_seconds = calculate_diff(data['start'], data['end'], time_format)
    if diff_seconds == 30:
        return 'not inserted to avoid 30 minutes '

    start_event = datetime.strptime(data['start'], time_format)
    end_event = datetime.strptime(data['end'], time_format)

    module_calendar = ModuleCalendar(
        # module_session_id=*****,
        name=data['title'],
        start_event=start_event,
        end_event=end_event,
    )

    db.session.add(module_calendar)
    db.session.commit()

    return 'event inserted'


@app.route('/update-event-calendar', methods=['POST'])
def update_event():
    data = request.get_json(force=True) 
    event = ModuleCalendar.query.get( data['id'] )
    
    # print('55555555555555')
    # print('55555555555555')
    # print('55555555555555')
    event.name = data['title']
    event.start_event = datetime.strptime(data['start'], "%Y-%m-%d %H:%M:%S")
    event.end_event = datetime.strptime(data['end'], "%Y-%m-%d %H:%M:%S")
    # print('66666666666')
    db.session.commit()
    # print('----77777')

    return 'updated'


@app.route('/delete-event-calendar', methods=['POST'])
def delete_event():
    data = request.get_json(force=True) 

    # print('-------1--------')
    # print( str(data) )
    # print('-------2--------')
    # print( str(data['id']) )
    # print('-------3--------')
    # print('-------4--------')

    event = ModuleCalendar.query.get( data['id'] )
    db.session.delete(event)
    db.session.commit()
    
    return 'removed'
