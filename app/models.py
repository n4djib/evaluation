from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from decimal import *


# FIX:  = db.Column(db.String(64), index=True, unique=True)

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.String(150))
    branches = db.relationship('Branch', back_populates='school')
    def __repr__(self):
        return '<School {}>'.format(self.name)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.String(150))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    school = db.relationship("School", back_populates="branches")

    students = db.relationship('Student', backref='branch', lazy='dynamic')
    semesters = db.relationship('Semester', back_populates='branch')
    promos = db.relationship('Promo', back_populates='branch')
    def __repr__(self):
        return '<Branch {}>'.format(self.name)

class Promo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), index=True, unique=True)
    display_name = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    finish_date = db.Column(db.Date)

    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    branch = db.relationship('Branch', back_populates='promos')
    # sessions = db.relationship('Session', back_populates='promo', order_by="Session.start_date")
    sessions = db.relationship('Session', back_populates='promo')
    # annual_sessions = db.relationship('AnnualSession', backref='promo', lazy='dynamic')
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)



class AnnualSession(db.Model):
    __tablename__ = 'annual_session'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    is_rattrapage = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'))
    # promo = db.relationship('Promo', ***************)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)

class GradeAnnual(db.Model):
    __tablename__ = 'grade_annual'
    id = db.Column(db.Integer, primary_key=True)
    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    annual_session_id = db.Column(db.Integer, db.ForeignKey('annual_session.id'))
    annual_session = db.relationship('AnnualSession', backref='annual_grade')

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
    student_sessions = db.relationship('StudentSession', back_populates='session')

    annual_session_id = db.Column(db.Integer, db.ForeignKey('annual_session.id'))
    annual_session = db.relationship('AnnualSession', backref='session')
    def student_nbr(self):
        return StudentSession.query.filter_by(session_id=self.id).count()

    def get_previous(self):
        sessions = self.get_chain()
        index = sessions.index(self.id)
        if index == 0:
            return None
        # return sessions[index-1]
        return Session.query.get(sessions[index-1])

    def get_next(self):
        sessions = self.get_chain()
        index = sessions.index(self.id)
        if index == len(sessions)-1:
            return None
        return Session.query.get(sessions[index+1])

    def get_chain(self):
        sessions = Session.query.filter_by(promo_id=self.promo.id).join(Semester)\
            .order_by(Semester.annual, Semester.semester).all()
        sessions_id = []
        for session in sessions:
            sessions_id.append(session.id)
        return sessions_id

    def get_annual_chain(self):
        sessions = Session.query.filter_by(promo_id=self.promo.id).join(Semester)\
            .order_by(Semester.annual, Semester.semester).all()
        current_annual = self.semester.annual
        sessions_id = []
        for session in sessions:
            if session.semester.annual == current_annual:
                sessions_id.append(session.id)
        return sessions_id
        
    def get_annual_dict(self):
        chain = self.get_annual_chain()
        _dict = {'S1': -1, 'S2': -1, 'R1': -1, 'R2': -1, 'A': -1}
        for session_id in chain:
            session = Session.query.filter_by(id=session_id).first()
            is_rattrapage = session.is_rattrapage
            semester_half = session.semester.semester

            if is_rattrapage != True and semester_half == 1:
                _dict['S1'] = session.id
            if is_rattrapage != True and semester_half == 2:
                _dict['S2'] = session.id
            if is_rattrapage == True and semester_half == 1:
                _dict['R1'] = session.id
            if is_rattrapage == True and semester_half == 2:
                _dict['R2'] = session.id

        if self.annual_session_id != None:
            _dict['A'] = self.annual_session_id
        return _dict

