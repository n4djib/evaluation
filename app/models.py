from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy.event import listen
from decimal import *
from sqlalchemy import or_
from app._shared_functions import extract_fields, check_grades_status
from flask import flash

# FIX:  = db.Column(db.String(64), index=True, unique=True)

# add cascade to foreign keys
#   https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete

# 
#






# # aaaaaa
# class Aaaaaa(db.Model):
#     __tablename__ = 'aaaaaa'
#     id = db.Column(db.Integer, primary_key=True)
#     student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
#     username = db.Column(db.String(20), index=True, unique=True) # matricule
#     last_name = db.Column(db.String(45), index=True)
#     first_name = db.Column(db.String(45), index=True)
#     # student = db.relationship("Student", back_populates="aaaaaa")
#     a1 = db.Column(db.Numeric(10,2))
#     c1 = db.Column(db.Integer)
#     s1 = db.Column(db.Integer)
#     a2 = db.Column(db.Numeric(10,2))
#     c2 = db.Column(db.Integer)
#     s2 = db.Column(db.Integer)
#     a3 = db.Column(db.Numeric(10,2))
#     c3 = db.Column(db.Integer)
#     s3 = db.Column(db.Integer)
#     a4 = db.Column(db.Numeric(10,2))
#     c4 = db.Column(db.Integer)
#     s4 = db.Column(db.Integer)
#     a5 = db.Column(db.Numeric(10,2))
#     c5 = db.Column(db.Integer)
#     s5 = db.Column(db.Integer)
#     #
#     average = db.Column(db.Numeric(10,2))
#     credit = db.Column(db.Integer)
#     session = db.Column(db.Integer)




class Promo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), index=True, unique=True)
    display_name = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    finish_date = db.Column(db.Date)
    color = db.Column(db.String(50))
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    sub_tree = db.Column(db.Text)
    sessions = db.relationship('Session', backref='promo')
    annual_session = db.relationship('AnnualSession', back_populates='promo')
    classement = db.relationship("Classement", uselist=False, back_populates="promo")
    module_sessions = db.relationship('ModuleSession', backref='promo')
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)
    def get_next_semester(self):
        sessions = Session.query.filter_by(promo_id=self.id, is_rattrapage=False).join(Semester).join(Annual)\
            .order_by(Annual.annual, Semester.semester).all()
        if len(sessions) == 0:
            return None
        last_session = sessions[-1]
        next_semester = last_session.semester.get_next()
        return next_semester
    def get_label(self):
        if self.display_name != None and self.display_name != '':
            return self.name + ' ' + self.display_name
        return self.name
    def get_color(self):
        return '#333333' if self.color == None or self.color == '' else self.color
    def has_closed_session(self):
        for session in self.sessions:
            if session.is_closed == True:
                return True
        return False
    def get_latest_annual(self):
        latest_annual = Annual.query\
            .join(Semester).join(Session).filter_by(promo_id=self.id)\
            .order_by(Annual.annual.desc()).first()
        if latest_annual is None:
            return 0
        return latest_annual.annual
    # def get_latest_of_semesters_list(self):
    #     semester = self.sessions.semester
    #     latest_of_semesters_list = semester.get_latest_of_semesters_list()

