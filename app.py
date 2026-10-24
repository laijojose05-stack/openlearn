from flask import Flask, render_template, request, redirect, session,url_for
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import MySQLdb.cursors 
from MySQLdb.cursors import DictCursor
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "openlearn123"

# ---------------- CONFIG ----------------
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '1234')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'openlearn')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))

UPLOAD_FOLDER = os.path.join('static', 'uploads', 'notes')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

# Health check for Render
@app.route('/health')
def health():
    return {'status': 'ok'}, 200

# ---------------- HOME ----------------

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/choose-login')
def choose_login():
    return render_template('choose_login.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ---------------- ADMIN LOGIN ----------------

@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id FROM admin WHERE email=%s AND password=%s",
            (email, password)
        )
        admin = cur.fetchone()

        if admin:
            session.clear()
            session['admin'] = admin[0]
            return redirect('/admin/dashboard')

        return render_template('login_admin.html', error="Invalid login")

    return render_template('login_admin.html')


# =========================================================
# ADMIN DASHBOARD
# =========================================================
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/login-admin')

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM teachers WHERE branch IS NOT NULL")
    assigned_teachers = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    return render_template(
        'admin/dashboard.html',
        total_teachers=total_teachers,
        assigned_teachers=assigned_teachers,
        unassigned_teachers=total_teachers - assigned_teachers,
        total_students=total_students
    )


# =========================================================
# VIEW ALL TEACHERS (IMPORTANT BASE PAGE)
# =========================================================
@app.route('/admin/teachers')
def admin_teachers():
    if 'admin' not in session:
        return redirect('/login-admin')

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, branch FROM teachers")
    teachers = cur.fetchall()

    return render_template(
        'admin/pages/teachers.html',
        teachers=teachers
    )


# =========================================================
# ADD TEACHER
# =========================================================
@app.route('/admin/add-teacher', methods=['GET', 'POST'])
def admin_add_teacher():
    if 'admin' not in session:
        return redirect('/login-admin')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # prevent duplicate email
        cur.execute("SELECT id FROM teachers WHERE email=%s", (email,))
        if cur.fetchone():
            return render_template(
                'admin/pages/add_teacher.html',
                error="Teacher already exists"
            )

        cur.execute(
            "INSERT INTO teachers (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        mysql.connection.commit()

        return redirect('/admin/teachers')

    return render_template('admin/pages/add_teacher.html')


# =========================================================
# ASSIGN TEACHER
# =========================================================
@app.route('/admin/assign', methods=['GET', 'POST'])
def admin_assign():
    if 'admin' not in session:
        return redirect('/login-admin')

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        branch = request.form['branch']

        cur.execute(
            "UPDATE teachers SET branch=%s WHERE id=%s",
            (branch, teacher_id)
        )
        mysql.connection.commit()

    # only unassigned teachers
    cur.execute(
        "SELECT id, name, email FROM teachers WHERE branch IS NULL"
    )
    teachers = cur.fetchall()

    return render_template(
        'admin/pages/assign.html',
        teachers=teachers
    )


# =========================================================
# UNASSIGN TEACHER
# =========================================================
@app.route('/admin/unassign', methods=['GET', 'POST'])
def admin_unassign():
    if 'admin' not in session:
        return redirect('/login-admin')

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        teacher_id = request.form['teacher_id']
        cur.execute(
            "UPDATE teachers SET branch=NULL WHERE id=%s",
            (teacher_id,)
        )
        mysql.connection.commit()

    # only assigned teachers
    cur.execute(
        "SELECT id, name, email, branch FROM teachers WHERE branch IS NOT NULL"
    )
    teachers = cur.fetchall()

    return render_template(
        'admin/pages/unassign.html',
        teachers=teachers
    )

#------------ TEACHER ----------------

@app.route('/login-teacher', methods=['GET','POST'])
def login_teacher():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teachers WHERE email=%s AND password=%s",
                    (email,password))
        teacher = cur.fetchone()

        if teacher:
            session.clear()
            session['teacher'] = teacher[0]
            return redirect('/teacher/home')

        return render_template(
            'login_teacher.html',
            error="Invalid email or password. Please try again."
        )
    return render_template('login_teacher.html')


