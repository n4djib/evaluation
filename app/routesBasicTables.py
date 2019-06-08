from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import SchoolFormCreate, SchoolFormUpdate, \
    PromoFormCreate, PromoFormUpdate, BranchFormCreate, BranchFormUpdate, \
    AnnualFormCreate, AnnualFormUpdate, ModuleFormCreate, ModuleFormUpdate, \
    SemesterFormCreate, SemesterFormUpdate, SemesterFormSpecialUpdate, \
    WilayaFormCreate, WilayaFormUpdate, TeacherFormCreate, TeacherFormUpdate
from app.models import School, Branch, Annual, Semester, Module, Unit, Wilaya, Promo, Teacher
from flask_breadcrumbs import register_breadcrumb
# import babel
from datetime import datetime


#######################################
#####            INDEX            #####

@app.route('/basic-tables/')
@register_breadcrumb(app, '.basic', 'Basic Tables')
def basic_index():
    return render_template('basic-forms/index.html', title='Basic Tables List')


#######################################
#####            Promo            #####

@app.route('/promo/')
@register_breadcrumb(app, '.basic.promo', 'Promos')
def promo_index():
    # i have to order by school & branch
    promos = Promo.query.order_by(Promo.branch_id, Promo.start_date).all()
    return render_template('basic-forms/promo/index.html', title='Promos List', promos=promos)

@app.route('/promo/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.promo.create', 'Create')
def promo_create():
    form = PromoFormCreate()
    
    if request.method == 'POST':
        start_date_request = request.form.get('start_date_str')
        if start_date_request != None and start_date_request != '':
            start_date_string = str(start_date_request)+'-01'
            form.start_date.data = datetime.strptime(start_date_string, '%Y-%m-%d')
        finish_date_request = request.form.get('finish_date_str')
        if finish_date_request != None and finish_date_request != '':
            finish_date_string = str(finish_date_request)+'-28'
            form.finish_date.data = datetime.strptime(finish_date_string, '%Y-%m-%d')
    
    if form.validate_on_submit():
        promo = Promo(
            name=form.name.data, 
            display_name=form.display_name.data, 
            branch_id=form.branch_id.data, 
            start_date=form.start_date.data, 
            finish_date=form.finish_date.data, 
            color=form.color.data
        )
        db.session.add(promo)
        db.session.commit()
        flash('Created and Saved Successfully.', 'alert-success')
        return redirect(url_for('promo_view', id=promo.id))
    return render_template('basic-forms/promo/create.html', title='Promo Create', form=form)

@app.route('/promo/update/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.promo.view.update', 'Update')
def promo_update(id):
    promo = Promo.query.get_or_404(id)
    form = PromoFormUpdate(promo.id)

    if request.method == 'POST':
        # start_date_request = request.form.get('start_date')
        start_date_request = request.form.get('start_date_str')
        if start_date_request != None and start_date_request != '':
            start_date_string = str(start_date_request)+'-01'
            form.start_date.data = datetime.strptime(start_date_string, '%Y-%m-%d')
        finish_date_request = request.form.get('finish_date_str')
        if finish_date_request != None and finish_date_request != '':
            finish_date_string = str(finish_date_request)+'-28'
            form.finish_date.data = datetime.strptime(finish_date_string, '%Y-%m-%d')
    
    if form.validate_on_submit():    
        promo.name = form.name.data
        promo.display_name = form.display_name.data
        # promo.branch_id = form.branch_id.data
        promo.start_date = form.start_date.data
        promo.finish_date = form.finish_date.data
        promo.color = form.color.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('promo_view', id=promo.id))
    elif request.method == 'GET':
        form.name.data = promo.name
        form.display_name.data = promo.display_name
        form.start_date.data = promo.start_date
        # if promo.start_date != None and promo.start_date != '':
        #     form.start_date.data = promo.start_date.strftime("%d/%m/%Y")
        form.finish_date.data = promo.finish_date
        form.branch_id.data = promo.branch_id
        form.color.data = promo.color
    return render_template('basic-forms/promo/update.html', title='Promo Update', form=form)

@app.route('/promo/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.promo.view', 'View')
def promo_view(id):
    promo = Promo.query.get_or_404(id)
    return render_template('basic-forms/promo/view.html', title='Promo View', promo=promo)