class StudentSession(db.Model):
    __tablename__ = 'student_session'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    calculation = db.Column(db.String(100))

    student = db.relationship("Student", back_populates="student_sessions")
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    session = db.relationship('Session', back_populates='student_sessions')

    grades = db.relationship('Grade', back_populates='student_session')
    grades_unit = db.relationship('GradeUnit', back_populates='student_session')
    # grades_semester = db.relationship('GradeSemester', back_populates='student_session')

    def calculate(self, grades_unit=None):
        if grades_unit is None:
            grades_unit = self.grades_unit

        cumul_semester_coeff = self.session.semester.get_semester_cumul_coeff()
        cumul_semester_credit = self.session.semester.get_semester_cumul_credit()

        fondamental_unit_average = 0
        unit_fondamental_id = None

        average = 0
        credit = 0
        calculation = ''
        for grade_unit in grades_unit:
            avrg = grade_unit.average

            if grade_unit.is_fondamental == True:
                fondamental_unit_credit = grade_unit.credit
                unit_fondamental_id = grade_unit.unit_id
            if avrg == None:
                average = None
                break

            unit = Unit.query.filter_by(id=grade_unit.unit_id).first()
            unit_coefficient = unit.unit_coefficient
            average += round(avrg * unit_coefficient / cumul_semester_coeff, 2)
            credit += grade_unit.credit
            calculation += str(avrg) + ' * ' + str(unit_coefficient) + ' + '

        if average == None:
            self.average = None
            self.credit = None
            self.calculation = ''
        else:
            self.average = average
            unit_fondamental = Unit.query.filter_by(id=unit_fondamental_id).first()
            if average >= 10 and fondamental_unit_credit == unit_fondamental.get_unit_cumul_credit():
                credit = cumul_semester_credit
            
            self.credit = credit
            calculation = calculation[:-3]
            calculation = '(' + calculation + ') / ' + str(cumul_semester_coeff)
            self.calculation = calculation
        return 'semester calculated'

class GradeUnit(db.Model):
    __tablename__ = 'grade_unit'
    id = db.Column(db.Integer, primary_key=True)
    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    calculation = db.Column(db.String(100))

    unit_coefficient = db.Column(db.Integer())
    is_fondamental = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    unit = db.relationship('Unit', back_populates='grade_units')
    student_session_id = db.Column(db.Integer, db.ForeignKey('student_session.id'))
    student_session = db.relationship('StudentSession', back_populates='grades_unit')

    def calculate(self, grades=None):
        # grades in a one grade_unit
        if grades is None:
            grades = Grade.query.filter_by(student_session_id=self.student_session_id)\
                .join(Module).filter_by(unit_id=self.unit_id).all()

        cumul_unit_coeff = self.unit.get_unit_cumul_coeff()
        cumul_unit_credit = self.unit.get_unit_cumul_credit()
        average = 0
        credit = 0
        calculation = ''
        for grade in grades:
            if grade.average == None:
                average = None
                break
            coefficient = grade.module.coefficient
            average += round(grade.average * coefficient / cumul_unit_coeff, 2)
            credit += grade.credit
            calculation += str(grade.average) + ' * ' + str(coefficient) + ' + '

        self.average = average
        if average == None:
            self.credit = None
            self.calculation = ''
        else:
            self.average = average
            if self.average >= 10 and self.is_fondamental == False:
                self.credit = cumul_unit_credit
            else:
                self.credit = credit

            calculation = calculation[:-3]
            calculation = '(' + calculation + ') / ' + str(cumul_unit_coeff)
            # self.calculation = calculation + ' = ' + str(average)
            self.calculation = calculation
        return 'unit calculated'

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
    calculation = db.Column(db.String(100))

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

    def calculate(self):
        formula = self.formula
        dictionary = eval(formula)
        average = 0
        calculation = ''
        for field in dictionary:
            if field in ['cour', 'td', 'tp', 't_pers', 'stage']:
                val = getattr(self, field)
                percentage = dictionary[field]
                if val == None:
                    average = None
                    break
                getcontext().prec = 4
                average += round( val * Decimal(percentage) , 2)

                calculation += str(field) + ': ' + str(val) + ' * ' + str(percentage) + ' + '
        
        # if average != None:
        #     calculation += '= ' + str(average)
        #     calculation = calculation.replace('+ =', '=')
        # else:
        #     calculation = None
        calculation = calculation[:-3]

        credit = None
        if average != None:
            if average >= 10:
                credit = dictionary['credit']
            else:
                credit = 0

        self.average = average
        self.credit = credit
        self.calculation = calculation
        return 'grade calculated'