class AnnualSession(db.Model):
    __tablename__ = 'annual_session'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    is_closed = db.Column(db.Boolean, default=False)
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'))
    promo = db.relationship('Promo', back_populates='annual_session')
    annual_id = db.Column(db.Integer, db.ForeignKey('annual.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    sessions = db.relationship('Session', back_populates='annual_session')
    annual_grades = db.relationship('AnnualGrade', back_populates='annual_session')
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)
    def get_annual_dict(self):
        # assuming sessions always exist
        first_session = self.sessions[0]
        return first_session.get_annual_dict()
    def get_annual_dict_obj(self):
        first_session = self.sessions[0]
        return first_session.get_annual_dict_obj()
    def get_normal_sessions(self):
        normal_sessions = []
        for session in self.sessions:
            if session.is_rattrapage != True:
                normal_sessions.append(session)
        return normal_sessions
    def get_annual_pedagogique(self):
        session = self.sessions[0]
        return session.get_annual_pedagogique()
    def calculate(self):
        annual_grades = self.annual_grades
        for annual_grade in annual_grades:
            annual_grade.calculate()
        return 'AnnualSession calculated'
    def get_students_to_enter_rattrapage(self):
        students = AnnualGrade.query\
            .filter_by(annual_session_id=self.id)\
            .filter( AnnualGrade.enter_ratt == True )\
            .join(Student).order_by(Student.username).all()
        return students
    def check_need_calculate(self):
        for annual_grade in self.annual_grades:
            if annual_grade.is_dirty == True:
                return True
        return False
    def check_students_consistant_between_two_semesters(self):
        annual_dict_obj = self.get_annual_dict_obj()
        s1 = annual_dict_obj['S1']
        s2 = annual_dict_obj['S2']
        if s1 != None and s2 != None:
            students_list1 = s1.get_students_list()
            students_list2 = s2.get_students_list()
            students_list1.sort()
            students_list2.sort()
            if students_list1 == students_list2:
                return True
            else:
                #show message what is the problem
                l1 = len(students_list1)
                l2 = len(students_list2)
                s1_nbr = s1.get_name()
                s2_nbr = s2.get_name()
                msg1 = 'there is an inconsistency in the number of students </br>'
                msg2 = str(s1_nbr)+': ' + str(l1) + ' <> ' + str(s2_nbr)+': ' + str(l2)
                flash(msg1 + msg2, 'alert-danger')
                return False
        return True
    def check_students_ratt_are_in_semesters(self, ratt):
        annual_dict_obj = self.get_annual_dict_obj()
        s1 = annual_dict_obj['S1']
        r1 = annual_dict_obj['R1']
        s2 = annual_dict_obj['S2']
        r2 = annual_dict_obj['R2']

        if r1 == ratt and s1 != None:
            students_list = s1.get_students_list()
            students_ratt = r1.get_students_list()
            for student_id in students_ratt:
                if student_id not in students_list:
                    flash('some ratt students are not in '+s1.get_name(), 'alert-danger')
                    return False

        if r2 == ratt and s2 != None:
            students_list = s2.get_students_list()
            students_ratt = r2.get_students_list()
            print('--------------')
            print('--------------')
            for student_id in students_ratt:
                if student_id not in students_list:
                    flash('some ratt students are not in '+s2.get_name(), 'alert-danger')
                    return False
        
        return True

class AnnualGrade(db.Model):
    __tablename__ = 'annual_grade'
    id = db.Column(db.Integer, primary_key=True)
    avr_1 = db.Column(db.Numeric(10,2))
    cr_1 = db.Column(db.Integer)
    avr_2 = db.Column(db.Numeric(10,2))
    cr_2 = db.Column(db.Integer)
    units_fond_aquired = db.Column(db.Boolean, default=False)
    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    enter_ratt = db.Column(db.Boolean, default=False)

    avr_r_1 = db.Column(db.Numeric(10,2))
    cr_r_1 = db.Column(db.Integer)
    avr_r_2 = db.Column(db.Numeric(10,2))
    cr_r_2 = db.Column(db.Integer)
    units_r_fond_aquired = db.Column(db.Boolean, default=False)
    average_r = db.Column(db.Numeric(10,2))
    credit_r = db.Column(db.Integer)

    average_final = db.Column(db.Numeric(10,2))
    credit_final = db.Column(db.Integer)
    is_dirty = db.Column(db.Boolean, default=False)
    decision = db.Column(db.String(50))
    
    annual_session_id = db.Column(db.Integer, db.ForeignKey('annual_session.id'))
    annual_session = db.relationship("AnnualSession", back_populates="annual_grades")
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_ratt_modules_list_annual_html(self):
        annual_dict = self.annual_session.get_annual_dict()
        student_session_1 = StudentSession.query\
            .filter_by(session_id=annual_dict['S1'], student_id=self.student_id)\
            .first()
        student_session_2 = StudentSession.query\
            .filter_by(session_id=annual_dict['S2'], student_id=self.student_id)\
            .first()
        
        mudules_list_1 = '' 
        mudules_list_2 = ''
        if student_session_1 != None:
            mudules_list_1 = student_session_1.get_ratt_modules_list_semester_html()
        if student_session_2 != None:
            mudules_list_2 = student_session_2.get_ratt_modules_list_semester_html()
        
        _br = ''
        if mudules_list_1 != '' and mudules_list_2 != '':
            _br = '</br>'
            
        return mudules_list_1 + _br + mudules_list_2
    def fetch_data(self):
        annual_dict = self.annual_session.get_annual_dict()

        sess_1 = StudentSession.query.filter_by(
            session_id=annual_dict['S1'], student_id=self.student_id).first()
        sess_2 = StudentSession.query.filter_by(
            session_id=annual_dict['S2'], student_id=self.student_id).first()

        ratt_1 = StudentSession.query.filter_by(
            session_id=annual_dict['R1'], student_id=self.student_id).first()
        ratt_2 = StudentSession.query.filter_by(
            session_id=annual_dict['R2'], student_id=self.student_id).first()

        # if sess_1 == None or sess_2 == None:
        #     flash("you need to have at least Semester 1 & 2")
        #     return

        # Filling the fields from sessions
        self.avr_1 = sess_1.average if sess_1 != None else None
        self.cr_1  = sess_1.credit if sess_1 != None else None
        self.avr_2 = sess_2.average if sess_2 != None else None
        self.cr_2  = sess_2.credit if sess_2 != None else None

        # units_fond_aquired
        self.units_fond_aquired = None
        if sess_1 != None and sess_2 != None:
            u_f_aqui_1 = sess_1.units_fond_aquired()
            u_f_aqui_2 = sess_2.units_fond_aquired()
            self.units_fond_aquired = u_f_aqui_1 and u_f_aqui_2

        # after ratt
        self.avr_r_1 = ratt_1.average if ratt_1 != None else None
        self.cr_r_1 = ratt_1.credit if ratt_1 != None else None
        self.avr_r_2 = ratt_2.average if ratt_2 != None else None
        self.cr_r_2 = ratt_2.credit if ratt_2 != None else None

        # units_r_fond_aquired   
        self.units_r_fond_aquired = None  # init with units_fond_aquired
        self.units_r_fond_aquired = False # remove this
        if ratt_1 != None or ratt_2 != None:
            ratt_1 = ratt_1 if ratt_1 != None else sess_1
            ratt_2 = ratt_2 if ratt_2 != None else sess_2
            u_r_f_aqui_1 = ratt_1.units_fond_aquired()
            u_r_f_aqui_2 = ratt_2.units_fond_aquired()
            self.units_r_fond_aquired = u_r_f_aqui_1 and u_r_f_aqui_2

        # and Nullify the rest
        self.average = None
        self.credit = None
        self.average_r = None
        self.credit_r = None
        self.average_final = None
        self.credit_final = None
        self.enter_ratt = None
        return 'fetch_data_annual_grade'
    def calculate(self):
        def average(avr_1, avr_2):
            """ the two vals must not be None """
            if avr_1 != None and avr_2 != None:
                return (avr_1 + avr_2) / 2
            return None
        def credit(cr_1, cr_2, average, is_fondamental, units_fond_aquired):
            if cr_1 == None or cr_2 == None:
                return None
            if is_fondamental == False and average >= 10:
                return 60
            if is_fondamental == True and average >= 10 and units_fond_aquired == True:
                return 60
            return  cr_1 + cr_2

        ag = self
        if ag.avr_1 == None or ag.avr_2 == None or ag.cr_1 == None or ag.cr_2 == None:
            return 'student is missing from one of the semesters'

        # set is_dirty to False
        self.is_dirty = False

        # does the Annual has a fondamental
        is_fondamental = ag.annual_session.annual.has_fondamental()

        # before Ratt
        ag.average = average(ag.avr_1, ag.avr_2)
        ag.credit = credit(ag.cr_1, ag.cr_2, ag.average, is_fondamental, ag.units_fond_aquired)

        ag.enter_ratt = False
        if ag.credit < 60:
            ag.enter_ratt = True

        # after Ratt
        ag.average_r = None
        if ag.avr_r_1 != None or ag.avr_r_2 != None:
            avr_r_1 = ag.avr_r_1 if ag.avr_r_1 != None else ag.avr_1
            avr_r_2 = ag.avr_r_2 if ag.avr_r_2 != None else ag.avr_2
            ag.average_r = average(avr_r_1, avr_r_2)

        ag.credit_r = None
        if ag.cr_r_1 != None or ag.cr_r_2 != None:
            cr_r_1 = ag.cr_r_1 if ag.cr_r_1 != None else ag.cr_1
            cr_r_2 = ag.cr_r_2 if ag.cr_r_2 != None else ag.cr_2
            ag.credit_r = credit(cr_r_1, cr_r_2, ag.average_r, 
                is_fondamental, ag.units_r_fond_aquired)

        avr_r = ag.average_r
        ag.average_final = avr_r if avr_r != None else ag.average

        cr_r = ag.credit_r
        ag.credit_final = cr_r if cr_r != None else ag.credit

        decision = ''

        if ag.average != None:
            if ag.credit_final < 60:
                decision = 'rattrapage'

        if ag.average_r != None:
            if ag.credit_final < 60 and ag.credit_final >= 30:
                decision = 'admis_avec_dettes'

        # 
        # et chaque semestre possede au moin 10 crédit
        # 
        #       add it to ajournée
        #       
        if ag.average_r != None:
            if ag.credit_final < 30: # or one of the semesters credit is bellow 101
                decision = 'ajournee'

        if ag.credit_final == 60:
            decision = 'admis'
            if ag.average_r != None:
                decision = 'admis_apres_ratt'

        ag.decision = decision

        return 'AnnualGrade calculated'

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    start_date = db.Column(db.Date)
    finish_date = db.Column(db.Date)
    is_rattrapage = db.Column(db.Boolean, default=False)
    is_closed = db.Column(db.Boolean, default=False)
    is_historic = db.Column(db.Boolean, default=False)
    configuration = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_entry = db.Column(db.DateTime)

    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'))
    annual_session_id = db.Column(db.Integer, db.ForeignKey('annual_session.id'))
    annual_session = db.relationship('AnnualSession', back_populates='sessions')
    student_sessions = db.relationship('StudentSession', back_populates='session')

    # attendance_supervisors = db.relationship('AttendanceSupervisor', backref='session')
    def __repr__(self):
        return '<Session {}>'.format(self.id)
        # return '<{} - {}>'.format(self.id, self.name)
    def get_label(self):
        label = 'Rattrapage ' if self.is_rattrapage else 'Semester '
        label += '(' + str(self.semester.get_nbr()) + ') - ' + self.promo.get_label() 
        return label
    def get_name(self):
        label = 'Rattrapage ' if self.is_rattrapage else 'Semestre '
        label += '(' + str(self.semester.get_nbr()) + ')'
        return label
    def get_title(self):
        branch = self.promo.branch.name
        letter = 'R' if self.is_rattrapage else 'S'
        if self.is_historic:
            letter = 'HR' if self.is_rattrapage else 'H'
        semester = self.semester.get_nbr()
        return 'Session ('+str(branch)+' - '+letter+' '+str(semester)+')'
    def student_nbr(self):
        return StudentSession.query.filter_by(session_id=self.id).count()
    def get_previous(self):
        sessions = self.get_chain()
        index = sessions.index(self.id)
        if index == 0:
            return None
        return Session.query.get_or_404(sessions[index-1])
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
        return Session.query.get_or_404(sessions[index+1])
    def get_chain(self):
        sessions = Session.query.filter_by(promo_id=self.promo.id).join(Semester)\
            .join(Annual).order_by(Annual.annual, Semester.semester).all()
        sessions_id = []
        for session in sessions:
            sessions_id.append(session.id)
        return sessions_id
    def get_chain_normal(self):
        sessions = Session.query.filter_by(promo_id=self.promo.id, is_rattrapage=False).join(Semester).join(Annual)\
            .order_by(Annual.annual, Semester.semester).all()
        sessions_id = []
        for session in sessions:
            sessions_id.append(session.id)
        return sessions_id
    def get_annual_chain(self):
        sessions = Session.query.filter_by(promo_id=self.promo.id).join(Semester).join(Annual)\
            .order_by(Annual.annual, Semester.semester).all()
        current_annual = self.semester.annual.annual
        sessions_id = []
        for session in sessions:
            if session.semester.annual.annual == current_annual:
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
    def get_annual_dict_obj(self):
        annual_dict = self.get_annual_dict()
        S1 = Session.query.get( annual_dict['S1'] )
        S2 = Session.query.get( annual_dict['S2'] )
        R1 = Session.query.get( annual_dict['R1'] )
        R2 = Session.query.get( annual_dict['R2'] )
        A = AnnualSession.query.get( annual_dict['A'] )
        # print("---")
        # print(str(S1.id))
        # print(str(S2.id))
        # # print(str(annual_dict['R1']))
        # # print(str(annual_dict['R2']))
        # print(str(A.id))
        # print("---")
        return {'S1': S1, 'S2': S2, 'R1': R1, 'R2': R2, 'A': A}
    # this will return the Ratt for a Normal Session and vice versa
    def get_parallel_session(self):
        sessions = Session.query.filter_by(promo_id=self.promo.id).join(Semester).join(Annual)\
            .order_by(Annual.annual, Semester.semester).all()
        this_annual = self.semester.annual.annual
        this_semester = self.semester.semester
        parallel = None
        for session in sessions:
            if session != self and session.semester.annual.annual == this_annual and session.semester.semester == this_semester:
                return session
        return parallel
    def reverse_status(self):
        self.is_closed = not self.is_closed
    def allow_delete(self):
        ### closed
        if self.is_closed == True:
            return False

        ### is rattrapage
        if self.is_closed != True:
            if self.is_rattrapage == True or self.is_historic == True: 
                return True

        ### has annual
        annual_dict = self.get_annual_dict()
        if annual_dict['A'] != -1:
            return False

        ### not the last one  or  has rattrapage
        if self.get_next() != None:
            return False

        return True
    def is_config_changed(self):
        if self.is_closed == True:
            return False
        configuration = str(self.semester.config_dict())
        if configuration != self.configuration:
            return True
        return False
    def get_annual_pedagogique(self):
        annual_dict = self.get_annual_dict()
        session_1 = Session.query.get( annual_dict['S1'] )
        session_2 = Session.query.get( annual_dict['S2'] )

        if session_1 != None and session_1.start_date != None:
            start = session_1.start_date.year
            return str(start) + '/' + str(start+1)
        if session_2 != None and session_2.finish_date != None:
            finish = session_2.start_finish.year
            return str(finish-1) + '/' + str(finish)

        # if it didn't return then try to grab it from Promo
        # what year is this and the caclculate from Start of Promo
        annual = self.semester.annual.annual
        if self.promo.start_date != None:
            promo_start = self.promo.start_date.year
            return str(promo_start+annual-1) + '/' + str(promo_start+annual)

        return '[ #é$/&? ]/[ #é$/&? ]'
    # 
    # Note: if you have 5 students and 4 of them are filled
    #    you'll get 80% because AVERAGE(100% + 100% + 100% + 100% + 0%) = 80%
    def check_progress(self):
        student_sessions = self.student_sessions
        percentages = 0
        nbr_students = 0
        for ss in student_sessions:
            percentages += ss.check_progress()
            nbr_students += 1

        if nbr_students == 0:
            return int(0)

        progress = int(percentages / nbr_students)

        # type = historic
        if self.is_historic:
            return progress

        if progress == 100:
            grades = Grade.query.join(StudentSession).filter_by(session_id=self.id).all()
            check = check_grades_status(grades)
            if check['CALC'] == True:
                return progress - 1
        return progress
    # def check_is_historic(self):
    #     return self.check_is_historic
    def set_dirty(self):
        # set one record of each student session to dirty
        student_sessions = StudentSession.query.filter_by(session_id=self.id).all()
        for student_session in student_sessions:
            for grade in student_session.grades:
                grade.is_dirty = True
                break
        # db.session.commit()
    def get_students_list(self):
        student_list = []
        for student_session in self.student_sessions:
            student_list.append(student_session.student_id)
        return student_list
    def check_recalculate_needed(self):
        if self.is_historic:
            return False
        grades = Grade.query.join(StudentSession).filter_by(session_id=self.id).all()
        for grade in grades:
            if grade.is_dirty == True :
                return True
        return False
    def check_errors_exist(self):
        student_sessions = self.student_sessions
        grades = Grade.query.join(StudentSession).filter_by(session_id=self.id).all()
        check = check_grades_status(grades)
        if check['ERRS'] == True:
            return True
        return False
    def get_students_to_enter_rattrapage(self):
        students = StudentSession.query\
            .filter_by(session_id=self.id)\
            .filter( or_(StudentSession.credit < 30, StudentSession.credit == None) )\
            .join(Student).order_by(Student.username).all()
        # 
        # 
        # 
        # 
        # remove students who passed by the Annual
        #   show only students you can find in Annual
        #       
        # 
        # 
        # 
        return students
    # if commit=False -> don't commit after calculate
    def calculate(self, commit=True):
        student_sessions = self.student_sessions
        for student_session in student_sessions:
            for grade in student_session.grades:
                grade.calculate()
            db.session.commit()
            for grade_unit in student_session.grade_units:
                grade_unit.calculate()
            db.session.commit()
            student_session.calculate()
        if commit == True:
            db.session.commit()
        return 'Session calculated'

class StudentSession(db.Model):
    __tablename__ = 'student_session'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    calculation = db.Column(db.String(100))
    student = db.relationship("Student", back_populates="student_sessions")
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'))
    session = db.relationship('Session', back_populates='student_sessions')
    grades = db.relationship('Grade', back_populates='student_session')
    grade_units = db.relationship('GradeUnit', back_populates='student_session')
    last_entry = db.Column(db.DateTime)
    def units_fond_aquired(self):
        for grade_unit in self.grade_units:
            if grade_unit.unit.is_fondamental == True:
                if grade_unit.credit != grade_unit.unit.get_unit_cumul_credit():
                    credit = grade_unit.credit
                    unit_cumul_credit = grade_unit.unit.get_unit_cumul_credit()
                    # raise Exception('units_fond_aquired: '+str(credit)+' '+str(unit_cumul_credit))
                    return False
        return True
    def check_is_rattrapage(self):
        grades = self.grades
        for grade in grades:
            if grade.check_is_rattrapage():
                return True
        return False
    # i pass grade_units to avoid commiting them then fetching again
    def calculate(self, grade_units=None):
        if grade_units is None:
            grade_units = self.grade_units


        # find annual_grade to set it dirty
        annual_session = self.session.annual_session
        if annual_session != None:
            annual_grade = AnnualGrade.query.filter_by(
                annual_session_id=annual_session.id, 
                student_id=self.student_id).first()
            if annual_grade != None:
                # set is_dirty to True
                annual_grade.is_dirty = True
                db.session.commit()


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
    # move this to grade_unit
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
        if self.credit is not None and self.credit >= 30:
            return ''
        modules_list = self.get_ratt_modules_list_semester()
        html = '<table class="table-no-border" >'
        # style='border: 1px solid black;'
        html += '<tr><td colspan=2><i><b>'
        html += '    Semestre ' + str(self.session.semester.get_nbr())
        html += '</b></i></td>  <td align="right"><i><b>Moy</b></i></td></tr>'
        for module_id in modules_list:
            module = Module.query.get_or_404(module_id)
            grade = Grade.query.filter_by(student_session_id=self.id, module_id=module_id).first()
            html += '<tr>'
            html += '<td>' + module.unit.display_name + '</td>'
            html += '<td style=" width: 100%;">  ' + module.display_name.replace(' ', ' ') + '</td>'
            html += '<td>  ' + str(grade.average) + '</td>'
            # html += '<td> ' + str(grade.credit) + '</td>'
            html += '</tr>'
        html += '</table>'

        # html = '<table style="width: 100%; border: 0px;">'
        # # style='border: 1px solid black;'
        # html += '<tr style="border: 0px;"><td style="border: 0px;" colspan=3><i><b>'
        # html += '    Semester ' + str(self.session.semester.get_nbr())
        # html += '</b></i></td></tr>'
        # for module_id in modules_list:
        #     module = Module.query.get_or_404(module_id)
        #     grade = Grade.query.filter_by(student_session_id=self.id, module_id=module_id).first()
        #     html += '<tr style="border: 0px;">'
        #     html += '<td style="border: 0px;">' + module.unit.display_name + '</td>'
        #     html += '<td style="width: 100%; border: 0px;">  ' + module.display_name.replace(' ', ' ') + '</td>'
        #     html += '<td style="border: 0px;">  ' + str(grade.average) + '</td>'
        #     # html += '<td> ' + str(grade.credit) + '</td>'
        #     html += '</tr>'
        # html += '</table>'

        return html
    def check_progress(self):
        nbr_cells = 0
        nbr_filled = 0
        # nbr_errs = 0

        # type == historic
        if self.session.is_historic:
            average = 50 if self.average else 0
            credit = 50 if self.credit else 0
            return average + credit


        # type != historic
        grades = Grade.query.filter_by(student_session_id=self.id).all()
        
        for grade in grades:
            fields_list = []
            if grade.formula != None:
                fields_list = extract_fields(grade.formula)
            for field in fields_list:
                if field in ['cour', 'td', 'tp', 't_pers', 'stage']:
                    # check if Rattrapage
                    if not self.session.is_rattrapage:
                        nbr_cells += 1
                        val = getattr(grade, field)
                        if val != None:
                            nbr_filled += 1
                            # # if  not isinstance(val, decimal.decimal):
                            # if val < 0  or  val > 20:
                            #     nbr_errs += 1
                            #     # ERRS = True
                    elif grade.is_rattrapage == True:
                        ratt = grade.module.get_rattrapable_field()
                        if field == ratt:
                            nbr_cells += 1
                            val = getattr(grade, field)
                            if val != None:
                                nbr_filled += 1
                                # # if  not isinstance(val, decimal.decimal):
                                # if val < 0  or  val > 20:
                                #     nbr_errs += 1
                                #     # ERRS = True

        if nbr_cells == 0:
            return 0
        return nbr_filled * 100 / nbr_cells
    def get_last_grade_modification(self):
        # take into consideration Modifications in Classement

        last_grade = Grade.query.filter_by(student_session_id=self.id)\
            .order_by( Grade.timestamp.desc() ).first()
        if last_grade == None:
            return '***'
        return last_grade.timestamp.strftime("%d/%m/%Y %H:%M")

class GradeUnit(db.Model):
    __tablename__ = 'grade_unit'
    id = db.Column(db.Integer, primary_key=True)
    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    calculation = db.Column(db.String(100))
    unit_coefficient = db.Column(db.Integer())
    is_fondamental = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    unit = db.relationship('Unit', back_populates='grade_units')
    student_session_id = db.Column(db.Integer, db.ForeignKey('student_session.id'))
    student_session = db.relationship('StudentSession', back_populates='grade_units')
    def check_is_rattrapage(self):
        grades = self.student_session.grades
        for grade in grades:
            if grade.module.unit_id == self.unit_id:
                if grade.check_is_rattrapage():
                    return True
        return False
    # i pass grades to avoid commiting them then fetching again
    def calculate(self, grades=None):
        # grades in a one grade_unit
        if grades is None:
            grades = Grade.query.filter_by(student_session_id=self.student_session_id)\
                .join(Module).filter_by(unit_id=self.unit_id).all()
            # why didn't i use 
            # grades = self.student_session.grades

        cumul_unit_coeff = self.unit.get_unit_cumul_coeff()
        cumul_unit_coeff = cumul_unit_coeff if cumul_unit_coeff != None else 0 

        cumul_unit_credit = self.unit.get_unit_cumul_credit()
        cumul_unit_credit = cumul_unit_credit if cumul_unit_credit != None else 0 

        average = 0
        credit = 0
        calculation = ''
        credit_calculation = ''
        for grade in grades:
            # if grade.average == None:
            #     average = None
            #     break
            g_avr = grade.average
            if g_avr == None:
                g_avr = 0

            coefficient = grade.module.coefficient
            coefficient = coefficient if coefficient != None else 0 
            
            average += round(g_avr * coefficient / cumul_unit_coeff, 2)
            credit += grade.credit
            calculation += str(g_avr) + ' * ' + str(coefficient) + ' + '
            credit_calculation += str(grade.credit) + ' + '

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
            # self.calculation = calculation
            self.calculation = '<div>   <b>Moy:</b> ' + calculation\
                 + '</div>   <b>Cr:</b> ' + credit_calculation[:-3]\
                + ' ( fondamental ) ( < or > than 10 )'
        return 'unit calculated'

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cour = db.Column(db.Numeric(10,2))
    td = db.Column(db.Numeric(10,2))
    tp = db.Column(db.Numeric(10,2))
    t_pers = db.Column(db.Numeric(10,2))
    stage = db.Column(db.Numeric(10,2))
    saving_grade = db.Column(db.Numeric(10,2))
    average = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    formula = db.Column(db.String(200))
    calculation = db.Column(db.String(100))
    is_rattrapage = db.Column(db.Boolean, default=False)
    is_dirty = db.Column(db.Boolean, default=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module = db.relationship('Module', back_populates='grades')
    student_session_id = db.Column(db.Integer, db.ForeignKey('student_session.id'))
    student_session = db.relationship('StudentSession', back_populates='grades')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __repr__(self):
        return '<{} - {} - {}>'.format(self.id, self.student_session_id, self.cour)
    def get_username(self):
        s = self.student_session.student
        return s.username
    def get_student_name(self):
        s = self.student_session.student
        return s.last_name + ' ' + s.first_name
    def check_is_rattrapage(self):
        if self.is_rattrapage == True:
            # get the original grade
            original_grade = self.get_ratt_original_grade()

            # check if this grade is empty
            field = self.module.get_rattrapable_field()
            this_grade = getattr(self, field)
            if this_grade == None or original_grade == None:
                return True

            # see if the new grade is higher
            if original_grade <= this_grade:
                return True
        return False
    def get_ratt_original_grade(self):
        original_grade = 0
        # original_grade = None
        if self.is_rattrapage == True:
            parallel_session = self.student_session.session.get_parallel_session()
            original = Grade.query.filter_by(module_id=self.module_id)\
                .join(StudentSession).filter_by(
                    session_id=parallel_session.id, 
                    student_id=self.student_session.student_id).first()
            # get the rattrapable
            if original != None:
                field = self.module.get_rattrapable_field()
                original_grade = getattr(original, field)
        return original_grade
    def calculate(self):
        average = 0
        calculation = ''
        dictionary = eval(self.formula)

        # find out if it is savable
        is_savable = False
        module_saving_enabled = False

        if self.saving_grade != None:
            promo_id = self.student_session.session.promo_id
            module_id = self.module_id
            is_rattrapage = self.student_session.session.is_rattrapage

            module_session = ModuleSession.query.filter_by(
                promo_id=promo_id, 
                module_id=module_id,
                is_rattrapage=is_rattrapage).first()

            if module_session != None:
                module_saving_enabled = module_session.saving_enabled

                # print('--------+++--------')
                # print(''+str(module_session.id))
                # print(''+str(module_saving_enabled))
                # print(' '+str(promo_id)+' '+str(module_id)+' '+str(is_rattrapage))
                # print('')

                # is_savable = True
                if module_saving_enabled == True:
                    # check saving_grade in range
                    is_in_range = self.saving_grade <= 20 and self.saving_grade >= 0

                    if is_in_range == True:
                        # is_rattrapage = module_session.session.is_rattrapage
                        session = module_session.get_session()
                        if session.is_rattrapage == True:
                            if self.is_rattrapage == True:
                                average = self.saving_grade
                                is_savable = True
                                calculation += '(saving_grade: '+str(average)+')'
                        else:
                            average = self.saving_grade
                            is_savable = True
                            calculation += '(saving_grade: '+str(average)+')'
                    else: 
                        calculation += '(there is an ERROR in the grades)'

        if is_savable == False:
            is_in_range = True
            for field in dictionary:
                if field in ['cour', 'td', 'tp', 't_pers', 'stage']:
                    val = getattr(self, field)
                    percentage = dictionary[field]
                    is_in_range = False
                    if val != None:
                        is_in_range = val >= 0 and val <= 20
                    getcontext().prec = 4
                    # print('')
                    # print(field + ' ' +str(val))
                    # print('')
                    if val != None and is_in_range:
                        average += round( val * Decimal(percentage) , 2)
                        # average += round( val , 2)
                    if val == None:
                        val = '#é$/&?|[+{#%*#$='
                    calculation += '('+str(field)+': '+str(val)+' * '+str(percentage)+')' + ' + '
            # end for

            if is_in_range == True:
                calculation = calculation[:-3]
            else:
                # calculation = '(there is an ERROR in the grades)'
                calculation += '(there is an ERROR in the grades)'


        # credit
        credit = 0
        if average != None:
            if average >= 10:
                credit = dictionary['credit']

        self.average = average
        self.credit = credit
        self.calculation = calculation
        self.is_dirty = False
        return 'grade calculated'

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.String(150))
    branches = db.relationship('Branch', backref='school')
    def __repr__(self):
        return '<School {}>'.format(self.name)
    def get_label(self):
        if self.description != None and self.description != '':
            return self.name + ' - ' + self.description
        return self.name

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True)
    description = db.Column(db.String(150))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    students = db.relationship('Student', backref='branch')
    annuals = db.relationship('Annual', backref='branch')
    promos = db.relationship('Promo', backref='branch', order_by='Promo.start_date, Promo.name')
    def __repr__(self):
        return '<Branch {}>'.format(self.name)
    def get_label(self):
        if self.description != None and self.description != '':
            return self.name + ' - ' + self.description
        return self.name
    def get_annuals_ordered(self):
        annuals = Annual.query.filter_by(branch_id=self.id)\
            .order_by(Annual.annual).all()
        return annuals
    def get_semesters_ordered(self):
        # semesters = Semester.query.join(Annual).filter_by(branch_id=self.id)\
        #     .order_by(Annual.annual, Semester.semester).all()
        semesters = Semester.query.join(Annual).filter_by(branch_id=self.id)\
            .order_by(Annual.annual, Semester.semester, Semester.latest_update).all()
        return semesters
    def years_from_config(self):
        return len(self.annuals)

