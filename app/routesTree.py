from app import app, db, cache
from flask import render_template, url_for, redirect, request, flash
from app.models import School, Session, Annual, Semester, Promo, AnnualSession
from flask_breadcrumbs import register_breadcrumb
# from app.routesSession import is_config_changed
from datetime import datetime
from app.routesCalculation import init_all, calculate_all



def get_creation_links(promo, seperate=True):
    sessions = promo.sessions
    semesters = promo.branch.get_semesters_ordered()
    semesters = semesters[-1].get_latest_of_semesters_list()

    links = ''
    if len(semesters) > 0:
        first_semester_id = semesters[0].id

        id = 'new_' + str(promo.id)
        pId = 'promo_' + str(promo.id)
        url = url_for('create_session', promo_id=promo.id, semester_id=first_semester_id)

        if len(sessions) > 0:
            first_session = sessions[0]
            sessions_chain = first_session.get_chain()
            last_session_id = sessions_chain[-1]
            last_session = Session.query.get_or_404(last_session_id)

            name = ''

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
        else:
            name = 'Create First Semester'
            links += '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", target:"_top", url: "'+url+'", iconSkin:"icon01"},'
    return links

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
            # name = 'Annual '+str(session.semester.annual.annual)+' Results       (an:'+str(an_s_id)+')'
            name = 'Annual '+str(session.semester.annual.annual)+' Results'
            annual = '{id:"annual_'+str(an_s_id)+'", pId:"'+pId+'", url: "'+url+'", name:"'+name+'", target:"_self", iconSkin:"icon17"},'
    return annual

def get_percentage_progress(percentage):
    load = "load-green"
    # load = "load-gold"
    perc = str(percentage)
    if percentage < 10:
        # perc = " "+str(percentage)
        perc = str(percentage)

    if percentage <= 25:
        load = "load-red"
    elif percentage <= 65:
        load = "load-orange"
    elif percentage <= 99:
        load = "load-green-yellow"

    perc_width = 1.5 if percentage <= 2 else percentage

    progress = "  "
    progress += "<div class='ld noload' style='display: inline-block; height:70%; width:70%;'>"
    progress += "  <span class='ld loadtext'>"+perc+"%</span>"
    progress += "  <div class='"+load+"' "
    progress += "    style='height:100%; width:"+str(perc_width)+"%;' "
    progress += "    style='width:"+str(percentage)+"%; '></div>"
    progress += "</div>"

    return progress


@app.route('/get_async_sessions_by_promo/<promo_id>/', methods=['GET', 'POST'])
def get_async_sessions_by_promo(promo_id):
    promo = Promo.query.get_or_404(promo_id)
    return '[' + get_sessions_tree(promo) + ']'

def get_sessions_tree(promo):
    sessions = Session.query.filter_by(promo_id=promo.id).join(Semester).join(Annual)\
        .order_by(Annual.annual, Semester.semester).all()

    sessions_tree = ''
    for session in sessions:
        semester = session.semester.get_nbr()
        annual = str(session.annual_session_id)

        id = 'semester_'+str(session.id)
        pId = 'promo_'+str(promo.id)
        url = url_for('session', session_id=session.id)

        icon = 'icon21'
        if session.is_rattrapage == True:
            icon = 'icon22'

        name = "Semester: "+str(semester)+" "
        if semester < 10:
            name += "  "
        if session.is_rattrapage:
            name = 'Rattrapage: '+str(semester)

        if session.is_closed == True:
            name += " <span class='button icon13_ico_docu'></span> "
        else:
            name += "       "

        # progress
        if not session.is_closed:
            name += get_percentage_progress( session.check_progress() )
        else:
            name += "                                "

        name += " <span style='font-size: 0.1px;'>" + session.promo.get_label() + "</span>"

        # Configuration change
        if session.is_config_changed() and session.is_closed==False:
            name += "<span style='color: orange;''>        Configuration has changed, you need to Re(initialized)</span>"

        p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, url: "'+url+'", '
        p += 'target:"_self", iconSkin:"'+icon+'" },'

        sessions_tree += p + get_annual_session(session, pId)

    seperate = True
    if sessions_tree == '':
        seperate = False
    return sessions_tree + get_creation_links(promo, seperate)

def get_promos_tree(branch, open_p_id):
    promos = branch.promos
    promos_tree = ''

    for promo in promos:
        id = 'promo_' + str(promo.id)
        pId = 'branch_' + str(branch.id)

        name = promo.name
        promo_display_name = str(promo.display_name).replace('None', '')
        if promo_display_name != '':
            name += " - <span style='color: "+str(promo.color)+";'>" + promo_display_name + "</span>"

        name = name + ' (' + str(  promo.get_latest_annual() ) + ' Year)'

        font = '{"font-weight":"bold", "font-style":"italic"}'
        icon = 'pIcon15'

        open = 'false'
        if open_p_id == 0:
            open = 'true'
        if open_p_id > 0:
            open = 'false'
            if open_p_id == promo.id:
                open = 'true'

        sessions_tree = ''
        if open == 'true':
            # promo_name = promo.name + ' ' + promo_display_name
            # sessions_tree = get_sessions_tree(promo, promo_name)
            sessions_tree = get_sessions_tree(promo)


        p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", times:1, isParent:true, open:'+open+', iconSkin:"'+icon+'", font:'+font+'},'
        promos_tree += p + sessions_tree

    return promos_tree

