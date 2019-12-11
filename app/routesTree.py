from app import app, db
# from app import cache
from flask import render_template, url_for, redirect, request, flash
from app.models import School, Session, Annual, Semester, Promo, AnnualSession
from flask_breadcrumbs import register_breadcrumb
from datetime import datetime
from flask_login import current_user, login_required
# from app.routesCalculation import init_all, calculate_all
from app.routesCalculation import init_all




def get_classement_link(promo, separate=True):
    # promo = promo.
    id = 'classement_' + str(promo.id)
    pId = 'promo_' + str(promo.id)
    name = 'Progression / Classement'
    hint = ''
    icon = 'icon24'
    url = url_for('classement_laureats', promo_id=promo.id)
    links = ''
    if separate is True:
        links += '{id:"separate_'+id+'", pId:"'+pId+'", name:"", iconSkin:"icon0"},'
    
    links += '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", hint:"'+hint+'", target:"_top", url: "'+url+'", iconSkin:"'+icon+'"},'
    return links

def get_students_list_link(promo, separate=True):
    id = 'students_list_' + str(promo.id)
    pId = 'promo_' + str(promo.id)
    name = 'Students List'
    hint = ''
    icon = 'icon15'
    url = url_for('student_by_promo', promo_id=promo.id)

    links = ''
    if separate is True:
        links += '{id:"separate_'+id+'", pId:"'+pId+'", name:"", iconSkin:"icon0"},'
    
    links += '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", hint:"'+hint+'", target:"_top", url: "'+url+'", iconSkin:"'+icon+'"},'
    return links

def get_creation_links(promo, separate=True):
    semesters = get_semesters_not_in_promo(promo)
    links = ''
    if len(semesters) > 0:
        first_semester_id = semesters[0].id
        next_semester_to_create = promo.get_next_semester()

        id = 'new_' + str(promo.id)
        pId = 'promo_' + str(promo.id)
        hint = ''
        semester_id=first_semester_id
        if next_semester_to_create != None:
            semester_id=next_semester_to_create.id
        url = url_for('create_session', promo_id=promo.id, semester_id=semester_id)
        name = 'Create Semester'
        # if separate is True:
        #     links += '{id:"separate_'+id+'", pId:"'+pId+'", name:"", iconSkin:"icon0"},'
        links += '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", hint:"'+hint+'", target:"_top", url: "'+url+'", iconSkin:"icon01"},'
    return links

def get_creation_link_modal(promo):
    semesters = get_semesters_not_in_promo(promo)
    links = ''
    if len(semesters) > 0:
        first_semester_id = semesters[0].id
        next_semester_to_create = promo.get_next_semester()

        id = 'new_modal_' + str(promo.id)
        pId = 'promo_' + str(promo.id)
        hint = ''
        semester_id=first_semester_id
        if next_semester_to_create != None:
            semester_id=next_semester_to_create.id
        url = ''
        # url = url_for('create_session', promo_id=promo.id, semester_id=semester_id)
        name = 'Create Semester Modal'
        links += '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", hint:"'+hint+'", target:"_top", url: "'+url+'", iconSkin:"icon01"},'
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
            hint = ''
            url = url_for('annual_session', annual_session_id=an_s_id)
            # name = 'Annual '+str(session.semester.annual.annual)+' Results       (an:'+str(an_s_id)+')'
            name = 'Annual '+str(session.semester.annual.annual)+' Results'
            annual = '{id:"annual_'+str(an_s_id)+'", pId:"'+pId+'", url: "'+url+'", name:"'+name+'", hint:"'+hint+'", target:"_self", iconSkin:"icon17"},'
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
        hint = ''

        icon = 'icon21'
        if session.is_rattrapage == True:
            icon = 'icon22'

        if session.is_historic:
            icon = 'icon21_ratt_h'
            if session.is_rattrapage == True:
                icon = 'icon22_ratt_h'

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

        # # Configuration change
        # if session.is_config_changed() and session.is_closed==False:
        #     name += "<span style='color: orange;''>        Configuration has changed, you need to Re(initialized)</span>"

        if session.check_errors_exist():
            name += "<span style='color: red;''>        <<<  Contains ERRORS  >>> </span>"


        p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", hint:"'+hint+'", open:true, url: "'+url+'", target:"_self", iconSkin:"'+icon+'" },'

        sessions_tree += p + get_annual_session(session, pId)

    separate = True
    if sessions_tree == '':
        separate = False
    return sessions_tree \
        + get_students_list_link(promo, separate)\
        + get_classement_link(promo, False)\
        + get_creation_links(promo, separate)\
        + get_creation_link_modal(promo)


