from app import app, db
from flask import render_template, url_for, redirect, flash, redirect
from app.models import Annual, Semester, Unit, Module, Percentage, Type, School
from flask_breadcrumbs import register_breadcrumb
from datetime import datetime



def tree_type(id):
    type = Type.query.filter_by(id=id).first()
    if type == None:
        return '*'
    return type.type

def tree_percentage(percentage, is_closed=False):
    # percent = str(percentage.percentage * 100)
    percent = ('0.00' if percentage.percentage is None else str(percentage.percentage * 100)) 
    normalized = percent.rstrip('0').rstrip('.')
    val = tree_type(percentage.type_id) + ': ' + normalized + '%'
    # val = tree_type(percentage.type_id) + ': ' + percent
    href = '/admin/percentage/edit/?id=' + str(percentage.id)
    if is_closed:
        href = 'URL_STRING_TO_BE_REPLACED'

    # link = '{ val: "' + val + '", href: "' + href + '", target: "_blank" }'
    link = '{ val: "' + val + '", href: "' + href + '" }'

    time = ''
    if percentage.time != None and percentage.time != '':
        time = 'Time: ' + str(percentage.time).rstrip('0').rstrip('.') + ' h'

    ratt = ''
    if percentage.rattrapable != None and percentage.rattrapable != False:
        ratt = 'Ratt.'

    return '''
    {
        text:{ 
            link: ''' + link + ''',
            time: "''' + time + '''",
            rattrapable: "''' + ratt + '''"
        }
    }'''

def tree_module(module, is_closed=False):
    # replacing Spaces by Empty Character
    val = module.name.replace(' ', ' ')
    href = '/admin/module/edit/?id=' + str(module.id)
    if is_closed:
        href = 'URL_STRING_TO_BE_REPLACED'

    # link = '{ val: "' + val + '", href: "' + href + '", target: "_blank" }'
    link = '{ val: "' + val + '", href: "' + href + '" }'
    code = str(module.code).replace('None', '???????')
    coeff = str(module.coefficient)
    credit = str(module.credit)
    time = ''
    if module.time != None and module.time != '':
        time =  'Time: ' + str(module.time).rstrip('0').rstrip('.') + ' h'
    
    percentages = ''
    percent = 0
    for percentage in module.percentages:
        percentages += tree_percentage(percentage, is_closed) + ','
        if percentage.percentage != None and percentage.percentage > 0:
            percent += percentage.percentage

    percentage_problem = ''
    if percent != 1:
        percentage_problem = ', percent: "make sure the percentages sum is 100%"'


    rattrapable_error = ''
    if module.has_rattrapable_error() == True:
        rattrapable_error = ', ratt_err: "rattrapable ERROR"'

    return '''
    {
        text:{
            link: ''' + link + ''', 
            code: "Code: ''' + code + '''", 
            coeff: "Coeff: ''' + coeff + '''", 
            credit: "Credit: ''' + credit + '''",
            time: "''' + time + '''"
            ''' + percentage_problem + '''
            ''' + rattrapable_error + '''
        }, 
        stackChildren: true, 
        children: [''' + percentages + ''']
    }'''

def tree_unit(unit, is_closed=False):
    href = '/admin/unit/edit/?id=' + str(unit.id)
    if is_closed:
        href = 'URL_STRING_TO_BE_REPLACED'

    # link = '{ val: "' + unit.name + '", href: "' + href + '", target: "_blank" }'
    link = '{ val: "' + unit.name + '", href: "' + href + '" }'
    coeff = str( unit.unit_coefficient ).replace('None', '')
    # credit = str( get_unit_credit(unit.id) )
    credit = str( unit.get_unit_cumul_credit() )
    modules = ''
    for module in unit.modules:
        modules += tree_module(module, is_closed) + ','

    is_fondamental = ' '
    if unit.is_fondamental == True:
        is_fondamental = 'Fondamental'

    return '''
    {
        text:{
            link: ''' + link + ''',
            coeff: "Coeff: ''' + coeff + '''",
            credit: "Credit: ''' + credit + '''",
            is_fondamental: "''' + is_fondamental + '''",
        }, 
        children: [''' + modules + ''']
    }'''