@app.route('/teacher/home')
def teacher_home():
    if 'teacher' not in session:
        return redirect('/login-teacher')

    cur = mysql.connection.cursor()
    cur.execute("SELECT name,branch FROM teachers WHERE id=%s",
                (session['teacher'],))
    t = cur.fetchone()

    return render_template('teacher/pages/home.html',
                           name=t[0], branch=t[1])


@app.route('/teacher/approve')
def teacher_approve():
    if 'teacher' not in session:
        return redirect('/login-teacher')

    cur = mysql.connection.cursor()
    cur.execute("SELECT branch FROM teachers WHERE id=%s",
                (session['teacher'],))
    branch = cur.fetchone()[0]

    cur.execute("SELECT * FROM students WHERE approved=0 AND branch=%s",
                (branch,))
    students = cur.fetchall()

    return render_template('teacher/pages/approve.html',
                           students=students)


@app.route('/teacher/approve/<int:id>')
def approve_student(id):
    if 'teacher' not in session:
        return redirect('/login-teacher')

    cur = mysql.connection.cursor()
    cur.execute("UPDATE students SET approved=1 WHERE id=%s",(id,))
    mysql.connection.commit()
    return redirect('/teacher/approve')


@app.route('/teacher/notes', methods=['GET', 'POST'])
def teacher_notes():
    if 'teacher' not in session:
        return redirect('/login-teacher')

    # Ensure the upload directory exists before saving files.
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    cur = None

    try:
        cur = mysql.connection.cursor()

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            file = request.files.get('file')

            if not title:
                return "Please enter a note title.", 400

            if file is None or not file.filename:
                return "Please select a file to upload.", 400

            filename = secure_filename(file.filename)
            if not filename:
                return "Invalid filename.", 400

            # Save the uploaded file.
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            # Store the note details in the database.
            cur.execute(
                "INSERT INTO notes (teacher_id, title, file_path) "
                "VALUES (%s, %s, %s)",
                (session['teacher'], title, path)
            )
            mysql.connection.commit()

            # Redirect after POST to prevent duplicate uploads on refresh.
            return redirect(url_for('teacher_notes'))

        # Load notes belonging to the currently logged-in teacher.
        cur.execute(
            "SELECT * FROM notes WHERE teacher_id=%s ORDER BY id DESC",
            (session['teacher'],)
        )
        notes = cur.fetchall()

        return render_template('teacher/pages/notes.html', notes=notes)

    except Exception:
        # Undo a partially completed database transaction where possible.
        try:
            mysql.connection.rollback()
        except Exception:
            pass
        raise

    finally:
        if cur is not None:
            cur.close()


@app.route('/teacher/updates', methods=['GET','POST'])
def teacher_updates():
    if 'teacher' not in session:
        return redirect('/login-teacher')

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        msg = request.form['message']
        cur.execute("INSERT INTO notifications(message) VALUES(%s)", (msg,))
        mysql.connection.commit()

    cur.execute("SELECT * FROM notifications ORDER BY id DESC")
    updates = cur.fetchall()

    return render_template('teacher/pages/updates.html', updates=updates)

@app.route('/teacher/delete-update/<int:id>')
def delete_update(id):
    if 'teacher' not in session:
        return redirect('/login-teacher')

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM notifications WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect('/teacher/updates')

