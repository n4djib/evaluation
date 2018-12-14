from app import app, db
from flask import render_template, url_for
from app.models import School, Session, Semester, Promo

from flask_breadcrumbs import register_breadcrumb


def get_creation_links(promo, seperate=True):
    sessions = promo.sessions
    semesters = promo.branch.semesters
    links = ''
    if len(semesters) > 0:
        first_semester_id = semesters[0].id

        id = 'new_' + str(promo.id)
        pId = 'promo_' + str(promo.id)
        url = url_for('create_session', promo_id=promo.id, semester_id=first_semester_id)

        if len(sessions) > 0:
            first_sessions = sessions[0]
            sessions_chain = first_sessions.get_chain()
            last_session_id = sessions_chain[-1]
            last_session = Session.query.get(last_session_id)

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
                    # if seperate is True:
                    #     links += '{id:"seperate_'+id+'", pId:"'+pId+'", name:"", iconSkin:"icon0"},'
        else:
            name = 'Create First Semester'
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

def get_sessions_tree(promo, promo_label=''):
    sessions = Session.query.filter_by(promo_id=promo.id).join(Semester)\
        .order_by(Semester.annual, Semester.semester).all()

    sessions_tree = ''
    for session in sessions:
        semester = session.semester.get_nbr()

        annual = str(session.annual_session_id)

        name = 'Semester: '
        if session.is_rattrapage:
            name = 'Rattrapage: '
        name += str(semester) + " <span style='font-size: 0.1px;'>" + promo_label + "</span>"
        
        id = 'semester_'+str(session.id)
        pId = 'promo_'+str(promo.id)
        url = url_for('session', session_id=session.id)
        if session.is_closed == True:
            p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, url: "'+url+'", target:"_self", iconSkin:"icon13"},'
        else:
            p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:true, url: "'+url+'", target:"_self"},'

        sessions_tree += p
        sessions_tree += get_annual_session(session, pId)

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



        # promo_label = promo.get_label()
        # name = "<span style='color: "+str(promo.color)+";'>" + promo_label + "</span>"

        name = promo.name

        promo_display_name = str(promo.display_name).replace('None', '')
        if promo_display_name != '':
            name += " - <span style='color: "+str(promo.color)+";'>" + promo_display_name + "</span>"

        name = name + ' (' + str(get_year(promo)) + ' Year)'





        font = '{"font-weight":"bold", "font-style":"italic"}'
        icon = 'pIcon15'

        # open = 'true'
        open = 'false'
        if open_p_id != 0:
            open = 'false'
            if open_p_id == promo.id:
                open = 'true'

        # sessions_tree = get_sessions_tree(promo, promo_label)
        sessions_tree = get_sessions_tree(promo, promo.name + ' ' + promo_display_name)
        if sessions_tree == '':
            icon = 'icon15'
        p = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:'+open+', iconSkin:"'+icon+'", font:'+font+'},'
        promos_tree += p + sessions_tree 
    return promos_tree

def get_branches_tree(school, open_b_id, open_p_id):
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
        branches_tree = get_branches_tree(school, open_b_id, open_p_id)
        open = 'true'
        if open_s_id != 0:
            open = 'false'
            if open_s_id == school.id:
                open = 'true'
        s = '{ id:"'+id+'", pId:0, name:"'+school.name+'", open:'+open+', iconSkin:"'+icon+'", isParent:true },'
        schools_tree += s + branches_tree
    return schools_tree

@app.route('/tree/school/<school_id>/branch/<branch_id>/promo/<promo_id>/', methods=['GET'])
@app.route('/tree/school/<school_id>/branch/<branch_id>/', methods=['GET'])
@app.route('/tree/school/<school_id>/', methods=['GET'])
@app.route('/tree/', methods=['GET'])
@register_breadcrumb(app, '.tree', 'Tree')
def tree(school_id=0, branch_id=0, promo_id=0):
    options_arr = get_options()
    # return str(options_arr)
    zNodes = '[' + get_schools_tree(int(school_id), int(branch_id), int(promo_id)) + ']'
    return render_template('tree/tree.html', title='Tree', zNodes=zNodes, options_arr=options_arr)


def get_options_by_promo(promo):
    options = ''
    semesters = promo.branch.semesters
    for semester in semesters:
        val = str(semester.id)
        opt = str(semester.get_nbr())
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