@app.route('/promo/delete/<int:id>/', methods=['GET', 'POST'])
def promo_delete(id):
    promo = Promo.query.get_or_404(id)
    # Note:
    #   has sessions or annual sessions
    if len(promo.sessions) > 0:
        flash("you can't delete this Promo because it is in Relation with other Records", 'alert-danger')
        flash("you have to break the relation with the Sessions first")
        return redirect(url_for('promo_view', id=id))

    db.session.delete(promo)
    db.session.commit()
    flash('Promo: ' + str(promo.name) + ' is deleted', 'alert-success')
    return redirect(url_for('promo_index'))


#######################################
#####           School            #####

@app.route('/school/')
@register_breadcrumb(app, '.basic.school', 'Schools')
def school_index():
    schools = School.query.all()
    return render_template('basic-forms/school/index.html', title='Schools List', schools=schools)

@app.route('/school/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.school.create', 'Create')
def school_create():
    form = SchoolFormCreate()
    if form.validate_on_submit():
        school = School(
            name=form.name.data, 
            description=form.description.data
        )
        db.session.add(school)
        db.session.commit()
        flash('Created and Saved Successfully.', 'alert-success')
        return redirect(url_for('school_view', id=school.id))
    return render_template('basic-forms/school/create.html', title='School Create', form=form)

@app.route('/school/update/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.school.view.update', 'Update')
def school_update(id):
    school = School.query.get_or_404(id)
    form = SchoolFormUpdate(school.id)
    if form.validate_on_submit():
        school.name = form.name.data
        school.description = form.description.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('school_view', id=school.id))
    elif request.method == 'GET':
        form.name.data = school.name
        form.description.data = school.description
    return render_template('basic-forms/school/update.html', title='School Update', form=form)

@app.route('/school/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.school.view', 'View')
def school_view(id):
    school = School.query.get_or_404(id)
    return render_template('basic-forms/school/view.html', title='School View', school=school)

@app.route('/school/delete/<int:id>/', methods=['GET', 'POST'])
def school_delete(id):
    school = School.query.get_or_404(id)
    if len(school.branches) > 0:
        flash("you can't delete this School because it is in Relation with other Records", 'alert-danger')
        flash("you have to break the relation with the Branches first")
        return redirect(url_for('school_view', id=id))
    db.session.delete(school)
    db.session.commit()
    flash('School: ' + str(school.name) + ' is deleted', 'alert-success')
    return redirect(url_for('school_index'))


#######################################
#####           Branch            #####

@app.route('/branch/')
@register_breadcrumb(app, '.basic.branch', 'Branches')
def branch_index():
    # i have to order by school & branch
    branches = Branch.query.order_by(Branch.school_id).all()
    return render_template('basic-forms/branch/index.html', title='Branches List', branches=branches)

@app.route('/branch/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.branch.create', 'Create')
def branch_create():
    form = BranchFormCreate()
    if form.validate_on_submit():
        branch = Branch(
            name=form.name.data, 
            description=form.description.data, 
            school_id=form.school_id.data
        )
        db.session.add(branch)
        db.session.commit()
        flash('Created and Saved Successfully.', 'alert-success')
        return redirect(url_for('branch_view', id=branch.id))
    return render_template('basic-forms/branch/create.html', title='Branch Create', form=form)

@app.route('/branch/update/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.branch.view.update', 'Update')
def branch_update(id):
    branch = Branch.query.get_or_404(id)
    form = BranchFormUpdate(branch.id)
    if form.validate_on_submit():
        branch.name = form.name.data
        branch.description = form.description.data
        branch.school_id = form.school_id.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('branch_view', id=branch.id))
    elif request.method == 'GET':
        form.name.data = branch.name
        form.description.data = branch.description
        form.school_id.data = branch.school_id
    return render_template('basic-forms/branch/update.html', title='Branch Update', form=form)

@app.route('/branch/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.branch.view', 'View')
def branch_view(id):
    branch = Branch.query.get_or_404(id)
    return render_template('basic-forms/branch/view.html', title='Branch View', branch=branch)

@app.route('/branch/delete/<int:id>/', methods=['GET', 'POST'])
def branch_delete(id):
    branch = Branch.query.get_or_404(id)
    if len(branch.promos) > 0 or len(branch.annuals) > 0 or len(branch.students) > 0:
        flash("you can't delete this Branch because it is in Relation with other Records", 'alert-danger')
        if len(branch.promos) > 0:
            flash("you have to break the relation with the Sessions first")
        if len(branch.annuals) > 0:
            flash("you have to break the relation with the Annuals first")
        return redirect(url_for('branch_view', id=id))
    db.session.delete(branch)
    db.session.commit()
    flash('Branch: ' + str(branch.name) + ' is deleted', 'alert-success')
    return redirect(url_for('branch_index'))