@app.route('/teacher/attendance', methods=['GET','POST'])
def teacher_attendance():
    if 'teacher' not in session:
        return redirect('/login-teacher')

    cur = mysql.connection.cursor()

    # Get teacher branch
    cur.execute("SELECT branch FROM teachers WHERE id=%s", (session['teacher'],))
    branch = cur.fetchone()[0]

    # Get students
    cur.execute(
        "SELECT id, name, regno FROM students WHERE approved=1 AND branch=%s",
        (branch,)
    )
    students = cur.fetchall()

    message = None

    if request.method == 'POST':
        # 🔹 Check if attendance already added today
        cur.execute(
            "SELECT COUNT(*) FROM attendance WHERE date = CURDATE()"
        )
        already = cur.fetchone()[0]

        if already > 0:
            message = "Attendance already uploaded for today"
        else:
            for s in students:
                status = request.form.get(f"status_{s[0]}")
                if status:
                    cur.execute(
                        "INSERT INTO attendance(student_id, date, status) VALUES(%s, CURDATE(), %s)",
                        (s[0], status)
                    )
            mysql.connection.commit()
            message = "Attendance uploaded successfully"

    return render_template(
        'teacher/pages/attendance.html',
        students=students,
        message=message
    )

# ---------------- STUDENT ----------------

@app.route('/login-student', methods=['GET','POST'])
def login_student():
    if request.method == 'POST':
        regno = request.form['regno']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT * FROM students WHERE regno=%s AND password=%s AND approved=1",
            (regno, password)
        )
        student = cur.fetchone()

        if student:
            # ✅ update last_login
            cur.execute(
                "UPDATE students SET last_login=%s WHERE id=%s",
                (datetime.now(), student[0])
            )
            mysql.connection.commit()

            session.clear()
            session['student'] = student[0]

            return redirect('/student/home')

        return render_template(
            'login_student.html',
            error="Invalid register number or password, or your account is not approved yet."
        )

    return render_template('login_student.html')

from flask import flash

@app.route('/register', methods=['GET','POST'])
def register_student():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        regno = request.form['regno']
        branch = request.form['branch']
        password = request.form['password']

        cur = mysql.connection.cursor()

        # Check if regno already exists
        cur.execute("SELECT * FROM students WHERE regno = %s", (regno,))
        existing = cur.fetchone()

        if existing:
            flash("Register number already exists. Please login.", "error")
            return redirect('/register')

        # Insert new student
        cur.execute(
            "INSERT INTO students (name, phone, regno, branch, password) VALUES (%s,%s,%s,%s,%s)",
            (name, phone, regno, branch, password)
        )
        mysql.connection.commit()

        flash("Registration successful. Please login.", "success")
        return redirect('/login-student')

    return render_template('register_student.html')


@app.route('/student/home')
def student_home():
    if 'student' not in session:
        return redirect('/login-student')

    cur = mysql.connection.cursor()

    # Fetch student details
    cur.execute(
        "SELECT name, branch, created_at FROM students WHERE id=%s",
        (session['student'],)
    )
    student = cur.fetchone()

    name, branch, last_login = student

    # 🔔 Check new notes after last login
    cur.execute("""
        SELECT COUNT(*) FROM notes
        WHERE created_at > %s
    """, (last_login,))
    new_notes = cur.fetchone()[0]

    # 🔔 Check new notifications after last login
    cur.execute("""
        SELECT COUNT(*) FROM notifications
        WHERE created_at > %s
    """, (last_login,))
    new_updates = cur.fetchone()[0]

    # ✅ Update last_login to now
    cur.execute(
        "UPDATE students SET created_at = NOW() WHERE id=%s",
        (session['student'],)
    )
    mysql.connection.commit()

    return render_template(
        'student/pages/home.html',
        name=name,
        branch=branch,
        new_notes=new_notes,
        new_updates=new_updates
    )