class Annual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    annual = db.Column(db.Integer)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    semesters = db.relationship('Semester', backref='annual')
    annual_sessions = db.relationship('AnnualSession', backref='annual')
    def has_fondamental(self):
        semesters = self.semesters
        for semester in semesters:
            if semester.has_fondamental() == True:
                return True
        return False
    def get_semesters_ordered(self):
        semesters = Semester.query.filter_by(annual_id=self.id)\
            .order_by(Semester.semester, Semester.latest_update).all()
        return semesters
    def get_label(self):
        if self.display_name != None and self.display_name != '':
            return self.name + ' - ' + self.display_name
        return self.name
    def get_string_literal(self):
        if self.annual > 1:
            return str(self.annual) + ' eme Année'
        return '1 ére Année'

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    semester = db.Column(db.Integer)
    latest_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_closed = db.Column(db.Boolean, default=False)
    annual_id = db.Column(db.Integer, db.ForeignKey('annual.id'))
    units = db.relationship('Unit', backref='semester', order_by="Unit.order")
    sessions = db.relationship('Session', backref='semester')
    def __repr__(self):
        return '<{} - {}>'.format(self.id, self.name)
    def get_nbr(self):
        return (self.annual.annual * 2) - 2 + self.semester
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
    def get_semester_units_coeff_comul(self):
        units = self.units
        unit_coefficient = 0
        for unit in units:
            if unit.unit_coefficient != None and unit.unit_coefficient != '':
                unit_coefficient = unit_coefficient + unit.unit_coefficient
        return unit_coefficient
    def get_semesters_list(self):
        # ordered from branch not 
        return self.annual.branch.get_semesters_ordered()
    def get_parallels(self):
        parallel_semesters = Semester.query.filter_by(semester=self.semester)\
                .join(Annual).filter_by(annual=self.annual.annual, branch_id=self.annual.branch_id)\
                .order_by(Semester.latest_update).all()
        return parallel_semesters
    def get_latest_of_semesters_list(self):
        semesters = self.get_semesters_list()
        # semesters = self.annual.branch.get_semesters_ordered()
        filtered_list = []
        for semester in semesters:
            # ann = semester.annual
            # parallel_semesters = Semester.query.filter_by(semester=semester.semester)\
            #     .join(Annual).filter_by(annual=ann.annual, branch_id=ann.branch_id)\
            #     .order_by(Semester.latest_update).all()
            parallel_semesters = semester.get_parallels()

            if parallel_semesters[-1] not in filtered_list:
                filtered_list.append(parallel_semesters[-1])

        return filtered_list
    def get_previous(self):
        semesters = self.get_latest_of_semesters_list()
        _previous = None
        for i in range(1, len(semesters)):
            if semesters[i].annual.annual == self.annual.annual and semesters[i].semester == self.semester:
                _previous = semesters[i-1]
        return _previous
    def get_next(self):
        semesters = self.get_latest_of_semesters_list()
        _next = None
        for i in range(0, len(semesters)-1):
            if semesters[i].annual.annual == self.annual.annual and semesters[i].semester == self.semester:
                _next = semesters[i+1]
        return _next
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
        semesters = { 's_id': self.id, 'name': self.name, 'display_name': self.display_name, 
            'branch':self.annual.branch_id, 'annual': self.annual.annual, 'semester': self.semester }
        for unit in self.units:
            semesters.setdefault('units', []).append(unit.config_dict())
        return semesters
    def has_fondamental(self):
        units = self.units
        for unit in units:
            if unit.is_fondamental == True:
                return True
        return False
    def has_percentage_problem(self):
        for unit in self.units:
            for module in unit.modules:
                if module.has_percentage_problem():
                    return True
        return False
    def has_code_missing(self):
        for unit in self.units:
            for module in unit.modules:
                if module.code == None or module.code == '':
                    return True
        return False
    def has_rattrapable_error(self):
        for unit in self.units:
            for module in unit.modules:
                if module.has_rattrapable_error() == True:
                    return True
        return False
    def nbr_of_modules(self):
        nbr = 0
        for unit in self.units:
            for module in unit.modules:
                nbr += 1
        return nbr
    # @hybrid_method
    def is_locked(self):
        if self.is_closed == True:
            return True
        for session in self.sessions:
            if session.is_closed == True:
                return True
        return False
    # def new_latest_update(self):
    #     return datetime.utcnow()

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    display_name = db.Column(db.String(250))
    unit_coefficient = db.Column(db.Integer)
    is_fondamental = db.Column(db.Boolean, default=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    order = db.Column(db.Integer, default=1)
    modules = db.relationship('Module', backref='unit', order_by="Module.order")
    grade_units = db.relationship('GradeUnit', back_populates='unit')
    def __repr__(self):
        return '<Unit {}>'.format(self.name)
    def get_unit_cumul_coeff(self):
        modules = self.modules
        coeff = 0
        for module in modules:
            coeff = coeff + module.coefficient if module.coefficient != None else 0
        return coeff
    def get_unit_cumul_credit(self):
        modules = self.modules
        credit = 0
        for module in modules:
            credit = credit + module.credit if module.credit != None else 0
        return credit
    def config_dict(self):
        units = { 'u_id': self.id, 'name': self.name, 'display_name': self.display_name, 
            'unit_coefficient': self.unit_coefficient, 'is_fondamental': self.is_fondamental, 
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
    order = db.Column(db.Integer, default=1)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'))
    percentages = db.relationship('Percentage', backref='module', order_by='Percentage.order')
    grades = db.relationship('Grade', back_populates='module')
    module_sessions = db.relationship('ModuleSession', backref='module')
    def __repr__(self):
        return '<Module {}>'.format(self.name)
    def config_dict(self):
        # modules = { 'm_id': self.id, 'name': self.name, 'display_name': self.display_name, 
        #     'coeff': self.coefficient, 'credit': self.credit, 'time': str(self.time) }
        modules = { 'm_id': self.id, 'code': self.code, 'name': self.name, 'display_name': self.display_name, 
            'coeff': self.coefficient, 'credit': self.credit }
        for percentage in self.percentages:
            modules.setdefault('percentages', []).append(percentage.config_dict())
        return modules
    def has_percentage_problem(self):
        percent = 0
        for percentage in self.percentages:
            percent += percentage.percentage

        if percent != 1:
            return True
        return False
    def get_rattrapable_field(self):
        for percentage in self.percentages:
            if percentage.rattrapable == True:
                return percentage.type.grade_table_field
        return 'cour'
    def has_rattrapable_error(self):
        nbr_ratt = 0
        for percentage in self.percentages:
            if percentage.rattrapable == True:
                nbr_ratt += 1
        if nbr_ratt > 1:
            return True
        return False
    # def set_latest_update(self):
    #     # raise Exception('___tttttt____: '+str(datetime.utcnow()) )
    #     self.unit.semester.latest_update = datetime.utcnow()
    def get_sessions(self):
        semester = self.unit.semester
        sessions = semester.sessions
        return sessions
    def get_sessions_all_in_parallel_semesters(self):
        _semester = self.unit.semester
        _annual = _semester.annual
        _branch = _annual.branch
        semesters = Semester.query.filter_by(semester=_semester.semester)\
            .join(Annual).filter_by(annual=_annual.annual)\
            .join(Branch).filter_by(id=_branch.id)\
            .join(School).filter_by(id=_branch.school_id)\
            .all()
        sessions = []
        for semester in semesters:
            sessions += semester.sessions
        return sessions
    def get_label(self):
        return str(self.code)+' - '+str(self.display_name)

class Percentage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    percentage = db.Column(db.Numeric(10,2))
    time = db.Column(db.Numeric(10,2))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
    rattrapable = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=1)
    def config_dict(self):
        type = Type.query.filter_by(id=self.type_id).first()
        # config = { 'type': type.type, 'per': str(self.percentage), 'time': str(self.time) } 
        config = { 'type': type.type, 'per': str(self.percentage) } 
        if self.rattrapable == True:
            config = { 'type': type.type, 'per': str(self.percentage), 'rattrapable': self.rattrapable } 
        return config

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(45))
    grade_table_field = db.Column(db.String(45))
    percentages = db.relationship('Percentage', backref='type')
    def __repr__(self):
        return '{}'.format(self.type)
        # return '<Type {}>'.format(self.type)

