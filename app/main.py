from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return render_template('main/index.html')


@bp.route('/courses')
@login_required
def courses():
    db = get_db()
    courses = db.execute(
        "SELECT * FROM courses ORDER BY course_name ASC"
    ).fetchall()
    return render_template('main/courses.html', courses=courses)


@bp.route('/create_course', methods=('GET', 'POST'))
@login_required
def create_course(): 
    if request.method == 'POST':
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        passing_grade = request.form['passing_grade']
        error = None
        
        if not course_code:
            error = 'Course code is required.'
        elif not course_name:
            error = 'Course name is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO courses (course_code, course_name, passing_grade)"
                " VALUES (?, ?, ?)",
                (course_code.upper(), course_name.title(), passing_grade)
            )
            db.commit()
            return redirect(url_for('main.courses'))
        
    return render_template('main/create_course.html')


def get_course(id):
    course = get_db().execute(
        "SELECT * FROM courses WHERE guid = ?", (id,)
    ).fetchone()
    
    if course is None:
        abort(404, f"Course guid {id} doesn't exist.")
        
    return course


@bp.route('/<id>/update_course', methods=('GET', 'POST'))
@login_required
def update_course(id):
    course = get_course(id)

    if request.method == 'POST':
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        passing_grade = request.form['passing_grade']
        error = None

        if not course_code:
            error = 'Course code is required.'
        elif not course_name:
            error = 'Course name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE courses SET course_code = ?, course_name = ?, passing_grade = ?"
                " WHERE guid = ?",
                (course_code.upper(), course_name.title(), passing_grade, id)
            )
            db.commit()
            return redirect(url_for('main.courses'))

    return render_template('main/update_course.html', course=course)


@bp.route('/<id>/delete_course', methods=('POST',))
@login_required
def delete_course(id):
    db = get_db()
    db.execute('DELETE FROM courses WHERE guid = ?', (id,))
    db.commit()
    return redirect(url_for('main.index'))


@bp.route('/<id>/grades', methods=('GET', 'POST'))
@login_required
def grades(id):
    db = get_db()
    grades = db.execute(
        "SELECT g.guid, course_guid, score, grade, course_code, course_name"
        " FROM grades g JOIN courses c ON g.course_guid = c.guid"
        " WHERE student_guid = ?", (id,)
    ).fetchall()
    return render_template('main/grades.html', grades=grades)


@bp.route('/create_grade', methods=('GET', 'POST'))
@login_required
def create_grade():
    if request.method == 'POST':
        db = get_db()
        student_guid = g.user['guid']
        course_guid = request.form['course_guid']
        score = request.form['score']
        grade = db.execute(
            "SELECT grade FROM rules WHERE ? >= min_score and ? <= max_score", (score, score)
        ).fetchone()[0]
        error = None
        
        if not course_guid:
            error = 'Please select a course.'
        elif not score:
            error = 'Please input a score.'
        
        if error is None:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO grades (student_guid, course_guid, score, grade)"
                    " VALUES (?, ?, ?, ?)",
                    (student_guid, course_guid, score, grade)
                )
                db.commit()
            except db.IntegrityError:
                error = f"Already have a grade for that course."
            else:
                return redirect(url_for('main.grades', id=g.user['guid']))
        
        if error:
            flash(error)

    db = get_db()
    courses = db.execute(
        "SELECT * FROM courses"
    ).fetchall()
    return render_template('main/create_grade.html', courses=courses)


def get_grade(id, check_id=True):
    grade = get_db().execute(
        "SELECT * FROM grades WHERE guid = ?", (id,)
    ).fetchone()
    
    if grade is None:
        abort(404, f"Course guid {id} doesn't exist.")
        
    if check_id and grade['student_guid'] != g.user['guid']:
        abort(403)
        
    return grade


@bp.route('/<id>/update_grade', methods=('GET', 'POST'))
@login_required
def update_grade(id):
    grade = get_grade(id)

    if request.method == 'POST':
        db = get_db()
        student_guid = g.user['guid']
        course_guid = request.form['course_guid']
        score = request.form['score']
        grade = db.execute(
            "SELECT grade FROM rules WHERE ? >= min_score and ? <= max_score", (score, score)
        ).fetchone()[0]
        error = None

        if not course_guid:
            error = 'Please select a course'
        elif not score:
            error = 'Please input a score'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE grades SET student_guid = ?, course_guid = ?, score = ?, grade = ?"
                " WHERE guid = ?",
                (student_guid, course_guid, score, grade, id)
            )
            db.commit()
            return redirect(url_for('main.grades', id=g.user['guid']))

    db = get_db()
    courses = db.execute(
        "SELECT * FROM courses"
    ).fetchall()
    return render_template('main/update_grade.html', courses=courses, grade=grade)


@bp.route('/<id>/delete_grade', methods=('POST',))
@login_required
def delete_grade(id):
    db = get_db()
    db.execute('DELETE FROM grades WHERE guid = ?', (id,))
    db.commit()
    return redirect(url_for('main.grades', id=g.user['guid']))