@app.route('/get_async_sessions_by_promo/<promo_id>/', methods=['GET', 'POST'])
def get_async_sessions_by_promo(promo_id):
    promo = Promo.query.get_or_404(promo_id)
    return '[' + get_sessions_tree(promo) + ']'



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

        year = promo.get_latest_annual()
        if year == 1:
            name = name + ' (' +str(promo.get_latest_annual())+ ' ère Année)'
        elif year > 1:
            name = name + ' (' +str(promo.get_latest_annual())+ ' ème Année)'

        hint = ''

        font = '{"font-weight":"bold", "font-style":"italic"}'
        icon = 'pIcon16'

        open = 'false'
        if open_p_id == 0:
            open = 'true'
        if open_p_id > 0:
            # open = 'false'
            if open_p_id == promo.id:
                open = 'true'

        sessions_tree = ''
        if open == 'true':
            # 
            # 
            # 
            sessions_tree = get_sessions_tree(promo)
            # 
            # 
            # 
            # if promo is None:
            #     pre_render_promos_tree(promo)
            # sessions_tree = promo.sub_tree
            # 
            # 
            # 

        p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", hint:"'+hint+'", times:1, isParent:true, open:'+open+', iconSkin:"'+icon+'", font:'+font+'},'
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

        hint = ''

        open = 'true'
        if open_b_id != 0:
            open = 'false'
            if open_b_id == branch.id:
                open = 'true'

        if p == '':
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+name+'", hint:"'+hint+'", open:'+open+', iconSkin:"icon11"},'
        else:
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+name+'", hint:"'+hint+'", open:'+open+', isParent:true},'
        
        separation = '{id:"separate_'+id+'", pId:"'+pId+'", name:"", iconSkin:"icon0"},'

        branches_tree += b + p + separation
        
    return branches_tree

def get_schools_tree(open_s_id, open_b_id, open_p_id):
    schools = School.query.all()
    schools_tree = ''
    for school in schools:
        id = 'school_'+str(school.id)
        name = school.name
        icon = 'pIcon12'
        hint = ''
        branches_tree = get_branches_tree(school, open_b_id, open_p_id)
        open = 'true'
        if open_s_id != 0:
            open = 'false'
            if open_s_id == school.id:
                open = 'true'
        s = '{ id:"'+id+'", pId:0, name:"'+name+'", hint:"'+hint+'", open:'+open+', iconSkin:"'+icon+'", isParent:true },'
        schools_tree += s + branches_tree
    return schools_tree
    

# @cache.cached(timeout=500)
# def get_schools_tree_cached(open_s_id, open_b_id, open_p_id):
#     return get_schools_tree(open_s_id, open_b_id, open_p_id)

def tree_session_dlc(*args, **kwargs):
    session = Session.query.get_or_404(request.view_args['session_id'])
    return [{'text': 'Tree ('+ session.promo.name +')', 
        'url': url_for('tree', school_id=session.promo.branch.school.id, 
                               branch_id=session.promo.branch.id, 
                               promo_id=session.promo.id) }]

@app.route('/tree/session/<session_id>/', methods=['GET'])
@register_breadcrumb(app, '.tree_session', '', dynamic_list_constructor=tree_session_dlc)
def tree_session(session_id=0):
    return '*** just used to generate the url ***'


def tree_promo_dlc(*args, **kwargs):
    promo = Promo.query.get_or_404(request.view_args['promo_id'])
    return [{'text': 'Tree ('+ promo.name +')', 
        'url': url_for('tree', school_id=promo.branch.school.id, 
                               branch_id=promo.branch.id, 
                               promo_id=promo.id) }]

@app.route('/tree/promo/<promo_id>/', methods=['GET'])
@register_breadcrumb(app, '.tree_promo', '', dynamic_list_constructor=tree_promo_dlc)
def tree_promo(promo_id=0):
    return '*** just used to generate the url ***'


def tree_annual_dlc(*args, **kwargs):
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
@register_breadcrumb(app, '.tree_annual', '', dynamic_list_constructor=tree_annual_dlc)
def tree_annual(annual_session_id=0):
    return '*** just used to generate the url-annual-session ***'