############################## 

class Wilaya(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), index=True, unique=True)
    name = db.Column(db.String(100), index=True, unique=True)
    students = db.relationship('Student', backref='wilaya')
    teachers = db.relationship('Teacher', backref='wilaya')
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
    email = db.Column(db.String(120))
    birth_date = db.Column(db.Date)
    birth_place = db.Column(db.String(45))
    address =  db.Column(db.String(120))
    photo = db.Column(db.String(250))
    last_name_arab = db.Column(db.String(100))
    first_name_arab = db.Column(db.String(100))
    sex = db.Column(db.String(20))
    residency = db.Column(db.String(20))
    phones = db.relationship('Phone', backref='student')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.id'))
    wilaya_id = db.Column(db.Integer, db.ForeignKey('wilaya.id'))
    ccp = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    student_sessions = db.relationship('StudentSession', back_populates='student')
    annual_grades = db.relationship('AnnualGrade', backref='student')
    classement = db.relationship("Classement", uselist=False, back_populates="student")
    attendance = db.relationship('Attendance', backref='student') #, order_by="Attendance."
    def __repr__(self):
        return '<{} - {} - {}>'.format(self.id, self.username, self.last_name)
    # @staticmethod
    def find(id):
        return db.session.query(Student).filter_by(id=id).one()
    def get_student_name(self):
        return self.last_name + ' ' + self.first_name
    def get_student_long_name(self):
        return self.username + ' - ' + self.last_name + ' ' + self.first_name
    def get_promos(self):
        promos = Promo.query.join(Session).join(StudentSession)\
            .filter_by(student_id=self.id).all()
        return promos
    def allow_username_change(self):
        promos = self.get_promos()
        for promo in promos:
            if promo.has_closed_session() == True:
                return False
        return True
    # take into considiration many users getting the same Matricule
    # maybe you have to lock
    @staticmethod
    def get_username(bransh, year, seperator='/'):
        # return 'username_start'
        username_start = bransh + seperator + year + seperator
        # username_start = 'SF-2019-'

        student = Student.query\
            .order_by(Student.username.desc())\
            .filter(Student.username.like(username_start + '%'))\
            .first()
        # student = Student.query.order_by(Student.username.desc()).filter(Student.username.like('SF/2017%')).first()
        if student == None:
            return username_start + '01'
            
        # username = student.username.lower()
        last = ''
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
    def get_sessions_ordered(self):
        sessions = Session.query.join(StudentSession).filter_by(student_id=self.id)\
            .join(Semester).join(Promo).join(Annual)\
            .order_by(Promo.name, Annual.annual, Semester.semester).all()
        return sessions

