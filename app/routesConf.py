from app import app, db
from flask import render_template, url_for
from app.models import Semester, Type, Unit, School
from flask_breadcrumbs import register_breadcrumb



def tree_type(id):
    type = Type.query.filter_by(id=id).first()
    if type == None:
        return '*'
    return type.type

def tree_percentage(percentage):
    # percent = str(percentage.percentage * 100)
    percent = ('0.00' if percentage.percentage is None else str(percentage.percentage * 100)) 
    normalized = percent.rstrip('0').rstrip('.')
    val = tree_type(percentage.type_id) + ': ' + normalized + '%'
    # val = tree_type(percentage.type_id) + ': ' + percent
    href = '/admin/percentage/edit/?id=' + str(percentage.id)
    link = '{val: "' + val + '", href: "' + href + '", target: "_blank"}'
    time = ''
    if percentage.time != None and percentage.time != '':
        time = 'Time: ' + str(percentage.time).rstrip('0').rstrip('.') + ' h'
    return '''
    {
        text:{ 
            link: ''' + link + ''',
            time: "''' + time + '''"
        }
    }'''

def tree_module(module):
    # replacing Spaces by Empty Character
    val = module.name.replace(' ', ' ')
    href = '/admin/module/edit/?id=' + str(module.id)
    link = '{ val: "' + val + '", href: "' + href + '", target: "_blank"}'
    code = str(module.code).replace('None', '???????')
    coeff = str(module.coefficient)
    credit = str(module.credit)
    time = ''
    if module.time != None and module.time != '':
        time =  'Time: ' + str(module.time).rstrip('0').rstrip('.') + ' h'
    
    percentages = ''
    percent = 0
    for percentage in module.percentages:
        percentages += tree_percentage(percentage) + ','
        if percentage.percentage != None and percentage.percentage > 0:
            percent += percentage.percentage

    percentage_problem = ''
    if percent != 1:
        percentage_problem = ', percent: "make sure the percentages sum is 100%"'

    return '''
    {
        text:{
            link: ''' + link + ''', 
            code: "Code: ''' + code + '''", 
            coeff: "Coeff: ''' + coeff + '''", 
            credit: "Credit: ''' + credit + '''",
            time: "''' + time + '''"
            ''' + percentage_problem + '''
        }, 
        stackChildren: true, 
        children: [''' + percentages + ''']
    }'''

def tree_unit(unit):
    href = '/admin/unit/edit/?id=' + str(unit.id)
    link = '{val: "' + unit.name + '", href: "' + href + '", target: "_blank"}'
    coeff = str( unit.unit_coefficient ).replace('None', '')
    # credit = str( get_unit_credit(unit.id) )
    credit = str( unit.get_unit_cumul_credit() )
    modules = ''
    for module in unit.modules:
        modules += tree_module(module) + ','

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

def tree_semester(semester):
    href = '/admin/semester/edit/?id=' + str(semester.id)
    link = '{ val: "' + semester.name + '", href: "' + href + '", target: "_blank"}'
    units = ''
    credit = semester.get_semester_cumul_credit()
    for unit in semester.units:
        units += tree_unit(unit) + ','

    return '''
    {
        text: { 
            link: ''' + link + ''',
            //empty: " ",
            credit: "Credit: ''' + str(credit) + '''",
            //new: "New<img src=/static/ztree/img/diy/19-big.png>",
            new: {
                val: "  new  ", 
                href: "mailto:we@great.com", 
            },
            edit: {
                val: "  edit  ", 
                href: "mailto:we@great.com", 
            }
        },
        children: [''' + units + ''']
    }'''


def tree_conf_data(semester_id):
    semester = Semester.query.filter_by(id=semester_id).first_or_404()
    t_semester = tree_semester(semester)

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
    return conf_data



@app.route('/conf/<semester_id>/', methods=['GET', 'POST'])
def conf(semester_id=0):
    conf_data = tree_conf_data(semester_id)
    return render_template('conf/treant.html', title='Conficuration Tree', data=conf_data)

