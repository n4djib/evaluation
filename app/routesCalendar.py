from app import app, db
from flask import render_template, jsonify, request
from app.models import School, Branch, Semester, Module, Promo,\
     Session, ModuleSession, Attendance, ModuleCalendar, Student

from datetime import datetime



@app.route('/select-list/api/event/<event_id>')
@app.route('/select-list/api/event/<event_id>/session/<session_id>')
def select_list_calendar_api(event_id=0, session_id=0):
    module_calendar = ModuleCalendar.query.get(event_id)

    if module_calendar == None:
        return 'Event Not Found ...'

    module_id = 0
    module_session = module_calendar.module_session

    if module_session != None:
        module_id = module_session.module.id

    if session_id != 0:
        return select_list_calendar(session_id=session_id, module_id=module_id, event_id=event_id)

    if module_session == None:
        # return 'No module_session is related (event: '+str(event_id)+')'
        return select_list_calendar(0, 0, 0, 0, 0, 0)

    sessions = Session.query.filter_by(
        promo_id=module_session.promo_id, 
        semester_id=module_session.module.unit.semester_id
    ).all()

    if len(sessions) != 1:
        raise Exception('it should return only one session')

    session_id = sessions[0].id
    module_id = module_session.module.id

    # html = select_list_calendar(0, 0, 0, session_id, module_id)
    html = select_list_calendar(0, 0, 0, session_id, module_id, event_id)
    return html




@app.route('/save-select-list', methods=['POST'])
def save_select_list_calendar():
    data = request.get_json(force=True) 
    print(' ')
    print( str(data) )
    print(' ')

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

    module_calendar = ModuleCalendar.query.get_or_404(event_id)
    module_session = module_calendar.module_session
    print('------')
    print('------')
    if module_session == None and promo_id != 0 and module_id != 0:
        module = Module.query.get_or_404(module_id)
        module_session = ModuleSession(
            promo_id=promo_id,
            module_id=module_id,
            module_code=module.code,
            module_name=module.name
        )

        db.session.add(module_session)
        db.session.commit()
        module_calendar.module_session_id = module_session.id
        db.session.commit()
        print('++++++ ' + str(module))
        print('++++++ ' + str(module_session.id))
        print('++++++ ' + str(module_session.module_code))
        print('++++++ ' + str(module_calendar.module_session_id))


    if module_session != None and promo_id != 0 and module_id != 0:
        module = Module.query.get_or_404(module_id)
        module_session.module_id = module_id
        module_session.module_code = module.code
        module_session.module_name = module.name
        db.session.commit()

    return 'save_select_list_calendar'


@app.route('/select-list/')
@app.route('/select-list/promo/<promo_id>') ###########################
@app.route('/select-list/school/<school_id>')
@app.route('/select-list/branch/<branch_id>')
@app.route('/select-list/session/<session_id>') ###########################
# @app.route('/select-list/school/<school_id>/module/<module_id>')
# @app.route('/select-list/branch/<branch_id>/module/<module_id>')
# @app.route('/select-list/promo/<promo_id>/module/<module_id>')
@app.route('/select-list/session/<session_id>/module/<module_id>') ########
@app.route('/select-list/session/<session_id>/module/<module_id>/event/<event_id>')
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

    print(' ')
    print(str(module))
    print(str(module_id))
    print(' ')

    return render_template('attendance/select-list-module-calendar.html',
        school=school, branch=branch, promo=promo, session=session, module=module, event=event)



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


def init_attendance(module_calendar):
    module_session = module_calendar.module_session
    # if module_session != None:
    #     # promo = Session.query.filter_by(promo_id=module_session.promo_id).first()
    #     promo = module_session.promo


def init_module_session(module_calendar):
    module_session = module_calendar.module_session
    # if module_session != None:
    #     pass






# @app.route('/attendance/session/<session_id>/module/<module_id>/')
# def attendance(session_id, module_id):
#     session = Session.query.get_or_404(session_id)
#     module = Module.query.get_or_404(module_id)