#######################################
#####           Annual            #####

@app.route('/annual/')
@register_breadcrumb(app, '.basic.annual', 'Annuales')
def annual_index():
    # i have to order by school & annual
    annuals = Annual.query.join(Branch).order_by(Branch.id, Annual.annual).all()
    return render_template('basic-forms/annual/index.html', title='Annuals List', annuals=annuals)

@app.route('/annual/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.annual.create', 'Create')
def annual_create():
    form = AnnualFormCreate()
    if form.validate_on_submit():
        annual = Annual(
            name=form.name.data, 
            display_name=form.display_name.data, 
            annual=form.annual.data,
            branch_id=form.branch_id.data
        )
        db.session.add(annual)
        db.session.commit()
        flash('Created and Saved Successfully.', 'alert-success')
        return redirect(url_for('annual_view', id=annual.id))
    return render_template('basic-forms/annual/create.html', title='Annual Create', form=form)

@app.route('/annual/update/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.annual.view.update', 'Update')
def annual_update(id):
    annual = Annual.query.get_or_404(id)
    form = AnnualFormUpdate(annual.id)
    if form.validate_on_submit():
        annual.name = form.name.data
        annual.display_name = form.display_name.data
        annual.annual = form.annual.data
        annual.branch_id = form.branch_id.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('annual_view', id=annual.id))
    elif request.method == 'GET':
        form.name.data = annual.name
        form.display_name.data = annual.display_name
        form.annual.data = annual.annual
        form.branch_id.data = annual.branch_id
    return render_template('basic-forms/annual/update.html', title='Annual Update', form=form)

@app.route('/annual/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.annual.view', 'View')
def annual_view(id):
    annual = Annual.query.get_or_404(id)
    return render_template('basic-forms/annual/view.html', title='Annual View', annual=annual)

@app.route('/annual/delete/<int:id>/', methods=['GET', 'POST'])
def annual_delete(id):
    annual = Annual.query.get_or_404(id)
    if len(annual.promos) > 0 or len(annual.semesters) > 0:
        flash("you can't delete this Annual because it is in Relation with other Records", 'alert-danger')
        if len(annual.promos) > 0:
            flash("you have to break the relation with the Promoss first")
        if len(annual.semesters) > 0:
            flash("you have to break the relation with the Semesters first")
        return redirect(url_for('annual_view', id=id))
    db.session.delete(annual)
    db.session.commit()
    flash('Annual: ' + str(annual.name) + ' is deleted', 'alert-success')
    return redirect(url_for('annual_index'))


#######################################
#####           Semester          #####

@app.route('/semester/')
@register_breadcrumb(app, '.basic.semester', 'Semesteres')
def semester_index():
    # i have to order by school & semester
    semesters = Semester.query.join(Annual)\
        .order_by(Annual.id, Semester.semester, Semester.latest_update).all()
    return render_template('basic-forms/semester/index.html', title='Semesters List', semesters=semesters)

@app.route('/semester/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.semester.create', 'Create')
def semester_create():
    form = SemesterFormCreate()
    if form.validate_on_submit():
        semester = Semester(
            name=form.name.data, 
            display_name=form.display_name.data, 
            semester=form.semester.data,
            # is_closed=form.is_closed.data,
            annual_id=form.annual_id.data
            # latest_update
        )
        db.session.add(semester)
        db.session.commit()
        flash('Created and Saved Successfully.', 'alert-success')
        return redirect(url_for('semester_view', id=semester.id))
    return render_template('basic-forms/semester/create.html', title='Semester Create', form=form)

@app.route('/semester/update/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.semester.view.update', 'Update')
def semester_update(id):
    semester = Semester.query.get_or_404(id)
    if semester.is_locked():
        flash("You can't update a closed Semester")
        return redirect(url_for('semester_view', id=id))
    form = SemesterFormUpdate(id)
    if form.validate_on_submit():
        semester.name = form.name.data
        semester.display_name = form.display_name.data
        semester.semester = form.semester.data
        # semester.is_closed = form.is_closed.data
        semester.annual_id = form.annual_id.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('semester_view', id=id))
    elif request.method == 'GET':
        form.name.data = semester.name
        form.display_name.data = semester.display_name
        form.semester.data = semester.semester
        # form.is_closed.data = semester.is_closed
        form.annual_id.data = semester.annual_id
    return render_template('basic-forms/semester/update.html', title='Semester Update', form=form)