@app.route('/session/<session_id>/conf/<semester_id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.tree.session.conf', 'Configuration')
def conf_session(session_id, semester_id):
    conf_data = tree_conf_data(semester_id)
    return render_template('conf/treant.html', title='Conficuration Tree', data=conf_data)




@app.route('/conf-mod/<semester_id>/', methods=['GET', 'POST'])
def conf_mod(semester_id):
    semester = Semester.query.filter_by(id=semester_id).first_or_404()
    t_semester = tree_semester(semester)

    conf_data = '''
    {
        chart: {
            container: "#tree-config",
            animateOnInit: true,
            node: {
              collapsable: true
            },
            animation: {
              nodeAnimation: "easeOutBounce",
              nodeSpeed: 700,
              connectorsAnimation: "bounce",
              connectorsSpeed: 700
            }
        },
        nodeStructure:''' + t_semester + '''
    }'''

    return render_template('conf/treant.html', title='Conficuration Tree', data=conf_data)




#######################################
#####                             #####
#####           BRANCHES          #####
#####                             #####
#######################################

def semesters_t(branch, open_sem_id):
    semesters = branch.semesters
    semesters_tree = ''
    for semester in semesters:
        id = 'semester_' + str(semester.id)
        pId = 'branch_' + str(branch.id)
        name = 'Semester ' + str(semester.get_nbr())

        cumul_credit = semester.get_semester_cumul_credit()
        if cumul_credit != 30:
            name += "  - <span style='color:blue;margin-right:0px;'>(credit=" + str(cumul_credit) + ")</span> "
        if semester.has_percentage_problem():
            name += "  - <span style='color:red;margin-right:0px;'>(percentage problem)</span> "
        if semester.has_code_missing():
            name += "  - <span style='color:purple;margin-right:0px;'>(has code missing)</span> "


        font = '{"font-weight":"bold", "font-style":"italic"}'
        icon = 'pIcon15'

        open = 'true'
        if open_sem_id != 0:
            open = 'false'
            if open_sem_id == semester.id:
                open = 'true'

        icon = 'icon19'
        # icon = 'icon20'
        url = url_for('conf', semester_id=semester.id)

        sem = '{id:"'+id+'", pId:"'+pId+'", name:"'+name+'", open:'+open+', url: "'+url+'", iconSkin:"'+icon+'", font:'+font+'},'
        semesters_tree += sem 
    return semesters_tree

def branches_t(school, open_b_id, open_sem_id):
    branches = school.branches
    branches_tree = ''
    for branch in branches:
        id = 'branch_'+str(branch.id)
        pId = 'school_'+str(school.id)
        # sem = ''
        sem = semesters_t(branch, open_sem_id)
        open = 'true'
        if open_b_id != 0:
            open = 'false'
            if open_b_id == branch.id:
                open = 'true'
        if sem == '':
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+branch.name+'", open:'+open+', iconSkin:"icon11"},'
        else:
            b = '{ id:"'+id+'", pId:"'+pId+'", name:"'+branch.name+'", open:'+open+', isParent:true},'
        
        branches_tree += b + sem
    return branches_tree

def schools_t(open_s_id=0, open_b_id=0, open_sem_id=0):
    schools = School.query.all()
    schools_tree = ''
    for school in schools:
        id = 'school_'+str(school.id)
        icon = 'pIcon12'
        branches_tree = branches_t(school, open_b_id, open_sem_id)
        open = 'true'
        if open_s_id != 0:
            open = 'false'
            if open_s_id == school.id:
                open = 'true'
        s = '{ id:"'+id+'", pId:0, name:"'+school.name+'", open:'+open+', iconSkin:"'+icon+'", isParent:true },'
        schools_tree += s + branches_tree
    return schools_tree

@app.route('/branches-tree/', methods=['GET', 'POST'])
def treeBranches(school_id=0, branch_id=0, semester_id=0):
    zNodes = '[' + schools_t(int(school_id), int(branch_id), int(semester_id)) + ']'
    return render_template('tree/tree.html', title='Tree', zNodes=zNodes)