#     # init_attendance(session, module)

#     attendances = Attendance.query.join(ModuleCalendar)\
#         .join(ModuleSession).filter_by(promo_id=session.promo_id, module_id=module_id)\
#         .all()
#     return render_template('attendance/attendance.html', 
#         attendances=attendances)

@app.route('/attendance/calendar/<calendar_id>')
def attendance(calendar_id=0):
    # init_attendance(module_calendar)

    module_calendar = ModuleCalendar.query.get_or_404(calendar_id)
    
    init_module_session(module_calendar)
    init_attendance(module_calendar)

    attendances = module_calendar.attendances

    return render_template('attendance/attendance.html', 
        attendances=attendances)


@app.route('/calendar')
@app.route('/calendar/session/<session_id>')
def calendar(session_id=0):
    return render_template('attendance/calendar.html', session_id=session_id)

def generate_modal(event_id):
    event = ModuleCalendar.query.get(event_id)
    return '<h1>Modal for Event id: '+str(event.id)+'</h1>'

@app.route('/load-event-calendar')
def load_event():
    events = ModuleCalendar.query.all()
    # return str( len(events) )
    # return str( events[0].id )

    data = []
    for event in events:
        module_session = event.module_session
        title = 'Untitled'
        if module_session != None:
            module = module_session.module
            if module != None:
                title = module.code + ' - ' + module.name

        data += [{
            'id': event.id,
            # 'title': event.name,
            'title': title,
            'start': event.start_event.strftime('%Y-%m-%d %H:%M:%S'),
            'end': event.end_event.strftime('%Y-%m-%d %H:%M:%S'),
            # 'description': 'description for Long Event',
            'color': 'lightgreen',
            'type': '1',
            'modalContent': generate_modal(event.id),
            # rendering: 'background'
        }]
    
    return jsonify(data)

@app.route('/insert-event-calendar', methods=['POST'])
def insert_event():
    # data = request.json
    data = request.get_json(force=True) 

    # print('-------1--------')
    # print('-------2--------')
    # print( str(data['start']) )
    # print( type(data['start']) )
    # print( type( datetime.strptime(data['start'], "%Y-%m-%d %H:%M:%S")  ) )
    # print('-------3--------')
    # print('-------4--------')

    event = ModuleCalendar(
        # module_session_id=*****,
        name=data['title'],
        start_event=datetime.strptime(data['start'], "%Y-%m-%d %H:%M:%S"),
        end_event=datetime.strptime(data['end'], "%Y-%m-%d %H:%M:%S"),
    )
    # title, start:start, end:end
    db.session.add(event)
    db.session.commit()

    return 'event inserted'

@app.route('/update-event-calendar', methods=['POST'])
def update_event():
    data = request.get_json(force=True) 
    event = ModuleCalendar.query.get( data['id'] )
    
    event.name = data['title']
    event.start_event = datetime.strptime(data['start'], "%Y-%m-%d %H:%M:%S")
    event.end_event = datetime.strptime(data['end'], "%Y-%m-%d %H:%M:%S")
    db.session.commit()

    return 'updated'

# @app.route('/update-event-calendar-and-module', methods=['POST'])
# def update_event_and_module():
#     data = request.get_json(force=True) 
#     event = ModuleCalendar.query.get( data['id'] )
    
#     event.name = data['title']
#     event.start_event = datetime.strptime(data['start'], "%Y-%m-%d %H:%M:%S")
#     event.end_event = datetime.strptime(data['end'], "%Y-%m-%d %H:%M:%S")
#     db.session.commit()

#     return 'updated'


@app.route('/delete-event-calendar', methods=['POST'])
def delete_event():
    data = request.get_json(force=True) 

    print('-------1--------')
    print( str(data) )
    print('-------2--------')
    print( str(data['id']) )
    print('-------3--------')
    print('-------4--------')

    event = ModuleCalendar.query.get( data['id'] )
    db.session.delete(event)
    db.session.commit()

    
    return 'removed'