@app.route('/semester/duplication-update/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.semester.view.update', 'Update Name')
def semester_special_update(id):
    semester = Semester.query.get_or_404(id)
    form = SemesterFormSpecialUpdate(id)
    if form.validate_on_submit():
        semester.name = form.name.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('semester_view', id=id))
    elif request.method == 'GET':
        form.name.data = semester.name
    return render_template('basic-forms/semester/update.html', title='Semester Duplication Update', form=form)

def semester_view_dlc(*args, **kwargs):
    id = request.view_args['id']
    semester = Semester.query.get_or_404(id)
    return [{'text': 'S '+str(semester.get_nbr()), 'url': url_for('semester_view', id=id)}]

@app.route('/semester/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.semester.view', '', dynamic_list_constructor=semester_view_dlc)
def semester_view(id):
    semester = Semester.query.get_or_404(id)
    return render_template('basic-forms/semester/view.html', title='Semester View', semester=semester)

# WARNING: i have to check before i delete
@app.route('/semester/delete/<int:id>/', methods=['GET', 'POST'])
def semester_delete(id):
    semester = Semester.query.get_or_404(id)
    if len(semester.sessions) > 0:
        flash("you can't delete this Semester because it is in Relation with other Records", 'alert-danger')
        flash("you have to break the relation with the Sessions first")
        return redirect(url_for('semester_view', id=id))
    db.session.delete(semester)
    db.session.commit()
    flash('Semester: ' + str(semester.name) + ' is deleted', 'alert-success')
    return redirect(url_for('semester_index'))

@app.route('/semester/close/<int:id>/', methods=['GET', 'POST'])
def semester_close(id):
    semester = Semester.query.get_or_404(id)
    for parallel in semester.get_parallels():
        if parallel.is_locked() == True:
            parallel.is_closed = True
    semester.is_closed = True
    db.session.commit()
    flash("this Semester is now Closed", 'alert-success')
    return redirect(url_for('semester_view', id=id))

@app.route('/semester/open/<int:id>/', methods=['GET', 'POST'])
def semester_open(id):
    semester = Semester.query.get_or_404(id)
    for parallel in semester.get_parallels():
        if parallel.is_locked() != True:
            flash("you can have only one Open Semester at a time", "alert-danger")
            return redirect(url_for('semester_index'))
    semester.is_closed = False
    db.session.commit()
    flash("this Semester is now Open", 'alert-success')
    return redirect(url_for('semester_view', id=id))

# you can find Semester Duplication 
#     in routesConfig.py duplicate_config()


#######################################
#####             Unit            #####

@app.route('/unit/delete/<int:id>/', methods=['GET', 'POST'])
def unit_delete(id):
    unit = Module.query.get_or_404(id)
    if len(unit.grades) > 0 or len(unit.unit_sessions) > 0 or len(unit.percentages) > 0:
        flash("you can't delete this Module because it is in Relation with other Records", 'alert-danger')
        if len(unit.grades) > 0:
            flash("you have to break the relation with the Grades first")
        if len(unit.unit_sessions) > 0:
            flash("you have to break the relation with the ModuleSessions first")
        if len(unit.unit_sessions) > 0:
            flash("you have to break the relation with the ModuleSessions first")
        return redirect(url_for('unit_view', id=id))
    db.session.delete(unit)
    db.session.commit()
    flash('Module: ' + str(unit.name) + ' is deleted', 'alert-success')
    return redirect(url_for('unit_index'))


#######################################
#####          Percantage         #####


#######################################
#####            Module           #####

@app.route('/module/')
@register_breadcrumb(app, '.basic.module', 'Modules')
def module_index():
    modules = Module.query.join(Unit).join(Semester).join(Annual).join(Branch).join(School)\
        .order_by(School.name, Branch.name, Annual.annual, Semester.semester, Unit.name, Module.code).all()
    return render_template('basic-forms/module/index.html', title='Modules List', modules=modules)