def get_branches_tree(school, open_b_id, open_p_id):
    branches = school.branches
    branches_tree = ''
    for branch in branches:
        id = 'branch_'+str(branch.id)
        pId = 'school_'+str(school.id)
        name = branch.name+' - '+str(branch.description)
        p = get_promos_tree(branch, open_p_id)

        open = 'true'
        if open_b_id != 0:
            open = 'false'
            if open_b_id == branch.id:
                open = 'true'
        if p == '':
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:'+open+', iconSkin:"icon11"},'
        else:
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:'+open+', isParent:true},'
        
        branches_tree += b + p

        ##################
        # break
        ##################


    return branches_tree


def get_schools_tree(open_s_id, open_b_id, open_p_id):
    schools = School.query.all()
    schools_tree = ''
    for school in schools:
        id = 'school_'+str(school.id)
        icon = 'pIcon12'
        branches_tree = get_branches_tree(school, open_b_id, open_p_id)
        open = 'true'
        if open_s_id != 0:
            open = 'false'
            if open_s_id == school.id:
                open = 'true'
        s = '{ id:"'+id+'", pId:0, name:"'+school.name+'", open:'+open+', iconSkin:"'+icon+'", isParent:true },'
        schools_tree += s + branches_tree
    return schools_tree

# @cache.cached(timeout=500)
# def get_schools_tree_cached(open_s_id, open_b_id, open_p_id):
#     return get_schools_tree(open_s_id, open_b_id, open_p_id)


def tree_dlc(*args, **kwargs):
    session_id = request.view_args['session_id']
    session = Session.query.get_or_404(session_id)

    school_id = 0
    branch_id = 0
    promo_id = 0
    if session != None:
        promo_id = session.promo_id
        branch_id = session.promo.branch_id
        school_id = session.promo.branch.school_id

    return [{'text': 'Tree ('+ session.promo.name +')', 
        'url': url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id) }]

@app.route('/tree/session/<session_id>/', methods=['GET'])
@register_breadcrumb(app, '.tree', '', dynamic_list_constructor=tree_dlc)
def tree_(session_id=0):
    return '*** just used to generate the url ***'


def annual_tree_dlc(*args, **kwargs):
    annual_session_id = request.view_args['annual_session_id']
    annual_session = AnnualSession.query.get_or_404(annual_session_id)
    session = annual_session.sessions[0]

    school_id = 0
    branch_id = 0
    promo_id = 0
    if session != None:
        promo_id = session.promo_id
        # branch_id = session.promo.branch_id
        school_id = session.promo.branch.school_id

    return [{'text': 'Tree ('+ session.promo.name +')', 
        'url': url_for('tree', school_id=school_id, branch_id=branch_id, promo_id=promo_id) }]

@app.route('/annual-tree/annual-session/<annual_session_id>/', methods=['GET'])
@register_breadcrumb(app, '.annual_tree', '', dynamic_list_constructor=annual_tree_dlc)
def annual_tree_(annual_session_id=0):
    return '*** just used to generate the url-annual-session ***'


@app.route('/tree/school/<school_id>/branch/<branch_id>/promo/<promo_id>/', methods=['GET'])
@app.route('/tree/school/<school_id>/branch/<branch_id>/', methods=['GET'])
@app.route('/tree/school/<school_id>/', methods=['GET'])
@app.route('/tree/', methods=['GET'])
@register_breadcrumb(app, '.tree_', 'Tree')
def tree(school_id=0, branch_id=0, promo_id=-1):
    options_arr = get_options()
    nbr_reinit_needed = check_reinit_needed()
    # nbr_reinit_needed = 1
    if nbr_reinit_needed > 0:
        reinit_url = url_for('tree_reinit_all')
        slow_redirect_url = url_for('slow_redirect', url=reinit_url, message='(Re)initializing ' + str(nbr_reinit_needed) + ' sessions')
        btn = '<a id="re-init-all" class="btn btn-warning" href="'+slow_redirect_url+'" >(Re)init all</a>'
        msg = str(nbr_reinit_needed) + ' Sessions needs to be (Re)initialized    ' + btn
        flash(msg, 'alert-warning')

    _tree_ = get_schools_tree(int(school_id), int(branch_id), int(promo_id))
    # _tree_ = get_schools_tree_cached(int(school_id), int(branch_id), int(promo_id))

    zNodes = '[' + _tree_ + ']'
    return render_template('tree/tree.html', title='Tree', zNodes=zNodes, options_arr=options_arr)

def get_options_by_promo(promo):
    options = ''
    semesters = promo.branch.get_semesters_ordered()
    semesters = semesters[-1].get_latest_of_semesters_list()
    for semester in semesters:
        val = str(semester.id)
        # opt = str(semester.get_nbr())
        opt = str(semester.get_nbr()) + ' - ' + semester.name
        options += '<option value='+val+'>'+opt+'</option>'
    return options

def get_options():
    array = []
    promos = Promo.query.all()
    for promo in promos:
        # only "promos" that does not have "sessions"
        if len(promo.sessions) == 0:
            array.append( [ promo.id, get_options_by_promo(promo) ] )
    return array



# @cache.cached(timeout=300)
# def check_reinit_cached():
#     return check_reinit_needed()

def check_reinit_needed():
    sessions = Session.query.filter_by(is_closed=False).all()
    count = 0
    for session in sessions:
        if session.is_config_changed():
            count += 1
    return count

@app.route('/tree/re-init/school/<school_id>', methods=['GET'])
@app.route('/tree/re-init/', methods=['GET'])
def tree_reinit_all(school_id=0):
    nbr_reinit = check_reinit_needed()
    sessions = Session.query.filter_by(is_closed=False).all()
    nbr_init = 0
    for session in sessions:
        if session.is_config_changed():
            init_all(session)
            calculate_all(session)
            nbr_init += 1
    flash( str(nbr_init) + " reinitialized")

    return redirect( url_for('tree') )

#
