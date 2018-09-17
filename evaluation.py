from app import app, db
from app.models import Student, Phone, User, Session, StudentSession, Grade, School, Branch, AnnualSession

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Student': Student, 'Phone': Phone, 'User': User, 'Session': Session, 
    		'StudentSession': StudentSession, 'Grade': Grade, 'School': School, 'Branch': Branch, 
    		'AnnualSession': AnnualSession}