@app.route('/module/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.module.create', 'Create')
def module_create():
    form = ModuleFormCreate()
    if form.validate_on_submit():
        module = Module(
            code=form.code.data, 
            name=form.name.data, 
            display_name=form.display_name.data, 
            coefficient=form.coefficient.data, 
            credit=form.credit.data, 
            time=form.credit.data, 
            order=form.credit.data, 
            unit_id=form.unit_id.data
        )
        db.session.add(module)
        db.session.commit()
        flash('Created and Saved Successfully.', 'alert-success')
        return redirect(url_for('module_view', id=module.id))
    return render_template('basic-forms/module/create.html', title='Module Create', form=form)

@app.route('/module/update/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.module.view.update', 'Update')
def module_update(id):
    module = Module.query.get_or_404(id)
    form = ModuleFormUpdate(module.id)
    if form.validate_on_submit():
        module.code = form.code.data
        module.name = form.name.data
        module.display_name = form.display_name.data
        module.coefficient = form.coefficient.data
        module.credit = form.credit.data
        module.time = form.time.data
        module.order = form.order.data
        # module.unit_id = form.unit_id.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('module_view', id=module.id))
    elif request.method == 'GET':
        form.code.data = module.code
        form.name.data = module.name
        form.display_name.data = module.display_name
        form.coefficient.data = module.coefficient
        form.credit.data = module.credit
        form.time.data = module.time
        form.order.data = module.order
        form.unit_id.data = module.unit_id
    return render_template('basic-forms/module/update.html', title='Module Update', form=form)

@app.route('/module/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.module.view', 'View')
def module_view(id):
    module = Module.query.get_or_404(id)
    return render_template('basic-forms/module/view.html', title='Module View', module=module)

@app.route('/module/delete/<int:id>/', methods=['GET', 'POST'])
def module_delete(id):
    module = Module.query.get_or_404(id)
    if len(module.grades) > 0 or len(module.module_sessions) > 0 or len(module.percentages) > 0:
        flash("you can't delete this Module because it is in Relation with other Records", 'alert-danger')
        if len(module.grades) > 0:
            flash("you have to break the relation with the Grades first")
        if len(module.module_sessions) > 0:
            flash("you have to break the relation with the ModuleSessions first")
        if len(module.module_sessions) > 0:
            flash("you have to break the relation with the ModuleSessions first")
        return redirect(url_for('module_view', id=id))
    db.session.delete(module)
    db.session.commit()
    flash('Module: ' + str(module.name) + ' is deleted', 'alert-success')
    return redirect(url_for('module_index'))


#######################################
#####            Wilaya           #####

@app.route('/wilaya/')
@register_breadcrumb(app, '.basic.wilaya', 'Wilayas')
def wilaya_index():
    wilayas = Wilaya.query.all()
    return render_template('basic-forms/wilaya/index.html', title='Wilayas List', wilayas=wilayas)

@app.route('/wilaya/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.wilaya.create', 'Create')
def wilaya_create():
    form = WilayaFormCreate()
    if form.validate_on_submit():
        wilaya = Wilaya(
            code=form.code.data, 
            name=form.name.data, 
        )
        db.session.add(wilaya)
        db.session.commit()
        flash('Created and Saved Successfully.', 'alert-success')
        return redirect(url_for('wilaya_view', id=wilaya.id))
    return render_template('basic-forms/wilaya/create.html', title='Wilaya Create', form=form)

@app.route('/wilaya/update/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.wilaya.view.update', 'Update')
def wilaya_update(id):
    wilaya = Wilaya.query.get_or_404(id)
    form = WilayaFormUpdate(wilaya.id)
    if form.validate_on_submit():
        wilaya.code = form.code.data
        wilaya.name = form.name.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('wilaya_view', id=wilaya.id))
    elif request.method == 'GET':
        form.code.data = wilaya.code
        form.name.data = wilaya.name
    return render_template('basic-forms/wilaya/update.html', title='Wilaya Update', form=form)

@app.route('/wilaya/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.wilaya.view', 'View')
def wilaya_view(id):
    wilaya = Wilaya.query.get_or_404(id)
    return render_template('basic-forms/wilaya/view.html', title='Wilaya View', wilaya=wilaya)

