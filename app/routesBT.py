from app import app, db
from flask import render_template, redirect, url_for, flash, request
from app.forms import SchoolFormCreate, SchoolFormUpdate, PromoFormCreate, PromoFormUpdate\
    , BranchFormCreate, BranchFormUpdate, WilayaFormCreate, WilayaFormUpdate
from app.models import School, Branch, Wilaya, Promo

from flask_breadcrumbs import register_breadcrumb




#######################################
#####            INDEX            #####

@app.route('/basic-tables/')
# @app.route('/basic/index/')
@register_breadcrumb(app, '.basic', 'Basic Tables')
def basic_index():
    return render_template('basic-forms/index.html', title='Basic Tables List')



#######################################
#####           School            #####

@app.route('/school/')
# @app.route('/school/index/')
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
@register_breadcrumb(app, '.basic.school.update', 'Update')
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
# @app.route('/school/view/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.school.view', 'View')
def school_view(id):
    school = School.query.get_or_404(id)
    return render_template('basic-forms/school/view.html', title='School View', school=school)

# WARNING: i have to check before i delete
@app.route('/school/delete/<int:id>/', methods=['GET', 'POST'])
def school_delete(id):
    school = School.query.get_or_404(id)
    if len(school.branches) > 0:
        flash("you can't delete this School because it is in Relation with other Records", 'alert-danger')
        flash("you have to break the relation with the branches first")
        return redirect(url_for('school_view', id=school.id))
    db.session.delete(school)
    db.session.commit()
    flash('School: ' + str(school.name) + ' is deleted', 'alert-success')
    return redirect(url_for('school_index'))



#######################################
#####           Branch            #####

@app.route('/branch/')
# @app.route('/branch/index/')
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
@register_breadcrumb(app, '.basic.branch.update', 'Update')
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
# @app.route('/branch/view/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.branch.view', 'View')
def branch_view(id):
    branch = Branch.query.get_or_404(id)
    return render_template('basic-forms/branch/view.html', title='Branch View', branch=branch)

# WARNING: i have to check before i delete
@app.route('/branch/delete/<int:id>/', methods=['GET', 'POST'])
def branch_delete(id):
    branch = Branch.query.get_or_404(id)
    if len(branch.promos) > 0 or len(branch.semesters) > 0:
        flash("you can't delete this Branch because it is in Relation with other Records", 'alert-danger')
        if len(branch.promos) > 0:
            flash("you have to break the relation with the Sessions first")
        if len(branch.semesters) > 0:
            flash("you have to break the relation with the Semesters first")
        return redirect(url_for('branch_view', id=branch.id))
    db.session.delete(branch)
    db.session.commit()
    flash('Branch: ' + str(branch.name) + ' is deleted', 'alert-success')
    return redirect(url_for('branch_index'))



#######################################
#####            Promo            #####

@app.route('/promo/')
# @app.route('/promo/index/')
@register_breadcrumb(app, '.basic.promo', 'Promos')
def promo_index():
    # i have to order by school & branch
    promos = Promo.query.order_by(Promo.branch_id).all()
    return render_template('basic-forms/promo/index.html', title='Promos List', promos=promos)

@app.route('/promo/create/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.promo.create', 'Create')
def promo_create():
    form = PromoFormCreate()
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
@register_breadcrumb(app, '.basic.promo.update', 'Update')
def promo_update(id):
    promo = Promo.query.get_or_404(id)
    form = PromoFormUpdate(promo.id)
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

# @app.route('/promo/view/<int:id>/', methods=['GET', 'POST'])
@app.route('/promo/<int:id>/', methods=['GET', 'POST'])
@register_breadcrumb(app, '.basic.promo.view', 'View')
def promo_view(id):
    promo = Promo.query.get_or_404(id)
    return render_template('basic-forms/promo/view.html', title='Promo View', promo=promo)

# WARNING: i have to check before i delete
@app.route('/promo/delete/<int:id>/', methods=['GET', 'POST'])
def promo_delete(id):
    promo = Promo.query.get_or_404(id)
    if len(promo.sessions) > 0:
        flash("you can't delete this Promo because it is in Relation with other Records", 'alert-danger')
        flash("you have to break the relation with the Sessions first")
        return redirect(url_for('promo_view', id=promo.id))
    db.session.delete(promo)
    db.session.commit()
    flash('Promo: ' + str(promo.name) + ' is deleted', 'alert-success')
    return redirect(url_for('promo_index'))



#######################################
#####           Semester          #####



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
@register_breadcrumb(app, '.basic.wilaya.update', 'Update')
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
    if len(wilaya.students) > 0:
        flash("you can't delete this Wilaya because it is in Relation with other Records", 'alert-danger')
        flash("you have to break the relation with the Students first")
        return redirect(url_for('wilaya_view', id=wilaya.id))
    db.session.delete(wilaya)
    db.session.commit()
    flash('Wilaya: ' + str(wilaya.name) + ' is deleted', 'alert-success')
    return redirect(url_for('wilaya_index'))