class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    phone = db.Column(db.String(45))
    type = db.Column(db.String(45))
    def __repr__(self):
        return '<Phone: id = {} | student_id = {} | phone = {}>'.format(self.id, self.student_id, self.phone)

############################## 

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True) # matricule
    title = db.Column(db.String(20))
    last_name = db.Column(db.String(45), index=True)
    first_name = db.Column(db.String(45), index=True)
    # last_name_arab = db.Column(db.String(100))
    # first_name_arab = db.Column(db.String(100))
    email = db.Column(db.String(120))
    birth_date = db.Column(db.Date)
    birth_place = db.Column(db.String(45))
    address =  db.Column(db.String(120))
    wilaya_id = db.Column(db.Integer, db.ForeignKey('wilaya.id'))
    photo = db.Column(db.String(250))
    phone = db.Column(db.String(20))
    sex = db.Column(db.String(20))
    ccp = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    module_sessions = db.relationship('ModuleSession', backref='teacher')
    teacher_attendances = db.relationship('TeacherAttendance', backref='teacher')

class ModuleSession(db.Model):
    __tablename__ = 'module_session'
    id = db.Column(db.Integer, primary_key=True)
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module_code = db.Column(db.String(20))
    module_name = db.Column(db.String(255))
    is_rattrapage = db.Column(db.Boolean)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    start_date = db.Column(db.Date)
    finish_date = db.Column(db.Date)
    exam_date = db.Column(db.Date)
    results_delivered_date = db.Column(db.Date)
    exam_surveyors = db.Column(db.Text)
    saving_enabled = db.Column(db.Boolean, default=False)
    last_entry = db.Column(db.DateTime)
    module_calendars = db.relationship('ModuleCalendar', backref='module_session')
    def has_teacher(self):
        if self.teacher_id == None:
            return True
        return False
    def get_session(self):
        # module = self.module
        semester = self.module.unit.semester
        
        session = Session.query.filter_by(
            is_rattrapage=self.is_rattrapage,
            promo_id=self.promo_id,
            semester_id=semester.id
        ).first()
        return session

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_calendar_id = db.Column(db.Integer, db.ForeignKey('module_calendar.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    attended = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TeacherAttendance(db.Model):
    __tablename__ = 'teacher_attendance'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    module_calendar_id = db.Column(db.Integer, db.ForeignKey('module_calendar.id'))
    from_ = db.Column(db.DateTime)
    to_ = db.Column(db.DateTime)
    attended = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ModuleCalendar(db.Model):
    __tablename__ = 'module_calendar'
    id = db.Column(db.Integer, primary_key=True)
    module_session_id = db.Column(db.Integer, db.ForeignKey('module_session.id'))
    name = db.Column(db.String(255))
    start_event = db.Column(db.DateTime)
    end_event = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    attendances = db.relationship('Attendance', backref='module_calendar')

############################## 

class Classement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    avr_classement = db.Column(db.Numeric(10,2))
    cr_classement = db.Column(db.Integer)
    dec_classement = db.Column(db.String(150))
    classement_cursus = db.relationship('ClassementCursus', backref='classement')
    student = db.relationship("Student", back_populates="classement")
    promo = db.relationship("Promo", back_populates="classement")

class ClassementCursus(db.Model):
    __tablename__ = 'classement_cursus'
    id = db.Column(db.Integer, primary_key=True)
    classement_id = db.Column(db.Integer, db.ForeignKey('classement.id'))
    cursus = db.Column(db.String(50))
    avr_cursus = db.Column(db.Numeric(10,2))
    cr_cursus = db.Column(db.Integer)
    dec_cursus = db.Column(db.String(150))
    classement_years = db.relationship('ClassementYear', backref='classement_cursus')

class ClassementYear(db.Model):
    __tablename__ = 'classement_year'
    id = db.Column(db.Integer, primary_key=True)
    classement_cursus_id = db.Column(db.Integer, db.ForeignKey('classement_cursus.id'))
    year = db.Column(db.Integer)
    average = db.Column(db.Numeric(10,2))
    average_app = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    credit_app = db.Column(db.Integer)
    credit_cumul = db.Column(db.Integer)
    decision = db.Column(db.String(150))
    decision_app = db.Column(db.String(150))
    R     = db.Column(db.Numeric(10,2))
    R_app = db.Column(db.Numeric(10,2))
    S     = db.Column(db.Numeric(10,2))
    S_app = db.Column(db.Numeric(10,2))
    avr_classement = db.Column(db.Numeric(10,2))
    classement_semesters = db.relationship('ClassementSemester', backref='classement_year')

class ClassementSemester(db.Model):
    __tablename__ = 'classement_semester'
    id = db.Column(db.Integer, primary_key=True)
    classement_year_id = db.Column(db.Integer, db.ForeignKey('classement_year.id'))
    semester = db.Column(db.Integer)
    average = db.Column(db.Numeric(10,2))
    average_app = db.Column(db.Numeric(10,2))
    credit = db.Column(db.Integer)
    credit_app = db.Column(db.Integer)
    b     = db.Column(db.Numeric(10,2))
    b_app = db.Column(db.Numeric(10,2))
    d     = db.Column(db.Numeric(10,2))
    d_app = db.Column(db.Numeric(10,2))
    s     = db.Column(db.Numeric(10,2))
    s_app = db.Column(db.Numeric(10,2))
    avr_classement = db.Column(db.Numeric(10,2))

############################## 

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(45))
    notification = db.Column(db.String(225))
    complite = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.Float, index=True, default=datetime.utcnow)
    delete_url = db.Column(db.String(225))
    # user_id = 


# class Role(db.Model, RoleMixin):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    roles = db.relationship('Role', secondary='user_roles',
            backref=db.backref('users', lazy='dynamic'), order_by='Role.id')
    attendance_supervisors = db.relationship('AttendanceSupervisor', backref='user')
    def __repr__(self):
        return '<User: id = {} | username = {} | email = {}>'.format(self.id, self.username, self.email)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
# Define Role model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(150))
    # def __repr__(self):
    #     return '<Role: id = {} | name = {}>'.format(self.id, self.username)

# Define UserRoles model
class UserRoles(db.Model):
    # __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class AttendanceSupervisor(db.Model):
    # __tablename__ = 'attendance_supervisor'
    id = db.Column(db.Integer(), primary_key=True)
    session_id = db.Column(db.Integer(), db.ForeignKey('session.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
 

@login.user_loader
def load_user(id):
    return User.query.get_or_404(int(id))
    






