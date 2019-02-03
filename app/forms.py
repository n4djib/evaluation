from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, ValidationError, Optional, EqualTo
# from wtforms import DateField
from wtforms.fields.html5 import DateField

# from flask_admin import BaseView
from flask_admin.form import widgets
# from flask_admin.form import DatePickerWidget

from app.models import Student, User, School, Branch, Wilaya, Promo
from sqlalchemy import and_
# from datetime import datetime



class StudentFormBase(FlaskForm):
    branch_id = SelectField('Branch', coerce=int,  
        choices = [('-1', '')]+[(b.id, b.name+' - '+b.description ) for b in Branch.query.order_by('name')
    ])
    username = StringField('Username', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name_arab = StringField('اللقب بالعربية', validators=[Optional()])
    first_name_arab = StringField('الاسم بالعربية', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    birth_date = DateField('Birth Date', validators=[Optional()])
    birth_place = StringField('Birth Place')
    wilaya_id = SelectField('Wilaya', coerce=int, 
        choices = [(-1, '')]+[(b.id, b.name) for b in Wilaya.query.order_by('code')
    ])
    address = StringField('Address')
    sex = SelectField('Sex', choices = [('', ''), ('F', 'F'), ('M', 'M')])
    residency = SelectField('Residency', choices = [('', ''), ('intern', 'Intern'), ('extern', 'Extern')])

class StudentFormCreate(StudentFormBase):
    submit = SubmitField('Create')
    def validate_username(self, username):
        student = Student.query.filter_by(username=username.data).first()
        if student is not None:
            raise ValidationError('Please use a different username.')
    # def validate_email(self, email):
    #     student = Student.query.filter_by(email=email.data).first()
    #     if student is not None:
    #         raise ValidationError('Please use a different email.')

class StudentFormUpdate(StudentFormBase):
    submit = SubmitField('Update')
    def __init__(self, _id=-1, *args, **kwargs):
        super(StudentFormUpdate, self).__init__(*args, **kwargs)
        self._id = _id
    def validate_username(self, username):
        student = Student.query.filter(and_(Student.username==username.data, Student.id!=self._id)).first()
        if student is not None:
            raise ValidationError('Please use a different username')
    # def validate_email(self, email):
    #     student = Student.query.filter(and_(Student.email==email.data, Student.id!=self._id)).first()
    #     if student is not None:
    #         raise ValidationError('Please use a different email')


##################

class SchoolFormBase(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description')

class SchoolFormCreate(SchoolFormBase):
    submit = SubmitField('Create')

class SchoolFormUpdate(SchoolFormBase):
    submit = SubmitField('Update')
    def __init__(self, _id=-1, *args, **kwargs):
        super(SchoolFormUpdate, self).__init__(*args, **kwargs)
        self._id = _id

##################

class BranchFormBase(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description')
    school_id = SelectField('School', coerce=int,  
        choices = [('-1', '')]+[(s.id, s.get_label()) for s in School.query.order_by('name')
    ])

class BranchFormCreate(BranchFormBase):
    submit = SubmitField('Create')

class BranchFormUpdate(BranchFormBase):
    submit = SubmitField('Update')
    def __init__(self, _id=-1, *args, **kwargs):
        super(BranchFormUpdate, self).__init__(*args, **kwargs)
        self._id = _id

##################

class PromoFormBase(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    display_name = StringField('display_name')
    # format='%Y-%m-%d'  format='%Y-%m-%d'  default=datetime.today, format='%d/%m/%Y'
    start_date = DateField('Start Date', validators=[Optional()])
    finish_date = DateField('Finish Date', validators=[Optional()])
    #
    # WARNING
    # i have to select branches in this school
    # in the form i need to choose the school and then the branch
    branch_id = SelectField('Branch', coerce=int,  
        choices = [('-1', '')]+[(b.id, b.get_label()) for b in Branch.query.order_by('name')
    ])
    color = StringField('Color', default="#333333")
    
class PromoFormCreate(PromoFormBase):
    submit = SubmitField('Create')

class PromoFormUpdate(PromoFormBase):
    branch_id = SelectField('Branch', 
        coerce=int, validators=[Optional()], render_kw={'disabled':''}, 
        choices = [('-1', '')]+[(b.id, b.get_label()) for b in Branch.query.order_by('name')
    ])
    submit = SubmitField('Update')
    def __init__(self, _id=-1, *args, **kwargs):
        super(PromoFormUpdate, self).__init__(*args, **kwargs)
        self._id = _id

##################

class WilayaFormBase(FlaskForm):
    code = StringField('code', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])

class WilayaFormCreate(WilayaFormBase):
    submit = SubmitField('Create')
    def validate_code(self, code):
        wilaya = Wilaya.query.filter(Wilaya.code==code.data).first()
        if wilaya is not None:
            raise ValidationError('Please use a different code')
    def validate_name(self, name):
        wilaya = Wilaya.query.filter(Wilaya.name==name.data).first()
        if wilaya is not None:
            raise ValidationError('Please use a different name')

class WilayaFormUpdate(WilayaFormBase):
    submit = SubmitField('Update')
    def __init__(self, _id=-1, *args, **kwargs):
        super(WilayaFormUpdate, self).__init__(*args, **kwargs)
        self._id = _id
    def validate_code(self, code):
        wilaya = Wilaya.query.filter(and_(Wilaya.code==code.data, Wilaya.id!=self._id)).first()
        if wilaya is not None:
            raise ValidationError('Please use a different code')
    def validate_name(self, name):
        wilaya = Wilaya.query.filter(and_(Wilaya.name==name.data, Wilaya.id!=self._id)).first()
        if wilaya is not None:
            raise ValidationError('Please use a different name')

##################
##################
##################

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

##################
##################
##################
