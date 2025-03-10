import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.auth_utils import is_valid_email, is_valid_password
from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        student_number = request.form['student_number']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        
        if not student_number:
            error = 'Student Number is required.'
        elif not email:
            error = 'Email is required.'
        elif not is_valid_email(email):
            error = 'Invalid email format.'
        elif not is_valid_password(password):
            error = 'Please choose a stronger password.'
            
        if error is None:
            try:
                db.execute(
                    "INSERT INTO students (student_number, email, password) VALUES (?, ?, ?)",
                    (student_number.upper(), email, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Student {student_number} is already registered."
            else:
                return redirect(url_for("auth.login"))
        
        if error:
            flash(error)
    
    return render_template('auth/register.html')


@bp.route('login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        sn_email = request.form['sn_email']
        password = request.form['password']
        db = get_db()
        error = None
        if is_valid_email(sn_email):
            user = db.execute(
                "SELECT * FROM students WHERE email = ?", (sn_email,)
            ).fetchone()
        else:
            user = db.execute(
                "SELECT * FROM students WHERE student_number = ?", (sn_email.upper(),)
            ).fetchone()
            
        if user is None:
            error = 'Incorrect Student Number or Email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
            
        if error is None:
            session.clear()
            session['user_id'] = user['guid']
            return redirect(url_for('index'))
        
        if error:
            flash(error)
            
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM students WHERE guid = ?", (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view