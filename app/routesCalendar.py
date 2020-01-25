from app import app
from flask import render_template
from app.models import School, Branch, Semester, Module, Promo,\
     Session, ModuleSession, Attendance, ModuleCalendar, Student



@app.route('/select-list/')
@app.route('/select-list/school/<school_id>')
@app.route('/select-list/branch/<branch_id>')
@app.route('/select-list/promo/<promo_id>')
@app.route('/select-list/session/<session_id>')
@app.route('/select-list/school/<school_id>/module/<module_id>')
@app.route('/select-list/branch/<branch_id>/module/<module_id>')
@app.route('/select-list/promo/<promo_id>/module/<module_id>')
@app.route('/select-list/session/<session_id>/module/<module_id>')
def select_list_calendar(school_id=0, branch_id=0, promo_id=0, session_id=0, module_id=0):
    school = branch = promo = session = module = None

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

    return render_template('select-list-module-calendar.html',
        school=school, branch=branch, promo=promo, session=session, module=module)


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
        if session.is_historic == True:
            continue
        html_options += '<option value="'+id+'">'+display_name+historic+'</option>'
    return html_options

@app.route('/select-options-module-by-session/<session_id>', methods=['GET'])
@app.route('/select-options-module-by-session/<session_id>/module/<module_id>', methods=['GET'])
def get_modules_by_session(session_id, module_id=0):
    session = Session.query.get_or_404(session_id)
    # modules = Module.query.join(ModuleSession)\
    #     .filter_by(session_id=session_id).order_by(Module.code).all()

    units = session.semester.units
    modules = []
    for unit in units:
        for mod in unit.modules:
            modules.append(mod)

    html_options = '<option value="">Select Module</option>'
    for module in modules:
        selected = ''
        if str(module.id) == str(module_id):
            selected = 'selected'
        html_options += '<option value="'+str(module.id)+'" '+selected+'>'+module.code+' - '+module.name+'</option>'
    return html_options




#########################################
#########################################
#########################################

@app.route('/attendance/session/<session_id>/module/<module_id>/')
def attendance(session_id, module_id):
    session = Session.query.get_or_404(session_id)
    attendances = Attendance.query.join(ModuleCalendar)\
        .join(ModuleSession).filter_by(promo_id=session.promo_id, module_id=module_id)\
        .all()
    return render_template('attendance.html', 
        session_id=session_id, module_id=module_id, attendances=attendances)