@app.route('/tree/school/<school_id>/branch/<branch_id>/promo/<promo_id>/', methods=['GET'])
@app.route('/tree/school/<school_id>/branch/<branch_id>/', methods=['GET'])
@app.route('/tree/school/<school_id>/', methods=['GET'])
@app.route('/tree/', methods=['GET'])
@register_breadcrumb(app, '.tree', 'Tree')
# def tree(school_id=0, branch_id=0, promo_id=-1):
def tree(school_id=0, branch_id=-1, promo_id=-1):
    options_arr = get_options()

    # sessions_to_check = Session.query.filter_by(is_closed=False).all()
    # nbr_reinit_needed = check_reinit_needed(sessions_to_check)
    # nbr_recalculate_needed = check_recalculate_needed(sessions_to_check)
    # # nbr_sessions_errors = check_errors_exists(sessions_to_check)

    # if nbr_reinit_needed > 0:
    #     reinit_url = url_for('tree_reinit_all')
    #     slow_redirect_url = url_for('slow_redirect', url=reinit_url, message='(Re)initializing ' + str(nbr_reinit_needed) + ' sessions')
    #     btn = '<a id="re-init-all" class="btn btn-warning" href="'+slow_redirect_url+'" >(Re)initialize All</a>'
    #     msg = str(nbr_reinit_needed) + ' Sessions needs to be (Re)initialized    ' + btn
    #     flash(msg, 'alert-warning')

    # # if nbr_sessions_errors == 0:
    # if nbr_recalculate_needed > 0:
    #     recalculate_url = url_for('tree_recalc_all')
    #     slow_redirect_url = url_for('slow_redirect', url=recalculate_url, message='(Re)calculating' + str(nbr_recalculate_needed) + ' sessions')
    #     btn = '<a id="re-calc-all" class="btn btn-warning" href="'+slow_redirect_url+'" >(Re)Calculate All</a>'
    #     msg = str(nbr_recalculate_needed) + ' Sessions needs to be (Re)calculate    ' + btn
    #     flash(msg, 'alert-warning')
    # # else:
    # #     msg = str(nbr_sessions_errors) + ' Sessions Containes ERRORS'
    # #     flash(msg, 'alert-danger')


    _tree_ = get_schools_tree(int(school_id), int(branch_id), int(promo_id))
    # _tree_ = get_schools_tree_cached(int(school_id), int(branch_id), int(promo_id))

    zNodes = '[' + _tree_ + ']'
    return render_template('tree/tree.html', title='Tree', 
        zNodes=zNodes, options_arr=options_arr)



# def get_semesters_id_in_promo(promo):
#     semesters_id_list = []
#     sessions = promo.sessions
#     for session in sessions:
#         semester_id = session.semester.id
#         if semester_id not in semesters_id_list:
#             semesters_id_list.append(semester_id)
#     return semesters_id_list

def get_semesters_nbr_in_promo(promo):
    semesters_nbr_list = []
    sessions = promo.sessions
    for session in sessions:
        semester_nbr = session.semester.get_nbr()
        if semester_nbr not in semesters_nbr_list:
            semesters_nbr_list.append(semester_nbr)
    return semesters_nbr_list

def get_semesters_not_in_promo(promo):
    semesters = promo.branch.get_semesters_ordered()
    semesters = semesters[-1].get_latest_of_semesters_list()

    semesters_nbr_in_promo = get_semesters_nbr_in_promo(promo)
    semesters_remaining_promo = []
    for semester in semesters:
        if semester.get_nbr() not in semesters_nbr_in_promo:
            semesters_remaining_promo.append(semester)
    return semesters_remaining_promo

def get_options_by_promo(promo):
    options = ''
    semesters = get_semesters_not_in_promo(promo)
    next_semester_to_create = promo.get_next_semester()
    for semester in semesters:
        selected = ''
        if semester == next_semester_to_create:
            selected = 'selected' 
        val = str(semester.id)
        opt = str(semester.get_nbr()) + ' - ' + semester.name
        options += '<option value='+val+' '+selected+'>'+opt+'</option>'
    return options

def get_options():
    array = []
    promos = Promo.query.all()
    for promo in promos:
        array.append( [promo.id, get_options_by_promo(promo)] )
    return array


# @cache.cached(timeout=300)
# def check_reinit_cached():
#     return check_reinit_needed()


def check_reinit_needed(sessions):
    # sessions = Session.query.filter_by(is_closed=False).all()
    count = 0
    for session in sessions:
        if session.is_config_changed():
            count += 1
    return count

def check_recalculate_needed(sessions):
    count = 0
    for session in sessions:
        if session.check_recalculate_needed():
            count += 1
    return count

def check_errors_exists(sessions):
    # sessions = Session.query.filter_by(is_closed=False).all()
    count = 0
    for session in sessions:
        if session.check_errors_exist():
            count += 1
    return count



@app.route('/tree/re-init/school/<school_id>', methods=['GET'])
@app.route('/tree/re-init/', methods=['GET'])
def tree_reinit_all(school_id=0):
    # nbr_reinit = check_reinit_needed()
    sessions = Session.query.filter_by(is_closed=False).all()
    nbr_init = 0
    for session in sessions:
        if session.is_config_changed():
            init_all(session)
            nbr_init += 1
    flash( str(nbr_init) + " reinitialized")

    return redirect( url_for('tree') )


@app.route('/tree/re-calc/school/<school_id>', methods=['GET'])
@app.route('/tree/re-calc/', methods=['GET'])
def tree_recalc_all(school_id=0):
    sessions = Session.query.filter_by(is_closed=False).all()
    nbr_calc = 0
    for session in sessions:
        if session.check_recalculate_needed():
            # calculate_all(session)
            session.calculate()
            nbr_calc += 1
    flash( str(nbr_calc) + " recalculated")

    return redirect( url_for('tree') )


#
#
#




############## RE-Render Promo Tree ################

@app.route('/tree/prerender/', methods=['GET'])
def pre_render_tree():
    # later
    # filter further more to speed up pre render
    promos = Promo.query.all()
    for promo in promos:
        pre_render_promos_tree(promo.id)

    flash('pre-rendered the tree')
    return redirect(url_for('tree'))