def tree_semester(semester, is_closed=False):
    # href = '/admin/semester/edit/?id=' + str(semester.id)
    # if is_closed:
    #     href = 'URL_STRING_TO_BE_REPLACED'

    href = url_for('semester_view', id=semester.id)

    # link = '{ val: "' + semester.name + '", href: "' + href + '", target: "_blank" }'
    link = '{ val: "' + semester.name + '", href: "' + href + '" }'

    units = ''
    credit = semester.get_semester_cumul_credit()
    for unit in semester.units:
        units += tree_unit(unit, is_closed) + ','

    return '''
    {
        text: { 
            link: ''' + link + ''',
            //empty: " ",
            credit: "Credit: ''' + str(credit) + '''",
            //new: "New<img src=/static/ztree/img/diy/19-big.png>",
            //new: { val: "  new  ",  href: "mailto:we@great.com", },
            //edit: { val: "  edit  ",  href: "mailto:we@great.com", }
        },
        children: [''' + units + ''']
    }'''

def tree_conf_data(semester_id):
    semester = Semester.query.filter_by(id=semester_id).first_or_404()

    # is_closed = semester.is_locked() or semester.is_closed
    is_closed = semester.is_locked()
    t_semester = tree_semester(semester, is_closed)

    conf_data = '''
    {
        chart: {
            container: "#tree-config",
            animateOnInit: true,
            //connectors: {
            //    type: 'step'
            //},
            
            node: {
              collapsable: true
            },
            animation: {
              nodeAnimation: "easeOutBounce",
              nodeSpeed: 700,
              connectorsAnimation: "bounce",
              connectorsSpeed: 700
            }/**/
        },
        nodeStructure:''' + t_semester + '''
    }'''

    if is_closed:
        href = url_for('tree_semesters')
        conf_data = conf_data.replace('URL_STRING_TO_BE_REPLACED', href)
        flash(' this Semester is closed')
    
    return conf_data

@app.route('/conf-semester/<semester_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.semester_tree.cccconf', 'Configuration')
def conf(semester_id=0):
    conf_data = tree_conf_data(semester_id)
    return render_template('conf/treant.html', title='Conficuration Tree', data=conf_data)

@app.route('/session/<session_id>/conf-semester/<semester_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.conf', 'Configuration')
def conf_session(session_id, semester_id):
    conf_data = tree_conf_data(semester_id)
    return render_template('conf/treant.html', title='Conficuration Tree', data=conf_data)

# @app.route('/conf-mod/<semester_id>/', methods=['GET', 'POST'])
# def conf_mod(semester_id):
#     semester = Semester.query.filter_by(id=semester_id).first_or_404()
#     t_semester = tree_semester(semester)

#     conf_data = '''
#     {
#         chart: {
#             container: "#tree-config",
#             animateOnInit: true,
#             node: {
#               collapsable: true
#             },
#             animation: {
#               nodeAnimation: "easeOutBounce",
#               nodeSpeed: 700,
#               connectorsAnimation: "bounce",
#               connectorsSpeed: 700
#             }
#         },
#         nodeStructure:''' + t_semester + '''
#     }'''

#     return render_template('conf/treant.html', title='Conficuration Tree', data=conf_data)


#######################################
#####                             #####
#####        Semester Tree        #####
#####                             #####
#######################################

