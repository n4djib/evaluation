from app import app, db
from flask import render_template, g, flash
# from app.permissions_and_roles import current_privileges

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(401)
def authentication_failed(error):
    flash('Authenticated failed.')
    return redirect(url_for('login'))



@app.errorhandler(403)
def authorisation_failed(error):
    flash(('Your current identity is "{id}". You need special privileges to'
           ' access this page').format(id=g.identity.user.username))
    return render_template('errors/privileges.html', priv=[])
    
