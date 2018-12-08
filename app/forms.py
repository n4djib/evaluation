from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, ValidationError, Optional, EqualTo
from wtforms.fields.html5 import DateField
from app.models import Student, User, School, Branch, Wilaya, Promo
from sqlalchemy import and_

# from sqlalchemy_utils import ColorType



class StudentFormBase(FlaskForm):
    branch_id = SelectField('Branch', coerce=int,  
        choices = [('-1', '')]+[(b.id, b.name+' - '+b.description ) for b in Branch.query.order_by('name')
    ])
    username = StringField('Username', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    email = StringField('Email', validators=[Optional(), Email()])
    birth_date = DateField('Birth Date', validators=[Optional()])
    birth_place = StringField('Birth Place')
    wilaya_id = SelectField('Wilaya', coerce=int, validators=[Optional()], 
        choices = [('-1', '')]+[(b.id, b.name) for b in Wilaya.query.order_by('code')
    ])
    address = StringField('Address')

class StudentFormCreate(StudentFormBase):
    submit = SubmitField('Create')
    def validate_username(self, username):
        student = Student.query.filter_by(username=username.data).first()
        if student is not None:
            raise ValidationError('Please use a different username.')
    def validate_email(self, email):
        student = Student.query.filter_by(email=email.data).first()
        if student is not None:
            raise ValidationError('Please use a different email.')

class StudentFormUpdate(StudentFormBase):
    submit = SubmitField('Update')
    def __init__(self, _id=-1, *args, **kwargs):
        super(StudentFormUpdate, self).__init__(*args, **kwargs)
        self._id = _id
    def validate_username(self, username):
        student = Student.query.filter( and_(Student.username == username.data , Student.id != self._id) ).first()
        if student is not None:
            raise ValidationError('Please use a different username')
    def validate_email(self, email):
        student = Student.query.filter( and_(Student.email == email.data , Student.id != self._id) ).first()
        if student is not None:
            raise ValidationError('Please use a different email')



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
        choices = [('-1', '')]+[(s.id, s.name+' - '+s.description ) for s in School.query.order_by('name')
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
    # color = ColorField('Color')
    # , format='%d/%m/%Y'
    start_date = DateField('Start Date', validators=[Optional()])
    finish_date = DateField('Finish Date', validators=[Optional()])
    branch_id = SelectField('Branch', coerce=int,  
        choices = [('-1', '')]+[(b.id, b.name+' - '+b.description ) for b in Branch.query.order_by('name')
    ])

class PromoFormCreate(PromoFormBase):
    submit = SubmitField('Create')

class PromoFormUpdate(PromoFormBase):
    branch_id = SelectField('Branch', 
        coerce=int, validators=[Optional()], render_kw={'disabled':''}, 
        choices = [('-1', '')]+[(b.id, b.name+' - '+b.description) for b in Branch.query.order_by('name')
    ])
    submit = SubmitField('Update')
    def __init__(self, _id=-1, *args, **kwargs):
        super(PromoFormUpdate, self).__init__(*args, **kwargs)
        self._id = _id



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


#