def semesters_tr(annual, open_sem_id):
    semesters = annual.get_semesters_ordered()
    semesters_tree = ''
    for semester in semesters:
        id = 'semester_' + str(semester.id)
        pId = 'annual_' + str(annual.id)
        name = 'Semester ' + str(semester.get_nbr())

        # add lock
        # if semester.is_locked() or semester.is_closed:
        if semester.is_locked():
            name += " <span class='button icon13_ico_docu'></span>"
        elif semester.get_nbr() < 10:
            name += "    "
        elif semester.get_nbr() >= 10:
            name += "  "

        if semester.has_fondamental():
            name += "<span style='color:purple;margin-right:0px;'>[fondamental]</span>"
            
        if semester.latest_update != None:
            latest_update = semester.latest_update.strftime('%Y-%m-%d %H:%M:%S')
            name += " <span style='font-size: 8px;'>(" + latest_update + ")</span>"

        name += " <span style='font-size: 0.1px;'>" + str(annual.name) + "</span>"

        # collecting ERRORS
        cumul_credit = semester.get_semester_cumul_credit()
        units_coeff_comul = semester.get_semester_units_coeff_comul()

        if cumul_credit != 30:
            name += " - <span style='color:blue;margin-right:0px;'>(credit=" + str(cumul_credit) + ")</span> "
        if units_coeff_comul != 10:
            name += " - <span style='color:orange;margin-right:0px;'>(unit coeff=" + str(units_coeff_comul) + ")</span> "
        if semester.has_percentage_problem():
            name += " - <span style='color:red;margin-right:0px;'>(percentage problem)</span> "
        if semester.has_code_missing():
            name += " - <span style='color:purple;margin-right:0px;'>(has code missing)</span> "
        if semester.has_rattrapable_error():
            name += " - <span style='color:Tan;margin-right:0px;'>(has Rattrapable Error)</span> "

        name = "<span style='font-size:16px;'>" + name + "</span>"

        font = '{ }'
        # font = '{"font-weight":"bold", "font-style":"italic"}'

        open = 'true'
        if open_sem_id != 0:
            open = 'false'
            if open_sem_id == semester.id:
                open = 'true'

        icon = 'icon21'
        url = url_for('conf', semester_id=semester.id)
        # <span id="hh">Text Demo...</span>
        sem = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:'+open+', url: "'+url+'", target:"_self", iconSkin:"'+icon+'", font:'+font+'},'
        semesters_tree += sem 
    return semesters_tree

def annuals_tr(branch, open_sem_id):
    annuals = branch.get_annuals_ordered()
    annuals_tree = ''
    for annual in annuals:
        id = 'annual_' + str(annual.id)
        pId = 'branch_' + str(branch.id)
        name = 'Annual ' + str(annual.annual)

        sem = semesters_tr(annual, open_sem_id)
        open = 'true'

        font = '{ }'
        icon = 'pIcon23'

        a = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:'+open+', target:"_self", iconSkin:"'+icon+'", font:'+font+', isParent:true},'
        annuals_tree += a + sem
    return annuals_tree

def branches_tr(school, open_b_id, open_sem_id):
    branches = school.branches
    branches_tree = ''
    for branch in branches:
        id = 'branch_'+str(branch.id)
        pId = 'school_'+str(school.id)

        ann = annuals_tr(branch, open_sem_id)
        name = branch.name+' - '+str(branch.description)
        open = 'true'
        if open_b_id != 0:
            open = 'false'
            if open_b_id == branch.id:
                open = 'true'
        if ann == '':
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:'+open+', iconSkin:"icon11"},'
        else:
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:'+open+', isParent:true},'
        
        branches_tree += b + ann
    return branches_tree

def schools_tr(open_s_id=0, open_b_id=0, open_sem_id=0):
    schools = School.query.all()
    schools_tree = ''
    for school in schools:
        id = 'school_'+str(school.id)
        icon = 'pIcon12'
        branches_tree = branches_tr(school, open_b_id, open_sem_id)
        open = 'true'
        if open_s_id != 0:
            open = 'false'
            if open_s_id == school.id:
                open = 'true'
        s = '{ id:"'+id+'", pId:0, name:"'+school.name+'", open:'+open+', iconSkin:"'+icon+'", isParent:true },'
        schools_tree += s + branches_tree
    return schools_tree