# WARNING: i have to check before i delete
@app.route('/wilaya/delete/<int:id>/', methods=['GET', 'POST'])
def wilaya_delete(id):
    wilaya = Wilaya.query.get_or_404(id)
    if len(wilaya.students) > 0 or len(wilaya.teachers) > 0:
        flash("you can't delete this Wilaya because it is in Relation with other Records", 'alert-danger')
        if len(wilaya.students) > 0:
            flash("you have to break the relation with the Students first")
        if len(wilaya.teachers) > 0:
            flash("you have to break the relation with the Teachers first")
        return redirect(url_for('wilaya_view', id=id))
    db.session.delete(wilaya)
    db.session.commit()
    flash('Wilaya: ' + str(wilaya.name) + ' is deleted', 'alert-success')
    return redirect(url_for('wilaya_index'))


#######################################
#####           Teacher           #####

@app.route('/teacher/')
@register_breadcrumb(app, '.basic.teacher', 'Teachers')
def teacher_index():
    teachers = Teacher.query.all()
    return render_template('basic-forms/teacher/index.html', title='Teachers List', teachers=teachers)

@app.route('/teacher/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.teacher.create', 'Create')
def teacher_create():
    form = TeacherFormCreate()
    if form.validate_on_submit():
        teacher = Teacher(
            username=form.username.data,
            last_name=form.last_name.data, 
            first_name=form.first_name.data,
            # last_name_arab=form.last_name_arab.data,
            # first_name_arab=form.first_name_arab.data,
            email=form.email.data,
            birth_date=form.birth_date.data,
            birth_place=form.birth_place.data,
            address=form.address.data,
            wilaya_id=form.wilaya_id.data,
            sex=form.sex.data,
            phone=form.phone.data
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Created and Saved Successfully.', 'alert-success')
        return redirect(url_for('teacher_view', id=teacher.id))
    return render_template('basic-forms/teacher/create.html', title='Teacher Create', form=form)

@app.route('/teacher/update/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.teacher.view.update', 'Update')
def teacher_update(id):
    teacher = Teacher.query.get_or_404(id)
    form = TeacherFormUpdate(teacher.id)
    if form.validate_on_submit():
        teacher.username = form.username.data
        teacher.last_name = form.last_name.data
        teacher.first_name = form.first_name.data
        # teacher.last_name_arab = form.last_name_arab.data
        # teacher.first_name_arab = form.first_name_arab.data
        if len(form.email.data) > 0:
            teacher.email = form.email.data
        teacher.birth_date = form.birth_date.data
        teacher.birth_place = form.birth_place.data
        teacher.address = form.address.data
        teacher.wilaya_id = form.wilaya_id.data
        teacher.sex = form.sex.data
        teacher.phone = form.phone.data
        db.session.commit()
        flash('Your changes have been saved.', 'alert-success')
        return redirect(url_for('teacher_view', id=teacher.id))
    elif request.method == 'GET':
        form.username.data = teacher.username
        form.last_name.data = teacher.last_name
        form.first_name.data = teacher.first_name
        # form.last_name_arab.data = teacher.last_name_arab
        # form.first_name_arab.data = teacher.first_name_arab
        form.email.data = teacher.email
        form.birth_date.data = teacher.birth_date
        form.birth_place.data = teacher.birth_place
        form.address.data = teacher.address
        form.wilaya_id.data = teacher.wilaya_id
        form.sex.data = teacher.sex
        form.phone.data = teacher.phone
    return render_template('basic-forms/teacher/update.html', title='Teacher Update', form=form)

@app.route('/teacher/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.teacher.view', 'View')
def teacher_view(id):
    teacher = Teacher.query.get_or_404(id)
    return render_template('basic-forms/teacher/view.html', title='Teacher View', teacher=teacher)

# WARNING: i have to check before i delete
@app.route('/teacher/delete/<int:id>/', methods=['GET', 'POST'])
def teacher_delete(id):
    teacher = Teacher.query.get_or_404(id)
    if len(teacher.module_sessions) > 0 or len(teacher.teacher_attendances) > 0:
        flash("you can't delete this Teacher because it is in Relation with other Records", 'alert-danger')
        if len(teacher.module_sessions) > 0:
            flash("you have to break the relation with the Module Sessions first")
        if len(teacher.teacher_attendances) > 0:
            flash("you have to break the relation with the Teacher Attendances first")
        return redirect(url_for('teacher_view', id=id))
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher: ' + str(teacher.name) + ' is deleted', 'alert-success')
    return redirect(url_for('teacher_index'))