@app.route('/student/attendance')
def student_attendance():
    if 'student' not in session:
        return redirect('/login-student')

    student_id = session['student']
    cur = mysql.connection.cursor(DictCursor)

    # Total present
    cur.execute("""
        SELECT COUNT(*) AS present 
        FROM attendance 
        WHERE student_id=%s AND status='Present'
    """, (student_id,))
    present = cur.fetchone()['present']

    # Total days
    cur.execute("""
        SELECT COUNT(*) AS total 
        FROM attendance 
        WHERE student_id=%s
    """, (student_id,))
    total = cur.fetchone()['total']

    percent = round((present / total) * 100, 2) if total > 0 else 0

    # 🔹 Teacher-marked attendance records
    cur.execute("""
        SELECT date, status
        FROM attendance
        WHERE student_id=%s
        ORDER BY date DESC
    """, (student_id,))
    attendance = cur.fetchall()

    return render_template(
        'student/pages/attendance.html',
        present=present,
        total=total,
        percent=percent,
        attendance=attendance
    )

@app.route('/student/notes')
def student_notes():
    if 'student' not in session:
        return redirect('/login-student')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notes")
    notes = cur.fetchall()

    return render_template('student/pages/notes.html', notes=notes)

@app.route('/student/updates')
def student_updates():
    if 'student' not in session:
        return redirect('/login-student')

    cur = mysql.connection.cursor()
    cur.execute("SELECT message,created_at FROM notifications ORDER BY created_at DESC")
    updates = cur.fetchall()

    return render_template('student/pages/updates.html', updates=updates)

#------------------parent-----------------

@app.route('/register-parent', methods=['GET','POST'])
def register_parent():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        regno = request.form['regno']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO parents (name,email,regno,password) VALUES (%s,%s,%s,%s)",
            (name, email, regno, password)
        )
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login_parent'))

    return render_template('parent/register.html')


@app.route('/login-parent', methods=['GET', 'POST'])
def login_parent():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor(DictCursor)
        cur.execute(
            "SELECT * FROM parents WHERE email=%s AND password=%s",
            (email, password)
        )
        parent = cur.fetchone()
        cur.close()

        if parent:
            session.clear()
            session['parent'] = parent['id']   # ✅ store parent id
            return redirect('/parent/dashboard')

        # login failed
        return render_template(
            'login_parent.html',
            error="Invalid email or password"
        )

    return render_template('login_parent.html')



@app.route('/parent/dashboard')
def parent_dashboard():
    if 'parent' not in session:
        return redirect('/login-parent')

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("SELECT * FROM parents WHERE id=%s", (session['parent'],))
    parent = cur.fetchone()

    cur.execute("SELECT * FROM students WHERE regno=%s", (parent['regno'],))
    student = cur.fetchone()

    cur.execute("""
        SELECT COUNT(*) AS total,
               SUM(status='Present') AS present
        FROM attendance
        WHERE student_id=%s
    """, (student['id'],))
    a = cur.fetchone()

    percent = round((a['present']/a['total'])*100, 2) if a['total'] else 0

    return render_template(
        'parent/home.html',
        parent=parent,
        student=student,
        attendance_percent=percent
    )


@app.route('/parent/attendance')
def parent_attendance():
    if 'parent' not in session:
        return redirect('/login-parent')

    cur = mysql.connection.cursor(DictCursor)

    cur.execute("""
        SELECT a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN parents p ON s.regno = p.regno
        WHERE p.id=%s
        ORDER BY a.date DESC
    """, (session['parent'],))

    attendance = cur.fetchall()

    return render_template(
        'parent/attendance.html',
        attendance=attendance
    )


@app.route('/parent/updates')
def parent_updates():
    if 'parent' not in session:
        return redirect('/login-parent')

    cur = mysql.connection.cursor(DictCursor)
    cur.execute("SELECT * FROM notifications ORDER BY created_at DESC")
    updates = cur.fetchall()

    return render_template(
        'parent/updates.html',
        updates=updates
    )


# ---------------- LOGOUT ----------------

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/choose-login')

# ---------------- RUN ----------------

if __name__ == '__main__':
   app.run(debug=True)