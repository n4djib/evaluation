from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from decimal import *


# FIX:  = db.Column(db.String(64), index=True, unique=True)

class Promo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), index=True, unique=True)
    display_name = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    finish_date = db.Column(db.Date)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    sessions = db.relationship('Session', backref='promo')
    annual_session = db.relationship('AnnualSession', back_populates='promo')
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)
    def get_next_semester(self):
        sessions = Session.query.filter_by(promo_id=self.id, is_rattrapage=False).join(Semester)\
            .order_by(Semester.annual, Semester.semester).all()
        last_session = sessions[-1]
        next_semester = last_session.semester.get_next()
        return next_semester.get_nbr()

class AnnualSession(db.Model):
    __tablename__ = 'annual_session'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    is_closed = db.Column(db.Boolean, default=False)
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'))
    promo = db.relationship('Promo', back_populates='annual_session')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    sessions = db.relationship('Session', back_populates='annual_session')
    annual_grades = db.relationship('AnnualGrade', back_populates='annual_session')
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)
    def get_annual_dict(self):
        first_session = self.sessions[0]
        return first_session.get_annual_dict()

class AnnualGrade(db.Model):
    __tablename__ = 'annual_grade'
    id = db.Column(db.Integer, primary_key=True)

    s1 = db.Column(db.Numeric(10,2))
    c1 = db.Column(db.Integer)
    s2 = db.Column(db.Numeric(10,2))
    c2 = db.Column(db.Integer)

    rs1 = db.Column(db.Numeric(10,2))
    rc1 = db.Column(db.Integer)
    rs2 = db.Column(db.Numeric(10,2))
    rc2 = db.Column(db.Integer)

    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    average_r = db.Column(db.Numeric(10,2))
    credit_r = db.Column(db.Integer)

    saving_average = db.Column(db.Numeric(10,2))
    saving_credit = db.Column(db.Integer)

    annual_session_id = db.Column(db.Integer, db.ForeignKey('annual_session.id'))
    annual_session = db.relationship("AnnualSession", back_populates="annual_grades")
    # annual_session = db.relationship('AnnualSession', backref='annual_session')
    # annual_session = db.relationship('AnnualSession', backref='annual_grade')

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    def get_ratt_modules_list_annual_html(self):
        annual_dict = self.annual_session.get_annual_dict()

        # return str(annual_dict['S1']) + ' - ' + str(annual_dict['S2'])

        student_session_1 = StudentSession.query\
            .filter_by(session_id=annual_dict['S1'], student_id=self.student_id)\
            .first()
        student_session_2 = StudentSession.query\
            .filter_by(session_id=annual_dict['S2'], student_id=self.student_id)\
            .first()
        
        mudules_list_1 = ''
        mudules_list_2 = ''
        # mudules_list_1 = str(annual_dict['S1'])
        # mudules_list_2 = str(annual_dict['S2'])
        
        if student_session_1 != None:
            mudules_list_1 += student_session_1.get_ratt_modules_list_semester_html()
        # if student_session_2 != None:
        #     mudules_list_2 += student_session_2.get_ratt_modules_list_semester_html()
        
        return mudules_list_1 + "</br>" + mudules_list_2


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
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'))

    annual_session_id = db.Column(db.Integer, db.ForeignKey('annual_session.id'))
    annual_session = db.relationship('AnnualSession', back_populates='sessions')
    # annual_session = db.relationship('AnnualSession', backref='session')

    student_sessions = db.relationship('StudentSession', back_populates='session')

    def student_nbr(self):
        return StudentSession.query.filter_by(session_id=self.id).count()

    def get_previous(self):
        sessions = self.get_chain()
        index = sessions.index(self.id)
        if index == 0:
            return None
        return Session.query.get(sessions[index-1])

    def get_previous_normal(self):
        sessions = self.get_chain_normal()
        index = sessions.index(self.id)
        if index == 0:
            return None
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

    def get_chain_normal(self):
        sessions = Session.query.filter_by(promo_id=self.promo.id, is_rattrapage=False).join(Semester)\
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
    grade_units = db.relationship('GradeUnit', back_populates='student_session')
    # grades_semester = db.relationship('GradeSemester', back_populates='student_session')

    def calculate(self, grade_units=None):
        if grade_units is None:
            grade_units = self.grade_units

        cumul_semester_coeff = self.session.semester.get_semester_cumul_coeff()
        cumul_semester_credit = self.session.semester.get_semester_cumul_credit()

        grade_unit_fondamental = None
        average = 0
        credit = 0
        calculation = ''

        for grade_unit in grade_units:
            if grade_unit.is_fondamental == True:
                grade_unit_fondamental = grade_unit

            if grade_unit.average == None:
                average = None
                break

            unit_coefficient = grade_unit.unit.unit_coefficient
            average += round(grade_unit.average * unit_coefficient / cumul_semester_coeff, 2)
            credit += grade_unit.credit
            calculation += str(grade_unit.average) + ' * ' + str(unit_coefficient) + ' + '
        # end for


        if average == None:
            self.average = None
            self.credit = None
            self.calculation = ''
        else:
            self.average = average
            self.credit = credit
            
            if grade_unit_fondamental == None and average >= 10:
                self.credit = cumul_semester_credit

            if grade_unit_fondamental != None and average >= 10:
                unit_cumul_credit = grade_unit_fondamental.unit.get_unit_cumul_credit()
                if grade_unit_fondamental.credit == unit_cumul_credit:
                    self.credit = cumul_semester_credit

            self.calculation = '(' + calculation[:-3] + ') / ' + str(cumul_semester_coeff)
        return 'semester calculated'

    def get_ratt_modules_list_unit(self, grade_unit):
        mudules_in_unit = [module.id for module in grade_unit.unit.modules]

        grades = Grade.query.filter(Grade.module_id.in_(mudules_in_unit))\
            .join(StudentSession)\
            .filter_by(student_id=self.student_id, session_id=self.session_id).all()

        _list = []
        for grade in grades:
            if grade.credit == grade.module.credit:
                continue
            _list.append( grade.module_id )
        return _list

    def get_ratt_modules_list_semester(self):
        student_session = StudentSession.query\
            .filter_by(session_id=self.session_id, student_id=self.student_id).first()

        modules_list = []
        for g_unit in student_session.grade_units:
            if g_unit.credit == g_unit.unit.get_unit_cumul_credit():
                continue
            modules_list += self.get_ratt_modules_list_unit(g_unit)

        return modules_list

    def get_ratt_modules_list_semester_html(self):
        if self.credit >= 30:
            return ''
        modules_list = self.get_ratt_modules_list_semester()
        html = '<table>'
        for module_id in modules_list:
            module = Module.query.get(module_id)
            grade = Grade.query.filter_by(student_session_id=self.id, module_id=module_id).first()
            html += '<tr>'
            html += '<td>' + module.unit.display_name + '</td>'
            html += '<td>  ' + module.display_name + '</td>'
            html += '<td>  ' + str(grade.average) + '</td>'
            # html += '<td> ' + str(grade.credit) + '</td>'
            html += '</tr>'

        html += '</table>'

        return html

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
    student_session = db.relationship('StudentSession', back_populates='grade_units')

    def calculate(self, grades=None):
        # grades in a one grade_unit
        if grades is None:
            grades = Grade.query.filter_by(student_session_id=self.student_session_id)\
                .join(Module).filter_by(unit_id=self.unit_id).all()
            # why didn't i use 
            # grades = self.student_session.grades

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
            self.credit = credit
            if self.average >= 10 and self.is_fondamental == False:
                self.credit = cumul_unit_credit

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
    is_rattrapage = db.Column(db.Boolean, default=False)

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

                calculation += '('+ str(field) + ': ' + str(val) + ' * ' + str(percentage) + ')' + ' + '
        
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

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.String(150))
    branches = db.relationship('Branch', backref='school')
    def __repr__(self):
        return '<School {}>'.format(self.name)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.String(150))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    students = db.relationship('Student', backref='branch')
    semesters = db.relationship('Semester', backref='branch')
    promos = db.relationship('Promo', backref='branch')
    def __repr__(self):
        return '<Branch {}>'.format(self.name)

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    annual = db.Column(db.Integer)
    semester = db.Column(db.Integer)

    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    prev_semester = db.Column(db.Integer, db.ForeignKey('semester.id'))

    next_semester = db.relationship('Semester')
    units = db.relationship('Unit', backref='semester', order_by="Unit.order")
    sessions = db.relationship('Session', backref='semester')
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
    def has_fondamental(self):
        units = self.units
        for unit in units:
            if unit.is_fondamental == True:
                return True
        return False
        

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    unit_coefficient = db.Column(db.Integer)
    is_fondamental = db.Column(db.Boolean, default=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    order = db.Column(db.Integer)

    modules = db.relationship('Module', backref='unit', order_by="Module.order")
    grade_units = db.relationship('GradeUnit', back_populates='unit')
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
    code = db.Column(db.String(20))
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    coefficient = db.Column(db.Integer)
    credit = db.Column(db.Integer)
    time = db.Column(db.Numeric(10,2))
    order = db.Column(db.Integer)

    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))

    percentages = db.relationship('Percentage', backref='module')

    grades = db.relationship('Grade', back_populates='module')
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
    # type_name = db.relationship('Type', back_populates='percentages')
    def config_dict(self):
        type = Type.query.filter_by(id=self.type_id).first()
        return {'type': type.type, 'per': str(self.percentage)} 

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(45))
    grade_table_field = db.Column(db.String(45))
    # percentages = db.relationship('Percentage', back_populates='type_name')
    # percentages = db.relationship('Percentage', backref='type_name')
    def __repr__(self):
        return '<Type {}>'.format(self.type)


class Wilaya(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), index=True, unique=True)
    name = db.Column(db.String(100), index=True, unique=True)
    students = db.relationship('Student', backref='wilaya')
    def __repr__(self):
        return '<Wilaya {}>'.format(self.name)
    def get_label(self):
        # return self.code + ' - ' + self.name
        return self.name

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True) # matricule
    last_name = db.Column(db.String(45), index=True)
    first_name = db.Column(db.String(45), index=True)
    # email = db.Column(db.String(120), index=True, unique=True)
    email = db.Column(db.String(120), index=True)
    birth_date = db.Column(db.Date)
    birth_place = db.Column(db.String(45))
    address =  db.Column(db.String(120))
    photo = db.Column(db.String(250))
    
    sex = db.Column(db.String(20))
    phones = db.relationship('Phone', backref='student')

    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    wilaya_id = db.Column(db.Integer, db.ForeignKey('wilaya.id'))
    student_sessions = db.relationship('StudentSession', back_populates='student')

    annual_grades = db.relationship('AnnualGrade', backref='student')

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