@app.route('/semesters-tree/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.semester_tree', 'Semesters Tree')
def tree_semesters(school_id=0, branch_id=0, semester_id=0):
    zNodes = '[' + schools_tr(int(school_id), int(branch_id), int(semester_id)) + ']'
    return render_template('tree/tree.html', title='Tree', zNodes=zNodes)


#######################################
#####                             #####
#####         Duplication         #####
#####                             #####
#######################################

def duplicate_percentage(percentage, new_module):
    perc_name = percentage.name
    if perc_name == None or perc_name == '':
        perc_name = percentage.type.type

    new_percentage = Percentage(
        name = perc_name,
        percentage = percentage.percentage,
        time = percentage.time,
        module_id = new_module.id,
        type_id = percentage.type_id,
        rattrapable = percentage.rattrapable,
        order = percentage.order
    )
    db.session.add(new_percentage)
    db.session.commit()

    return ' P: ' + str(new_percentage.id)

def duplicate_module(module, new_unit):
    new_module = Module(
        code = module.code,
        name = module.name,
        display_name = module.display_name,
        coefficient = module.coefficient,
        credit = module.credit,
        time = module.time,
        order = module.order,
        unit_id = new_unit.id
    )
    db.session.add(new_module)
    db.session.commit()

    # add children
    msg_percentages = ''
    for percentage in module.percentages:
        msg_percentages = msg_percentages +  duplicate_percentage(percentage, new_module) + ' - '

    return ' M: ' + str(new_module.id) + ' <' + msg_percentages + '>'

def duplicate_unit(unit, new_semester):
    new_unit = Unit(
        name = unit.name,
        display_name = unit.display_name,
        unit_coefficient = unit.unit_coefficient,
        is_fondamental = unit.is_fondamental,
        semester_id = new_semester.id,
        order = unit.order
    )
    db.session.add(new_unit)
    db.session.commit()

    # add children
    msg_modules = ''
    for module in unit.modules:
        msg_modules = msg_modules +  duplicate_module(module, new_unit) + ' - '

    return ' U: ' + str(new_unit.id) + ' [' + msg_modules + ']'

def duplicate_semester(semester):
    # new_name = semester.name + ' - ' + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), 
    new_name = semester.name
    # remove (***) from name

    new_semester = Semester(
        name = new_name, 
        display_name = semester.display_name,
        semester = semester.semester,
        latest_update = datetime.utcnow(),
        annual_id = semester.annual_id
    )
    db.session.add(new_semester)
    db.session.commit()

    # add children
    msg_units = ''
    for unit in semester.units:
        msg_units = msg_units +  duplicate_unit(unit, new_semester) + ' - '

    msg = ' S: ' + str(new_semester.id) + ' (' + msg_units + ' ) '
    return [new_semester, msg]

@app.route('/duplicate-config/<semester_id>/', methods=['GET', 'POST'])
def duplicate_config(semester_id=0):
    semester = Semester.query.get_or_404(semester_id)
    for parallel in semester.get_parallels():
        if parallel.is_locked() != True:
            flash("you can't Duplicate when there is a Parallel Open Semester", "alert-danger")
            return redirect( url_for('semester_index'))
    new_semester = duplicate_semester(semester)
    if new_semester[0] == None:
        flash('Some Error happend', 'alert-danger')
        return redirect( url_for('semester_view', id=new_semester[0].id) )
    flash('Semester ('+str(new_semester[0].get_nbr())+') was Duplicated', 'alert-success')
    # return redirect( url_for('semester_view', id=new_semester[0].id) )
    return redirect( url_for('semester_special_update', id=new_semester[0].id) )
    # return 'Semester: ' + str(semester.id) + ' duplicate: ' + str(new_semester[0]) + ' \n--- ' + new_semester[1]

