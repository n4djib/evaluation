from app import app, db
from flask import render_template
from app.models import Semester, Type, Unit

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
    if percentage.time != None:
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
    if module.time != None:
        time =  'Time: ' + str(module.time).rstrip('0').rstrip('.') + ' h'
    
    percentages = ''
    percent = 0
    for percentage in module.percentages:
        percentages += tree_percentage(percentage) + ','
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

def get_unit_credit(unit_id):
    unit = Unit.query.filter_by(id=unit_id).first()
    modules = unit.modules
    unit_credit = 0
    for module in modules:
        unit_credit += int(module.credit or 0)
        # unit_credit += int(0 if module.credit is None else module.credit)
    return unit_credit

def tree_unit(unit):
    href = '/admin/unit/edit/?id=' + str(unit.id)
    link = '{val: "' + unit.name + '", href: "' + href + '", target: "_blank"}'
    coeff = str( unit.unit_coefficient ).replace('None', '')
    credit = str( get_unit_credit(unit.id) )
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
    credit = 0
    for unit in semester.units:
        credit += get_unit_credit(unit.id)
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

@app.route('/conf/<semester_id>/', methods=['GET', 'POST'])
def conf(semester_id):
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


