from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(150))
    branches = db.relationship('Branch', back_populates='school')
    def __repr__(self):
        return '<School {}>'.format(self.name)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(150))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    students = db.relationship('Student', backref='branch', lazy='dynamic')
    school = db.relationship("School", back_populates="branches")

    semesters = db.relationship('Semester', back_populates='branch')
    promos = db.relationship('Promo', back_populates='branch')
    def __repr__(self):
        return '<Branch {}>'.format(self.name)

class Promo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    finish_date = db.Column(db.Date)

    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    branch = db.relationship('Branch', back_populates='promos')

    # sessions = db.relationship('Session', back_populates='promo', order_by="Session.start_date")
    sessions = db.relationship('Session', back_populates='promo')
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # year = db.Column(db.Integer)
    name = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    finish_date = db.Column(db.Date)
    is_rattrapage = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    configuration = db.Column(db.Text)

    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    semester = db.relationship('Semester', back_populates='sessions')
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'))
    promo = db.relationship('Promo', back_populates='sessions')

    prev_session = db.Column(db.Integer, db.ForeignKey('session.id'))
    # previous = db.relationship('Session', backref='prev_session', lazy='dynamic')
    # previous = db.relationship('Session', back_populates='session')
    
    student_sessions = db.relationship('StudentSession', back_populates='session')
    def student_nbr(self):
        return StudentSession.query.filter_by(session_id=self.id).count()

class StudentSession(db.Model):
    __tablename__ = 'student_session'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)

    student = db.relationship("Student", back_populates="student_sessions")
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    session = db.relationship('Session', back_populates='student_sessions')

    grades = db.relationship('Grade', back_populates='student_session')
    grades_unit = db.relationship('GradeUnit', back_populates='student_session')
    # grades_semester = db.relationship('GradeSemester', back_populates='student_session')

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cour = db.Column(db.Numeric(10,2))
    td = db.Column(db.Numeric(10,2))
    tp = db.Column(db.Numeric(10,2))
    t_pers = db.Column(db.Numeric(10,2))
    stage = db.Column(db.Numeric(10,2))

    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    formula = db.Column(db.String(200))
    # fields = db.Column(db.String(50))

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module = db.relationship('Module', back_populates='grades')
    student_session_id = db.Column(db.Integer, db.ForeignKey('student_session.id'))
    student_session = db.relationship('StudentSession', back_populates='grades')
    def __repr__(self):
        return '<{} - {} - {}>'.format(self.id, self.student_session_id, self.cour)
    def get_student_name(self):
        s = self.student_session.student
        return s.username + ' - ' + s.last_name + ' - ' + s.first_name

class GradeUnit(db.Model):
    __tablename__ = 'grade_unit'
    id = db.Column(db.Integer, primary_key=True)
    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    unit_coefficient = db.Column(db.Integer())
    is_fondamental = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    unit = db.relationship('Unit', back_populates='grade_units')
    student_session_id = db.Column(db.Integer, db.ForeignKey('student_session.id'))
    student_session = db.relationship('StudentSession', back_populates='grades_unit')

### Creating Configuration Tables ###
class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    credit_formula = db.Column(db.String(250))
    year = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    units = db.relationship('Unit', back_populates='semester', order_by="Unit.order")
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    branch = db.relationship('Branch', back_populates='semesters')
    sessions = db.relationship('Session', back_populates='semester')
    prev_semester = db.Column(db.Integer, db.ForeignKey('semester.id'))
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)
    def get_nbr(self):
        return self.year * 2 - 2 + self.semester
    def get_semester_cumul_coeff(self):
        units = self.units
        coeff = 0
        for unit in units:
            coeff = coeff + unit.unit_coefficient
        return coeff
    def get_semester_cumul_credit(self):
        units = self.units
        credit = 0
        for unit in units:
            credit = credit + unit.get_unit_cumul_credit()
        return credit

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    unit_coefficient = db.Column(db.Integer())
    is_fondamental = db.Column(db.Boolean, default=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    semester = db.relationship('Semester', back_populates='units')
    modules = db.relationship('Module', back_populates='unit', order_by="Module.order")
    grade_units = db.relationship('GradeUnit', back_populates='unit')
    order = db.Column(db.Integer())
    def __repr__(self):
        return '<Unit {}>'.format(self.name)
    def get_unit_cumul_coeff(self):
        modules = self.modules
        coeff = 0
        for module in modules:
            coeff = coeff + module.coefficient
        return coeff
    def get_unit_cumul_credit(self):
        modules = self.modules
        credit = 0
        for module in modules:
            credit = credit + module.credit
        return credit

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    coefficient = db.Column(db.Integer())
    credit = db.Column(db.Integer())
    time = db.Column(db.Numeric(10,2))
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    unit = db.relationship('Unit', back_populates='modules')
    percentages = db.relationship('Percentage', backref='module', lazy='dynamic')
    grades = db.relationship('Grade', back_populates='module')
    order = db.Column(db.Integer())
    def __repr__(self):
        return '<Module {}>'.format(self.name)

class Percentage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    percentage = db.Column(db.Numeric(10,2))
    time = db.Column(db.Numeric(10,2))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    type_name = db.relationship('Type', back_populates='percentages')
    # def __repr__(self):
    #     return '<Unit {}>'.format(self.name)

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(45))
    grade_table_field = db.Column(db.String(45))
    percentages = db.relationship('Percentage', back_populates='type_name')
    def __repr__(self):
        return '<Type {}>'.format(self.type)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True) # matricule
    last_name = db.Column(db.String(45), index=True)
    first_name = db.Column(db.String(45), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    birth_date = db.Column(db.Date)
    birth_wilaya = db.Column(db.String(45))
    birth_place = db.Column(db.String(45))
    address =  db.Column(db.String(120))
    photo = db.Column(db.String(250))
    sex = db.Column(db.String(20))
    phones = db.relationship('Phone', backref='student', lazy='dynamic')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    student_sessions = db.relationship('StudentSession', back_populates='student')
    def __repr__(self):
        return '<{} - {}>'.format(self.username, self.last_name)

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    phone = db.Column(db.String(45))
    type = db.Column(db.String(45))
    def __repr__(self):
        return '<Phone: id = {} | student_id = {} | phone = {}>'.format(self.id, self.student_id, self.phone)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<User: id = {} | username = {} | email = {}>'.format(self.id, self.username, self.email)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