### Creating Configuration Tables ###
class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    # credit_formula = db.Column(db.String(250))
    annual = db.Column(db.Integer)
    semester = db.Column(db.Integer)

    units = db.relationship('Unit', back_populates='semester', order_by="Unit.order")

    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    branch = db.relationship('Branch', back_populates='semesters')
    sessions = db.relationship('Session', back_populates='semester')
    prev_semester = db.Column(db.Integer, db.ForeignKey('semester.id'))
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)
    def get_nbr(self):
        return (self.annual * 2) - 2 + self.semester
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
    def get_previous(self):
        # if it returns many you shoold raise an exception
        return Semester.query.filter_by(id=self.prev_semester).first()
    def get_next(self):
        return Semester.query.filter_by(prev_semester=self.id).first()
    def get_chain_before(self):
        _list = []
        prv = self.get_previous()
        if prv != None:
            _list += prv.get_chain_before() + [prv.id]
        return _list
    def get_chain_after(self):
        _list = []
        nxt = self.get_next()
        if nxt != None:
            _list += [nxt.id] + nxt.get_chain_after()
        return _list
    def get_chain(self):
        return self.get_chain_before() + [self.id] + self.get_chain_after()
    def get_annual_chain(self):
        if self.semester == 1:
            return [self.id, self.get_next().id]
        if self.semester == 2:
            return [self.get_previous().id, self.id]
        raise ValueError('Semester -> get_annual_chain -> year and semester must be Initialized')
    def config_dict(self):
        semesters = {'s_id': self.id, 'name': self.name, 'display_name': self.display_name}
        for unit in self.units:
            semesters.setdefault('units', []).append(unit.config_dict())
        return semesters

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    unit_coefficient = db.Column(db.Integer)
    is_fondamental = db.Column(db.Boolean, default=False)

    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    semester = db.relationship('Semester', back_populates='units')

    modules = db.relationship('Module', back_populates='unit', order_by="Module.order")

    grade_units = db.relationship('GradeUnit', back_populates='unit')
    order = db.Column(db.Integer)
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
    def config_dict(self):
        units = {'u_id': self.id, 'name': self.name, 'display_name': self.display_name, 'coeff': self.unit_coefficient, 'is_fondamental': self.is_fondamental, 
            'unit_coeff': self.get_unit_cumul_coeff(), 'unit_credit': self.get_unit_cumul_credit() }
        for module in self.modules:
            units.setdefault('modules', []).append(module.config_dict())
        return units

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    coefficient = db.Column(db.Integer)
    credit = db.Column(db.Integer)
    time = db.Column(db.Numeric(10,2))

    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    unit = db.relationship('Unit', back_populates='modules')

    percentages = db.relationship('Percentage', backref='module', lazy='dynamic')

    grades = db.relationship('Grade', back_populates='module')
    order = db.Column(db.Integer)
    def __repr__(self):
        return '<Module {}>'.format(self.name)
    def config_dict(self):
        modules = {'m_id': self.id, 'name': self.name, 'display_name': self.display_name, 'coeff': self.coefficient, 'credit': self.credit}
        for percentage in self.percentages:
            modules.setdefault('percentages', []).append(percentage.config_dict())
        return modules

class Percentage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    percentage = db.Column(db.Numeric(10,2))
    time = db.Column(db.Numeric(10,2))

    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    type_name = db.relationship('Type', back_populates='percentages')
    def config_dict(self):
        type = Type.query.filter_by(id=self.type_id).first()
        return {'type': type.type, 'per': str(self.percentage)} 

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
        return '<{} - {} - {}>'.format(self.id, self.username, self.last_name)
    # @staticmethod
    def find(id):
        return db.session.query(Student).filter_by(id=id).one()

    # take into considiration many users getting the same Matricule
    # maybe you have to lock
    @staticmethod
    def get_username(bransh, year, seperator='/'):
        username_start = bransh + seperator + year + seperator
        # username_start = username_start
        student = Student.query.order_by(Student.username.desc()).filter(
            Student.username.like(username_start + '%')).first()
        # student = Student.query.order_by(Student.username.desc()).filter(Student.username.like('SF/2017%')).first()
        if student == None:
            return username_start + '01'
            
        # username = student.username.lower()
        last =''
        try:
            last = int( student.username.lower().replace(username_start.lower(), '') )
        except:
            last = 0
        _next = last + 1
        username_end = ''
        if _next < 10:
            username_end = '0' + str(_next)
        else:
            username_end = str(_next)
        return username_start + username_end

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
